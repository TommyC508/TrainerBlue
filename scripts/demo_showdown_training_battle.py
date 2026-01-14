#!/usr/bin/env python3
"""Demo battle using the official Showdown-backed training environment.

Runs a single episode, choosing random *valid* actions (using action_mask), and
prints a lightweight turn-by-turn summary plus the final winner.
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np

from src.ml.showdown_env import ShowdownPokemonBattleEnv


def _team_hp_summary(env: ShowdownPokemonBattleEnv):
    s = env._state_p1  # intentionally using internal state for a debug/demo view
    our_team = s.our_side.team
    opp_team = s.opponent_side.team

    our_alive = sum(1 for p in our_team if p.hp > 0)
    opp_alive = sum(1 for p in opp_team if p.hp > 0)

    our_active = s.get_our_active_pokemon()
    opp_active = s.get_opponent_active_pokemon()

    return {
        "our_alive": our_alive,
        "opp_alive": opp_alive,
        "our_active": getattr(our_active, "species", None),
        "opp_active": getattr(opp_active, "species", None),
        "our_active_hp": getattr(our_active, "hp", None),
        "our_active_max_hp": getattr(our_active, "max_hp", None),
        "opp_active_hp": getattr(opp_active, "hp", None),
        "opp_active_max_hp": getattr(opp_active, "max_hp", None),
    }


def main():
    parser = argparse.ArgumentParser(description="Demo: Showdown-backed training environment")
    parser.add_argument("--format", dest="formatid", default="gen9randombattle", help="Showdown format id")
    parser.add_argument(
        "--p1-team",
        dest="team_p1",
        default=None,
        help="Path to a Showdown team export (or packed team string) for p1 (required for non-random formats)",
    )
    parser.add_argument(
        "--p2-team",
        dest="team_p2",
        default=None,
        help="Path to a Showdown team export (or packed team string) for p2 (required for non-random formats)",
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--max-turns", type=int, default=200, help="Max turns")
    parser.add_argument(
        "--save-protocol",
        type=str,
        default="",
        help="If set, writes the raw simulator protocol log to this path",
    )
    args = parser.parse_args()

    env = ShowdownPokemonBattleEnv(
        formatid=args.formatid,
        team_p1=args.team_p1,
        team_p2=args.team_p2,
        max_turns=args.max_turns,
        record_protocol=bool(args.save_protocol),
    )
    obs, info = env.reset(seed=args.seed)

    print("=== Showdown-backed env demo ===")
    print("obs shape:", obs.shape)
    print("initial info:", info)

    total_reward = 0.0

    for t in range(args.max_turns):
        mask = env.get_action_mask()
        valid_actions = np.flatnonzero(mask)
        action = int(np.random.choice(valid_actions))

        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += float(reward)

        summary = _team_hp_summary(env)
        print(
            f"turn={t:03d} action={action} reward={reward:+.3f} "
            f"alive(p1/p2)={summary['our_alive']}/{summary['opp_alive']} "
            f"active={summary['our_active']}({summary['our_active_hp']}/{summary['our_active_max_hp']}) vs "
            f"{summary['opp_active']}({summary['opp_active_hp']}/{summary['opp_active_max_hp']})"
        )

        if terminated or truncated:
            break

    print("=== Result ===")
    print("winner:", info.get("winner"))
    print("turns:", info.get("turn"))
    print("total_reward:", total_reward)

    if args.save_protocol:
        os.makedirs(os.path.dirname(args.save_protocol) or ".", exist_ok=True)
        with open(args.save_protocol, "w", encoding="utf-8") as f:
            f.write(env.get_protocol_log())
        print("protocol log saved to:", args.save_protocol)

    env.close()


if __name__ == "__main__":
    main()
