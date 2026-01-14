#!/usr/bin/env python3
"""Smoke test for the official Showdown-backed Gym environment."""

import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ml.showdown_env import ShowdownPokemonBattleEnv


def main():
    parser = argparse.ArgumentParser(description="Smoke test: Showdown-backed Gym environment")
    parser.add_argument("--format", dest="formatid", default="gen9randombattle", help="Showdown format id")
    parser.add_argument("--p1-team", dest="team_p1", default=None, help="Team export path or packed team (p1)")
    parser.add_argument("--p2-team", dest="team_p2", default=None, help="Team export path or packed team (p2)")
    args = parser.parse_args()

    env = ShowdownPokemonBattleEnv(formatid=args.formatid, team_p1=args.team_p1, team_p2=args.team_p2)
    obs, info = env.reset(seed=123)
    print("reset:", obs.shape, info)

    total_reward = 0.0
    for t in range(10):
        # Take a random action from the discrete space
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        print(f"t={t} action={action} reward={reward:.3f} term={terminated} trunc={truncated}")
        if terminated or truncated:
            break

    print("total_reward:", total_reward)
    env.close()


if __name__ == "__main__":
    main()
