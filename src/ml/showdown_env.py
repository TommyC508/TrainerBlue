"""Gymnasium environment backed by the official Pokémon Showdown simulator.

This environment launches `external/pokemon-showdown/pokemon-showdown simulate-battle`
(as a subprocess) and plays both sides:
- p1 is controlled by the learning agent (this env)
- p2 is controlled by a simple opponent policy (currently random)

Observation shape matches `src/ml/environment.py` (202) so existing training code can
switch backends without changing model architecture.
"""

from __future__ import annotations

import os
import random
from typing import Any, Dict, Optional, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from ..battle.state import BattleState
from ..battle.showdown_process import ShowdownSimulatorProcess, ShowdownBlock, pack_team
from ..data.type_effectiveness import get_type_effectiveness


class ShowdownPokemonBattleEnv(gym.Env):
    metadata = {"render_modes": ["human", "ansi"], "render_fps": 1}

    def __init__(
        self,
        formatid: str = "gen9randombattle",
        team_p1: Optional[str] = None,
        team_p2: Optional[str] = None,
        max_turns: int = 200,
        max_timeouts_startup: int = 10,
        max_timeouts_step: int = 10,
        render_mode: Optional[str] = None,
        showdown_dir: Optional[str] = None,
        timeout_s: float = 2.0,
        record_protocol: bool = False,
    ):
        super().__init__()

        self.formatid = formatid
        self._team_p1_raw = team_p1
        self._team_p2_raw = team_p2
        self.max_turns = max_turns
        self.max_timeouts_startup = max_timeouts_startup
        self.max_timeouts_step = max_timeouts_step
        self.render_mode = render_mode

        # Match the existing Phase 4 env architecture
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(202,), dtype=np.float32)
        self.action_space = spaces.Discrete(9)

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.showdown_dir = showdown_dir or os.path.join(root, "external", "pokemon-showdown")

        self._team_p1_packed = self._maybe_pack_team(self._team_p1_raw)
        self._team_p2_packed = self._maybe_pack_team(self._team_p2_raw)

        self._proc = ShowdownSimulatorProcess(self.showdown_dir, timeout_s=timeout_s)

        self.record_protocol = record_protocol
        self._protocol_log: list[str] = []

        # Separate BattleState per player so request JSON doesn't overwrite
        self._state_p1 = BattleState(our_player_id="p1")
        self._state_p2 = BattleState(our_player_id="p2")

        self._turn = 0
        self._prev_our_hp = 600.0
        self._prev_opp_hp = 600.0

        # Per-step dynamic mapping: action index -> showdown choice string
        self._p1_action_choice: Dict[int, str] = {}
        self._p2_action_choice: Dict[int, str] = {}

    def _maybe_pack_team(self, team: Optional[str]) -> Optional[str]:
        if not team:
            return None
        team_text = team
        if os.path.exists(team):
            with open(team, "r", encoding="utf-8") as f:
                team_text = f.read()
        return pack_team(self.showdown_dir, team_text)

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)

        self._turn = 0
        self._state_p1 = BattleState(our_player_id="p1")
        self._state_p2 = BattleState(our_player_id="p2")

        # Restart subprocess per episode for clean state.
        self._proc.close()
        self._proc.start()

        if self.record_protocol:
            self._protocol_log = []

        self._proc.write_lines(
            self._initial_protocol_lines()
        )

        # Consume output until we have initial requests (or battle begins).
        self._drain_until_requests_or_end(min_reads=5, max_timeouts=self.max_timeouts_startup)

        # Initialize reward baselines
        self._prev_our_hp = self._sum_hp(self._state_p1.our_side.team)
        self._prev_opp_hp = self._sum_hp(self._state_p2.our_side.team)

        obs = self._get_observation()
        info = self._get_info()
        return obs, info

    def _initial_protocol_lines(self) -> list[str]:
        is_random_format = "random" in self.formatid
        if not is_random_format and (not self._team_p1_packed or not self._team_p2_packed):
            raise ValueError(
                "Non-random formats (e.g. gen9ou) require explicit teams for both players. "
                "Provide team_p1/team_p2 (packed team string or path to an export file)."
            )

        lines = [f'>start {{"formatid":"{self.formatid}"}}']

        if self._team_p1_packed:
            lines.append(f'>player p1 {{"name":"p1","team":"{self._team_p1_packed}"}}')
        else:
            lines.append('>player p1 {"name":"p1"}')

        if self._team_p2_packed:
            lines.append(f'>player p2 {{"name":"p2","team":"{self._team_p2_packed}"}}')
        else:
            lines.append('>player p2 {"name":"p2"}')

        return lines

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._turn >= self.max_turns:
            return self._get_observation(), 0.0, False, True, self._get_info()

        # Ensure mappings based on most recent requests
        self._refresh_action_maps()

        p1_choice = self._choice_for_action(action, self._p1_action_choice)
        p2_choice = self._choose_opponent_action()

        self._proc.write_lines([f">p1 {p1_choice}", f">p2 {p2_choice}"])

        ended = self._drain_until_requests_or_end(min_reads=1, max_timeouts=self.max_timeouts_step)

        our_hp = self._sum_hp(self._state_p1.our_side.team)
        opp_hp = self._sum_hp(self._state_p2.our_side.team)

        # Reward: damage differential + terminal bonus
        dmg_to_opp = max(0.0, self._prev_opp_hp - opp_hp)
        dmg_to_us = max(0.0, self._prev_our_hp - our_hp)
        reward = (dmg_to_opp - dmg_to_us) / 100.0
        reward -= 0.01

        terminated = ended or self._state_p1.finished or self._state_p2.finished
        truncated = False

        if terminated:
            winner = self._state_p1.winner
            if winner == "p1":
                reward += 1.0
            elif winner == "p2":
                reward -= 1.0

        self._prev_our_hp = our_hp
        self._prev_opp_hp = opp_hp

        self._turn += 1

        return self._get_observation(), reward, terminated, truncated, self._get_info()

    def get_action_mask(self) -> np.ndarray:
        """Boolean mask for actions 0..8 based on the current p1 request."""
        self._refresh_action_maps()
        mask = np.zeros(9, dtype=bool)
        for idx in self._p1_action_choice.keys():
            if 0 <= idx < 9:
                mask[idx] = True
        if not mask.any():
            mask[0] = True
        return mask

    def close(self):
        self._proc.close()

    def get_protocol_log(self) -> str:
        """Return the accumulated raw simulator protocol as a single string."""
        return "\n".join(self._protocol_log)

    # -----------------
    # Output processing
    # -----------------

    def _drain_until_requests_or_end(self, min_reads: int = 1, max_timeouts: int = 5) -> bool:
        """Read blocks until we have current requests for p1 and p2, or battle ends.

        The simulator may take a moment to emit the first `sideupdate` request.
        We allow a few timeouts to avoid treating that as a failure.
        """
        seen_p1_req = self._state_p1.current_request is not None
        seen_p2_req = self._state_p2.current_request is not None

        reads = 0
        consecutive_timeouts = 0

        while True:
            block = self._proc.read_block()
            if block is None:
                # If the simulator exited, surface stderr to avoid silent hangs.
                if self._proc.poll() is not None:
                    stderr_tail = self._proc.get_stderr_tail(max_lines=80)
                    extra = f"\n--- simulator stderr (tail) ---\n{stderr_tail}" if stderr_tail else ""
                    raise RuntimeError(
                        f"Showdown simulator process exited with code {self._proc.poll()} while waiting for output.{extra}"
                    )
                consecutive_timeouts += 1
                if consecutive_timeouts >= max_timeouts:
                    break
                continue

            reads += 1
            consecutive_timeouts = 0

            self._apply_block(block)

            if self._state_p1.finished or self._state_p2.finished:
                return True

            # Requests are delivered via sideupdate blocks
            if self._state_p1.current_request is not None:
                seen_p1_req = True
            if self._state_p2.current_request is not None:
                seen_p2_req = True

            # Some formats have team preview / forceSwitch; allow proceeding with only p1
            if seen_p1_req and seen_p2_req:
                return False

        if (not self._state_p1.finished and not self._state_p2.finished) and (
            self._state_p1.current_request is None and self._state_p2.current_request is None
        ):
            raise TimeoutError(
                f"Timed out waiting for simulator output/requests (format={self.formatid}). "
                "This usually means simulate-battle produced no output or got stuck."
            )

        return self._state_p1.finished or self._state_p2.finished

    def _apply_block(self, block: ShowdownBlock) -> None:
        if self.record_protocol:
            if block.block_type == "sideupdate":
                self._protocol_log.append("sideupdate")
                self._protocol_log.append(str(block.player_id or ""))
                self._protocol_log.extend(block.lines)
                self._protocol_log.append("")
            else:
                self._protocol_log.append(str(block.block_type))
                self._protocol_log.extend(block.lines)
                self._protocol_log.append("")

        if block.block_type == "update":
            for line in block.lines:
                if line.startswith("|"):
                    self._state_p1.update(line)
                    self._state_p2.update(line)

        elif block.block_type == "sideupdate":
            target = self._state_p1 if block.player_id == "p1" else self._state_p2
            for line in block.lines:
                if line.startswith("|"):
                    target.update(line)

        elif block.block_type == "end":
            # end block includes JSON; winner is already set via |win| line in updates
            return

        else:
            # Unknown block type; ignore
            return

    # -----------------
    # Action mapping
    # -----------------

    def _refresh_action_maps(self) -> None:
        self._p1_action_choice = self._build_action_map(self._state_p1)
        self._p2_action_choice = self._build_action_map(self._state_p2)

    def _build_action_map(self, state: BattleState) -> Dict[int, str]:
        """Map discrete action indices -> Showdown choice strings for the current request."""
        mapping: Dict[int, str] = {}

        req = state.current_request
        if not req:
            # If no request, default is safest
            return {0: "default"}

        # Team preview / forced switch
        if req.get("teamPreview") or req.get("forceSwitch") or req.get("wait"):
            return {0: "default"}

        active_list = req.get("active")
        if isinstance(active_list, list) and active_list:
            active0 = active_list[0]
            moves = active0.get("moves", []) if isinstance(active0, dict) else []

            for slot in range(1, 5):
                idx = slot - 1
                if idx < len(moves) and not moves[idx].get("disabled", False):
                    mapping[idx] = f"move {slot}"

        # Switches (map up to 5 legal switch slots to actions 4..8)
        side = req.get("side", {}) if isinstance(req.get("side"), dict) else {}
        pokemon_list = side.get("pokemon", []) if isinstance(side.get("pokemon"), list) else []

        switch_slots: list[int] = []
        for i, poke in enumerate(pokemon_list, start=1):
            if not isinstance(poke, dict):
                continue
            if poke.get("active"):
                continue
            condition = str(poke.get("condition", ""))
            if condition.startswith("0"):
                continue
            switch_slots.append(i)

        for k, slot in enumerate(switch_slots[:5]):
            mapping[4 + k] = f"switch {slot}"

        if not mapping:
            mapping[0] = "default"

        return mapping

    def _choice_for_action(self, action: int, mapping: Dict[int, str]) -> str:
        if action in mapping:
            return mapping[action]
        # Fall back to first valid choice in mapping
        return next(iter(mapping.values()))

    def _choose_opponent_action(self) -> str:
        if not self._p2_action_choice:
            return "default"
        return random.choice(list(self._p2_action_choice.values()))

    # -----------------
    # Observation / info
    # -----------------

    def _get_observation(self) -> np.ndarray:
        # Reuse the same encoding scheme as src/ml/environment.py
        features: list[float] = []

        features.extend(self._encode_team(self._state_p1.our_side.team, opp_active=self._state_p1.get_opponent_active_pokemon()))
        features.extend(self._encode_team(self._state_p1.opponent_side.team, opp_active=self._state_p1.get_our_active_pokemon()))
        features.extend(self._encode_field())

        arr = np.array(features, dtype=np.float32)
        # Clip into [-1, 1] for safety (some stats could be missing/odd)
        return np.clip(arr, -1.0, 1.0)

    def _encode_team(self, team, opp_active) -> list[float]:
        features: list[float] = []
        for i in range(6):
            if i < len(team):
                p = team[i]

                # HP%
                features.append(p.hp_percent / 100.0)

                # Stats (same normalization as Phase4 env)
                for stat in ["atk", "def", "spa", "spd", "spe"]:
                    features.append(p.stats.get(stat, 100) / 150.0)
                features.append(0.0)

                # Type matchup effectiveness features
                if opp_active and p.types:
                    eff1 = get_type_effectiveness(p.types[0], opp_active.types) if p.types else 1.0
                    features.append(eff1 - 1.0)
                    if len(p.types) > 1:
                        eff2 = get_type_effectiveness(p.types[1], opp_active.types)
                        features.append(eff2 - 1.0)
                    else:
                        features.append(0.0)
                else:
                    features.extend([0.0, 0.0])

                status_map = {"": 0.0, "par": 0.25, "brn": 0.5, "psn": 0.75, "slp": 1.0, "frz": 1.0}
                features.append(status_map.get(p.status, 0.0))

                for stat in ["atk", "def", "spa", "spd", "spe", "accuracy"]:
                    features.append(p.boosts.get(stat, 0) / 6.0)
            else:
                features.extend([0.0] * 16)
        return features

    def _encode_field(self) -> list[float]:
        features: list[float] = []

        weather_map = {"": 0.0, "sunnyday": 0.33, "raindance": 0.67, "sandstorm": 1.0}
        terrain_map = {"": 0.0, "electricterrain": 0.33, "grassyterrain": 0.67, "mistyterrain": 1.0}

        features.append(weather_map.get(self._state_p1.field.weather, 0.0))
        features.append(terrain_map.get(self._state_p1.field.terrain, 0.0))
        features.append(1.0 if self._state_p1.field.trick_room else 0.0)
        features.append(float(self._turn) / float(self.max_turns))
        features.extend([0.0] * 6)

        return features

    def _get_info(self) -> Dict[str, Any]:
        return {
            "turn": self._turn,
            "formatid": self.formatid,
            "winner": self._state_p1.winner,
            "p1_has_request": self._state_p1.current_request is not None,
            "p2_has_request": self._state_p2.current_request is not None,
            "action_mask": self.get_action_mask(),
        }

    @staticmethod
    def _sum_hp(team) -> float:
        # Sum current HP (not percent) for reward tracking
        total = 0.0
        for p in team:
            total += float(getattr(p, "hp", 0))
        return total
