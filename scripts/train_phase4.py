#!/usr/bin/env python3
"""
Phase 4 Training Script - Enhanced Environment Training
Train RL agent with improved environment simulation and reward function.
"""
import argparse
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.env_util import make_vec_env

from src.ml.environment import PokemonBattleEnv
from src.agents.random_agent import RandomAgent


def make_env(rank=0, seed=0):
    """
    Create a Pokemon battle environment.
    
    Args:
        rank: Index of the environment
        seed: Random seed
    """
    def _init():
        env = PokemonBattleEnv(opponent_agent=RandomAgent())
        env.reset(seed=seed + rank)
        return env
    return _init


def train_phase4(
    algorithm="PPO",
    timesteps=1000000,
    n_envs=16,
    save_path="models/ppo_phase4",
    log_dir="logs/phase4",
    checkpoint_freq=100000,
    eval_freq=50000,
    resume=None
):
    """
    Train Phase 4 model with enhanced environment.
    
    Args:
        algorithm: RL algorithm (PPO, A2C, DQN)
        timesteps: Total training timesteps
        n_envs: Number of parallel environments
        save_path: Path to save the model
        log_dir: Path for TensorBoard logs
        checkpoint_freq: Frequency of checkpoint saves
        eval_freq: Frequency of evaluation
        resume: Path to model to resume from
    """
    print("=" * 70)
    print("Phase 4 Training - Enhanced Environment")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  Algorithm: {algorithm}")
    print(f"  Total timesteps: {timesteps:,}")
    print(f"  Parallel environments: {n_envs}")
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
    
    if n_envs == 1:
        env = DummyVecEnv([make_env(0)])
    elif n_envs <= 4:
        env = DummyVecEnv([make_env(i) for i in range(n_envs)])
    else:
        # Use SubprocVecEnv for better performance with many envs
        env = SubprocVecEnv([make_env(i) for i in range(n_envs)])
    
    print("✅ Environments created")
    print()
    
    # Create evaluation environment
    print("Creating evaluation environment...")
    eval_env = DummyVecEnv([make_env(1000)])  # Different seed
    print("✅ Evaluation environment created")
    print()
    
    # Create callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=checkpoint_freq // n_envs,  # Adjust for parallel envs
        save_path=save_path,
        name_prefix="checkpoint",
        save_replay_buffer=False,
        save_vecnormalize=False,
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_path,
        log_path=log_dir,
        eval_freq=eval_freq // n_envs,  # Adjust for parallel envs
        n_eval_episodes=10,
        deterministic=True,
        render=False,
    )
    
    # Create or load model
    if resume:
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
        
        if algorithm == "PPO":
            model = PPO(
                "MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=log_dir,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=256,  # Larger batch for better stability
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01,  # Entropy for exploration
                vf_coef=0.5,
                max_grad_norm=0.5,
                device="auto"
            )
        elif algorithm == "A2C":
            model = A2C(
                "MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=log_dir,
                learning_rate=7e-4,
                n_steps=5,
                gamma=0.99,
                gae_lambda=1.0,
                ent_coef=0.01,
                vf_coef=0.5,
                max_grad_norm=0.5,
                device="auto"
            )
        elif algorithm == "DQN":
            model = DQN(
                "MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=log_dir,
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
                device="auto"
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
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
        # Train the model
        model.learn(
            total_timesteps=timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=False,  # Disabled to avoid tqdm dependency
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print()
        print("=" * 70)
        print("✅ Training completed successfully!")
        print("=" * 70)
        print(f"Duration: {duration}")
        print()
        
        # Save final model
        final_model_path = os.path.join(save_path, "final_model")
        model.save(final_model_path)
        print(f"Final model saved to: {final_model_path}")
        print()
        
        # Save metadata
        metadata = {
            "algorithm": algorithm,
            "timesteps": timesteps,
            "n_envs": n_envs,
            "duration_seconds": duration.total_seconds(),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }
        
        import json
        metadata_path = os.path.join(save_path, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"Metadata saved to: {metadata_path}")
        print()
        
        print("Next steps:")
        print(f"  1. View training progress: tensorboard --logdir {log_dir}")
        print(f"  2. Evaluate model: python scripts/evaluate_rl.py --model {final_model_path} --algorithm {algorithm}")
        print(f"  3. Benchmark model: python scripts/benchmark_phase3.py --model {final_model_path} --algorithm {algorithm}")
        print()
        
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("Training interrupted by user")
        print("=" * 70)
        
        # Save interrupted model
        interrupted_path = os.path.join(save_path, "interrupted_model")
        model.save(interrupted_path)
        print(f"Model saved to: {interrupted_path}")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Training failed with error: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Clean up
        env.close()
        eval_env.close()


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4 Training - Enhanced Environment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard Phase 4 training (1M timesteps, 16 envs)
  python scripts/train_phase4.py --timesteps 1000000 --n-envs 16

  # Quick test (10k timesteps, 4 envs)
  python scripts/train_phase4.py --timesteps 10000 --n-envs 4

  # Resume from Phase 3 model
  python scripts/train_phase4.py --resume models/ppo_phase3_500k/final_model --timesteps 500000

  # Extended training (5M timesteps)
  python scripts/train_phase4.py --timesteps 5000000 --n-envs 16

  # Try A2C algorithm
  python scripts/train_phase4.py --algorithm A2C --timesteps 1000000
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
        default="models/ppo_phase4",
        help="Path to save the model (default: models/ppo_phase4)"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs/phase4",
        help="Path for TensorBoard logs (default: logs/phase4)"
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
        help="Path to model to resume training from"
    )
    
    args = parser.parse_args()
    
    train_phase4(
        algorithm=args.algorithm,
        timesteps=args.timesteps,
        n_envs=args.n_envs,
        save_path=args.save_path,
        log_dir=args.log_dir,
        checkpoint_freq=args.checkpoint_freq,
        eval_freq=args.eval_freq,
        resume=args.resume
    )


if __name__ == "__main__":
    main()
