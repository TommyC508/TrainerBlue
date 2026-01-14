"""Run the official Pokémon Showdown simulator as a subprocess.

This wraps `external/pokemon-showdown/pokemon-showdown simulate-battle` and
provides a small API to:
- start/reset a battle
- send choices
- read protocol output blocks (update/sideupdate/end)

The simulator protocol is documented in `external/pokemon-showdown/sim/SIMULATOR.md`.
"""

from __future__ import annotations

import os
import subprocess
import selectors
from dataclasses import dataclass
from typing import Iterable, Optional


def pack_team(showdown_dir: str, team_text: str) -> str:
    """Convert a team (exported/JSON/packed) into packed team format.

    Uses `pokemon-showdown pack-team`, which reads from stdin and writes the packed
    team to stdout.
    """
    exe = os.path.join(showdown_dir, "pokemon-showdown")
    if not os.path.exists(exe):
        raise FileNotFoundError(
            f"Pokemon Showdown executable not found: {exe}. "
            "Run scripts/setup_showdown.sh first."
        )

    team_text = team_text if team_text.endswith("\n") else (team_text + "\n")
    result = subprocess.run(
        [exe, "pack-team"],
        cwd=showdown_dir,
        input=team_text,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        raise ValueError(f"Failed to pack team (exit {result.returncode}): {stderr}")

    return (result.stdout or "").strip()


@dataclass(frozen=True)
class ShowdownBlock:
    """One output block from the simulator."""

    block_type: str  # 'update' | 'sideupdate' | 'end' | ...
    player_id: Optional[str]  # for sideupdate: 'p1'/'p2'; else None
    lines: list[str]  # protocol lines (usually starting with '|')


class ShowdownSimulatorProcess:
    """Manages a single `simulate-battle` subprocess."""

    def __init__(
        self,
        showdown_dir: str,
        timeout_s: float = 4.0,
        env: Optional[dict[str, str]] = None,
    ):
        self.showdown_dir = showdown_dir
        self.timeout_s = timeout_s
        self.env = env
        self._proc: Optional[subprocess.Popen[str]] = None
        self._sel: Optional[selectors.BaseSelector] = None
        self._pending_lines: list[str] = []
        self._stderr_cache: list[str] = []

    def start(self) -> None:
        if self._proc:
            return

        exe = os.path.join(self.showdown_dir, "pokemon-showdown")
        if not os.path.exists(exe):
            raise FileNotFoundError(
                f"Pokemon Showdown executable not found: {exe}. "
                "Run scripts/setup_showdown.sh first."
            )

        merged_env = os.environ.copy()
        if self.env:
            merged_env.update(self.env)

        self._proc = subprocess.Popen(
            [exe, "simulate-battle"],
            cwd=self.showdown_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self._proc.stdout and self._proc.stdin

        self._pending_lines = []
        self._stderr_cache = []

        self._sel = selectors.DefaultSelector()
        self._sel.register(self._proc.stdout, selectors.EVENT_READ)
        if self._proc.stderr:
            self._sel.register(self._proc.stderr, selectors.EVENT_READ)

    def close(self) -> None:
        if not self._proc:
            return
        try:
            if self._proc.stdin:
                try:
                    self._proc.stdin.close()
                except Exception:
                    pass
            self._proc.terminate()
            try:
                self._proc.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        finally:
            if self._sel and self._proc.stdout:
                try:
                    self._sel.unregister(self._proc.stdout)
                except Exception:
                    pass
            if self._sel and self._proc and self._proc.stderr:
                try:
                    self._sel.unregister(self._proc.stderr)
                except Exception:
                    pass
            self._sel = None
            self._proc = None
            self._pending_lines = []

    def write_lines(self, lines: Iterable[str]) -> None:
        if not self._proc or not self._proc.stdin:
            raise RuntimeError("Showdown simulator process not started")
        for line in lines:
            if not line.endswith("\n"):
                line += "\n"
            self._proc.stdin.write(line)
        self._proc.stdin.flush()

    def read_block(self) -> Optional[ShowdownBlock]:
        """Read the next output block.

        Blocks are separated by a blank line. Returns None on timeout.
        """
        if not self._proc or not self._proc.stdout or not self._sel:
            raise RuntimeError("Showdown simulator process not started")

        # We must never call readline() unless the pipe is readable; otherwise we
        # can deadlock forever if the simulator pauses mid-block.
        while True:
            events = self._sel.select(timeout=self.timeout_s)
            if not events:
                return None

            # Drain any available stderr lines for debugging.
            if self._proc.stderr:
                for key, _mask in events:
                    if key.fileobj is self._proc.stderr:
                        err_line = self._proc.stderr.readline()
                        if err_line:
                            self._stderr_cache.append(err_line.rstrip("\n"))

            # Only proceed if stdout is readable.
            if any(key.fileobj is self._proc.stdout for key, _mask in events):
                break

        # Read at least one stdout line now that it's readable.
        line = self._proc.stdout.readline()
        if line == "":
            return None
        line = line.rstrip("\n")
        if line != "":
            self._pending_lines.append(line)

        # Continue reading until blank line terminator, but always gate reads via select.
        while True:
            events = self._sel.select(timeout=self.timeout_s)
            if not events:
                # Block not finished yet; caller can retry.
                return None

            if self._proc.stderr:
                for key, _mask in events:
                    if key.fileobj is self._proc.stderr:
                        err_line = self._proc.stderr.readline()
                        if err_line:
                            self._stderr_cache.append(err_line.rstrip("\n"))

            if not any(key.fileobj is self._proc.stdout for key, _mask in events):
                continue

            line = self._proc.stdout.readline()
            if line == "":
                # EOF mid-block
                break

            line = line.rstrip("\n")
            if line == "":
                # End of block
                break

            self._pending_lines.append(line)

        if not self._pending_lines:
            return None

        buf = self._pending_lines
        self._pending_lines = []

        block_type = buf[0].strip()
        if block_type == "sideupdate":
            player_id = buf[1].strip() if len(buf) > 1 else None
            lines = [l for l in buf[2:] if l]
            return ShowdownBlock(block_type=block_type, player_id=player_id, lines=lines)

        # update/end/etc
        return ShowdownBlock(block_type=block_type, player_id=None, lines=[l for l in buf[1:] if l])

    def get_stderr_tail(self, max_lines: int = 50) -> str:
        """Best-effort stderr tail for debugging simulator failures."""
        if not self._stderr_cache:
            return ""
        tail = self._stderr_cache[-max_lines:]
        return "\n".join(tail)

    def poll(self) -> Optional[int]:
        return None if not self._proc else self._proc.poll()
