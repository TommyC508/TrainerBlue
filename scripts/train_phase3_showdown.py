#!/usr/bin/env python3
"""Phase 3 re-training script using the official Pokemon Showdown environment."""
import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback

from src.ml.showdown_env import ShowdownPokemonBattleEnv


def make_env(
    rank: int = 0,
    seed: int = 0,
    formatid: str = "gen9randombattle",
    team_p1: str | None = None,
    team_p2: str | None = None,
    timeout_s: float = 1.0,
    max_timeouts_startup: int = 100,
):
    """Factory for a single Showdown environment instance."""

    def _init():
        env = ShowdownPokemonBattleEnv(
            formatid=formatid,
            team_p1=team_p1,
            team_p2=team_p2,
            timeout_s=timeout_s,
            max_timeouts_startup=max_timeouts_startup,
        )
        env.reset(seed=seed + rank)
        return env

    return _init


def train(
    timesteps: int = 100_000,
    n_envs: int = 1,
    save_path: str = "models/ppo_phase3_showdown_new",
    log_dir: str = "logs/phase3_showdown_new",
    checkpoint_freq: int = 50_000,
    eval_freq: int = 25_000,
    rollout_steps: int = 2048,
    formatid: str = "gen9randombattle",
    team_p1: str | None = None,
    team_p2: str | None = None,
    timeout_s: float = 1.0,
    max_timeouts_startup: int = 100,
):
    print("=" * 70)
    print("Phase 3 Re-Training - Showdown")
    print("=" * 70)
    print()
    print("Configuration:")
    print(f"  Total timesteps: {timesteps:,}")
    print(f"  Parallel environments: {n_envs}")
    print(f"  Save path: {save_path}")
    print(f"  Log directory: {log_dir}")
    print(f"  Checkpoint frequency: {checkpoint_freq:,}")
    print(f"  Evaluation frequency: {eval_freq:,}")
    print(f"  Timeout: {timeout_s}")
    print(f"  Startup timeouts: {max_timeouts_startup}")
    print(f"  Format: {formatid}")
    if team_p1 or team_p2:
        print("  Teams: custom")
    print()

    os.makedirs(save_path, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    env_fns = [
        make_env(i, formatid=formatid, team_p1=team_p1, team_p2=team_p2, timeout_s=timeout_s, max_timeouts_startup=max_timeouts_startup)
        for i in range(n_envs)
    ]
    env = DummyVecEnv(env_fns)

    print("✅ Environments created")
    print()

    eval_env = DummyVecEnv([
        make_env(10_000, formatid=formatid, team_p1=team_p1, team_p2=team_p2, timeout_s=timeout_s, max_timeouts_startup=max_timeouts_startup)
    ])
    print("✅ Evaluation environment created")
    print()

    checkpoint_callback = CheckpointCallback(
        save_freq=max(1, checkpoint_freq // max(1, n_envs)),
        save_path=save_path,
        name_prefix="checkpoint",
        save_replay_buffer=False,
        save_vecnormalize=False,
    )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_path,
        log_path=log_dir,
        eval_freq=max(1, eval_freq // max(1, n_envs)),
        n_eval_episodes=5,
        deterministic=True,
        render=False,
    )

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        tensorboard_log=log_dir,
        learning_rate=3e-4,
        n_steps=rollout_steps,
        batch_size=256,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        device="auto",
    )
    print("✅ Model created")
    print()

    print("=" * 70)
    print("Starting training...")
    print("=" * 70)
    print()
    print("Monitor progress with TensorBoard:")
    print(f"  tensorboard --logdir {log_dir}")
    print()

    start_time = datetime.now()
    try:
        model.learn(
            total_timesteps=timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=False,
        )
        duration = datetime.now() - start_time
        final_model_path = os.path.join(save_path, "final_model")
        model.save(final_model_path)
        print()
        print("✅ Training completed")
        print(f"Duration: {duration}")
        print(f"Final model saved to: {final_model_path}")
    except KeyboardInterrupt:
        interrupted_path = os.path.join(save_path, "interrupted_model")
        model.save(interrupted_path)
        print("Training interrupted; model saved to", interrupted_path)
    finally:
        env.close()
        eval_env.close()


def main():
    parser = argparse.ArgumentParser(description="Phase 3 re-training with Showdown backend")
    parser.add_argument("--timesteps", type=int, default=100000)
    parser.add_argument("--n-envs", type=int, default=1)
    parser.add_argument("--save-path", type=str, default="models/ppo_phase3_showdown_new")
    parser.add_argument("--log-dir", type=str, default="logs/phase3_showdown_new")
    parser.add_argument("--checkpoint-freq", type=int, default=50000)
    parser.add_argument("--eval-freq", type=int, default=25000)
    parser.add_argument("--rollout-steps", type=int, default=2048)
    parser.add_argument("--format", dest="formatid", type=str, default="gen9randombattle")
    parser.add_argument("--p1-team", dest="team_p1", type=str, default=None)
    parser.add_argument("--p2-team", dest="team_p2", type=str, default=None)
    parser.add_argument("--sim-timeout", dest="timeout_s", type=float, default=1.0)
    parser.add_argument("--sim-startup-timeouts", dest="max_timeouts_startup", type=int, default=100)
    args = parser.parse_args()

    train(
        timesteps=args.timesteps,
        n_envs=args.n_envs,
        save_path=args.save_path,
        log_dir=args.log_dir,
        checkpoint_freq=args.checkpoint_freq,
        eval_freq=args.eval_freq,
        rollout_steps=args.rollout_steps,
        formatid=args.formatid,
        team_p1=args.team_p1,
        team_p2=args.team_p2,
        timeout_s=args.timeout_s,
        max_timeouts_startup=args.max_timeouts_startup,
    )


if __name__ == "__main__":
    main()
