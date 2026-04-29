#!/usr/bin/env python3
"""
Phase 4 Training Script - Server Edition
Train RL agent with fixed reward function to incentivize KO wins.

Usage:
    python train_phase4_server.py --timesteps 1000000 --n-envs 16

Run on server and let it train overnight/over days.
"""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor

from src.ml.environment import PokemonBattleEnv
from src.agents.random_agent import RandomAgent
from src.agents.heuristic_agent import HeuristicAgent


def make_env(rank=0, seed=0, opponent="random"):
    """Create a Pokemon battle environment."""
    def _init():
        if opponent == "heuristic":
            env = PokemonBattleEnv(opponent_agent=HeuristicAgent(), max_turns=50)
        else:
            env = PokemonBattleEnv(opponent_agent=RandomAgent(), max_turns=50)
        env = Monitor(env)
        env.reset(seed=seed + rank)
        return env
    return _init


def train_phase4(
    algorithm="PPO",
    timesteps=1000000,
    n_envs=16,
    save_path="models/ppo_phase4_fixed_reward",
    log_dir="logs/phase4_fixed_reward",
    checkpoint_freq=100000,
    eval_freq=50000,
    resume=None,
    opponent="random",
):
    """Train Phase 4 model with fixed reward function."""
    
    print("=" * 80)
    print("Phase 4 Training - Fixed Reward Function (KO-focused)")
    print("=" * 80)
    print()
    print("Configuration:")
    print(f"  Algorithm: {algorithm}")
    print(f"  Total timesteps: {timesteps:,}")
    print(f"  Parallel environments: {n_envs}")
    print(f"  Environment max_turns: 50 (down from 100)")
    print(f"  Opponent: {opponent}")
    print(f"  Save path: {save_path}")
    print(f"  Log directory: {log_dir}")
    print(f"  Checkpoint frequency: {checkpoint_freq:,}")
    print(f"  Evaluation frequency: {eval_freq:,}")
    if resume:
        print(f"  Resuming from: {resume}")
    print()
    
    # Create directories
    os.makedirs(save_path, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    # Create vectorized environment
    print(f"Creating {n_envs} parallel environments...")
    
    env_fns = [make_env(i, opponent=opponent) for i in range(n_envs)]
    
    if n_envs == 1:
        env = DummyVecEnv(env_fns)
    elif n_envs <= 4:
        env = DummyVecEnv(env_fns)
    else:
        # Use SubprocVecEnv for better performance with many envs
        try:
            env = SubprocVecEnv(env_fns, start_method="spawn")
        except Exception as e:
            print(f"Warning: SubprocVecEnv failed ({e}), falling back to DummyVecEnv")
            env = DummyVecEnv(env_fns)
    
    print("✅ Training environments created")
    print()
    
    # Create evaluation environment(s)
    print("Creating evaluation environment...")
    eval_env_fns = [make_env(1000 + i, opponent=opponent) for i in range(2)]
    eval_env = DummyVecEnv(eval_env_fns)
    print("✅ Evaluation environment created")
    print()
    
    # Create callbacks
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
        n_eval_episodes=20,
        deterministic=True,
        render=False,
    )
    
    # Create or load model
    if resume:
        resume_path = Path(resume)
        if not resume_path.with_suffix('.zip').exists():
            print(f"❌ Model not found: {resume}")
            return False
            
        print(f"Loading model from {resume}...")
        if algorithm == "PPO":
            model = PPO.load(resume, env=env, tensorboard_log=log_dir)
        elif algorithm == "A2C":
            model = A2C.load(resume, env=env, tensorboard_log=log_dir)
        elif algorithm == "DQN":
            model = DQN.load(resume, env=env, tensorboard_log=log_dir)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        print("✅ Model loaded")
    else:
        print(f"Creating new {algorithm} model...")
        
        model_params = {
            "policy": "MlpPolicy",
            "env": env,
            "verbose": 1,
            "tensorboard_log": log_dir,
            "device": "auto"
        }
        
        if algorithm == "PPO":
            model = PPO(
                **model_params,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=256,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01,
                vf_coef=0.5,
                max_grad_norm=0.5,
            )
        elif algorithm == "A2C":
            model = A2C(
                **model_params,
                learning_rate=7e-4,
                n_steps=5,
                gamma=0.99,
                gae_lambda=1.0,
                ent_coef=0.01,
                vf_coef=0.5,
                max_grad_norm=0.5,
            )
        elif algorithm == "DQN":
            model = DQN(
                **model_params,
                learning_rate=1e-4,
                buffer_size=100000,
                learning_starts=10000,
                batch_size=128,
                gamma=0.99,
                train_freq=4,
                gradient_steps=1,
                target_update_interval=1000,
                exploration_fraction=0.1,
                exploration_final_eps=0.05,
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        print("✅ Model created")
    
    print()
    print("=" * 80)
    print("Starting training...")
    print("=" * 80)
    print()
    print("Monitor progress with TensorBoard:")
    print(f"  tensorboard --logdir {log_dir}")
    print()
    
    start_time = datetime.now()
    
    try:
        # Train the model
        model.learn(
            total_timesteps=timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=False,
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("=" * 80)
        print("✅ Training completed successfully!")
        print("=" * 80)
        print(f"Duration: {duration}")
        print()
        
        # Save final model
        final_model_path = os.path.join(save_path, "final_model")
        model.save(final_model_path)
        print(f"Final model saved to: {final_model_path}")
        print()
        
        # Save metadata
        import json
        metadata = {
            "algorithm": algorithm,
            "timesteps": timesteps,
            "n_envs": n_envs,
            "duration_seconds": duration.total_seconds(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "changes": [
                "Reward function: KO bonus increased from 5 to 50",
                "Turn limit: reduced from 100 to 50 turns",
                "Turn limit penalty: -25 reward for timeouts",
                "HP advantage weight: reduced from 0.5 to 0.2",
            ]
        }
        metadata_path = os.path.join(save_path, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to: {metadata_path}")
        print()
        
        print("Next steps:")
        print(f"  1. Evaluate: PYTHONPATH=. python scripts/evaluate_rl.py --model {final_model_path} --episodes 50")
        print(f"  2. View logs: tensorboard --logdir {log_dir}")
        print()
        
        return True
        
    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print("Training interrupted by user")
        print("=" * 80)
        
        # Save interrupted model
        interrupted_path = os.path.join(save_path, "interrupted_model")
        model.save(interrupted_path)
        print(f"Model saved to: {interrupted_path}")
        print()
        
        return False
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Training failed with error: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        env.close()
        eval_env.close()


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4 Training - Fixed Reward Function",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test (100k timesteps, 4 envs)
  python train_phase4_server.py --timesteps 100000 --n-envs 4

  # Full training (1M timesteps, 16 envs)
  python train_phase4_server.py --timesteps 1000000 --n-envs 16

  # Resume from Phase 3 checkpoint
  python train_phase4_server.py --resume models/ppo_phase3_showdown_new/best_model --timesteps 500000

  # Training against heuristic opponent
  python train_phase4_server.py --opponent heuristic --timesteps 1000000 --n-envs 8
        """
    )
    
    parser.add_argument(
        "--algorithm",
        type=str,
        default="PPO",
        choices=["PPO", "A2C", "DQN"],
        help="RL algorithm to use (default: PPO)"
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=1000000,
        help="Total training timesteps (default: 1000000)"
    )
    parser.add_argument(
        "--n-envs",
        type=int,
        default=16,
        help="Number of parallel environments (default: 16)"
    )
    parser.add_argument(
        "--save-path",
        type=str,
        default="models/ppo_phase4_fixed_reward",
        help="Path to save the model"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs/phase4_fixed_reward",
        help="Path for TensorBoard logs"
    )
    parser.add_argument(
        "--checkpoint-freq",
        type=int,
        default=100000,
        help="Checkpoint save frequency in timesteps (default: 100000)"
    )
    parser.add_argument(
        "--eval-freq",
        type=int,
        default=50000,
        help="Evaluation frequency in timesteps (default: 50000)"
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to model to resume training from (without .zip)"
    )
    parser.add_argument(
        "--opponent",
        type=str,
        default="random",
        choices=["random", "heuristic"],
        help="Opponent type for training (default: random)"
    )
    
    args = parser.parse_args()
    
    success = train_phase4(
        algorithm=args.algorithm,
        timesteps=args.timesteps,
        n_envs=args.n_envs,
        save_path=args.save_path,
        log_dir=args.log_dir,
        checkpoint_freq=args.checkpoint_freq,
        eval_freq=args.eval_freq,
        resume=args.resume,
        opponent=args.opponent,
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
