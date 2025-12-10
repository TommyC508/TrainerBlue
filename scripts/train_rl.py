#!/usr/bin/env python3
"""Training script for RL agent."""
import argparse
import logging
from pathlib import Path

from src.ml import RLAgent, create_vectorized_env
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train RL agent for Pokemon Showdown")
    parser.add_argument("--algorithm", type=str, default="PPO",
                       choices=["PPO", "DQN", "A2C"],
                       help="RL algorithm to use")
    parser.add_argument("--timesteps", type=int, default=100000,
                       help="Total training timesteps")
    parser.add_argument("--learning-rate", type=float, default=3e-4,
                       help="Learning rate")
    parser.add_argument("--batch-size", type=int, default=64,
                       help="Batch size")
    parser.add_argument("--n-envs", type=int, default=4,
                       help="Number of parallel environments")
    parser.add_argument("--save-path", type=str, default="models/rl_agent",
                       help="Path to save model")
    parser.add_argument("--log-dir", type=str, default="logs/rl",
                       help="Directory for logs")
    parser.add_argument("--device", type=str, default="auto",
                       choices=["cpu", "cuda", "auto"],
                       help="Device to use for training")
    parser.add_argument("--resume", type=str, default=None,
                       help="Path to resume training from")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level="INFO", log_file=f"{args.log_dir}/training.log")
    
    logger.info("=" * 60)
    logger.info("Pokemon Showdown RL Training")
    logger.info("=" * 60)
    logger.info(f"Algorithm: {args.algorithm}")
    logger.info(f"Total timesteps: {args.timesteps}")
    logger.info(f"Learning rate: {args.learning_rate}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Parallel environments: {args.n_envs}")
    logger.info(f"Device: {args.device}")
    
    # Create directories
    Path(args.save_path).mkdir(parents=True, exist_ok=True)
    Path(args.log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create vectorized environment for parallel training
    if args.n_envs > 1:
        logger.info(f"Creating {args.n_envs} parallel environments")
        env = create_vectorized_env(n_envs=args.n_envs)
    else:
        from src.ml import PokemonBattleEnv
        env = PokemonBattleEnv()
    
    # Create agent
    logger.info("Creating RL agent...")
    
    agent_params = {
        "learning_rate": args.learning_rate,
        "batch_size": args.batch_size,
        "tensorboard_log": args.log_dir,
    }
    
    # Algorithm-specific parameters
    if args.algorithm == "PPO":
        agent_params.update({
            "n_steps": 2048,
            "n_epochs": 10,
            "gamma": 0.99,
            "gae_lambda": 0.95,
            "clip_range": 0.2,
            "ent_coef": 0.01,
        })
    elif args.algorithm == "DQN":
        agent_params.update({
            "buffer_size": 100000,
            "learning_starts": 50000,
            "target_update_interval": 10000,
            "train_freq": 4,
            "gradient_steps": 1,
            "exploration_fraction": 0.1,
            "exploration_final_eps": 0.05,
        })
    
    agent = RLAgent(
        algorithm=args.algorithm,
        model_path=args.resume,
        device=args.device,
        env=env,
        **agent_params
    )
    
    # Train
    logger.info("Starting training...")
    try:
        agent.train(
            total_timesteps=args.timesteps,
            log_dir=args.log_dir,
            save_path=args.save_path,
            eval_freq=10000,
            n_eval_episodes=10,
        )
        
        logger.info("Training complete!")
        logger.info(f"Model saved to {args.save_path}")
        logger.info(f"Logs saved to {args.log_dir}")
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        save_path = f"{args.save_path}/interrupted_model"
        agent.save(save_path)
        logger.info(f"Saved interrupted model to {save_path}")
    
    # Evaluate final model
    logger.info("Evaluating final model...")
    from stable_baselines3.common.evaluation import evaluate_policy
    
    mean_reward, std_reward = evaluate_policy(
        agent.model,
        env,
        n_eval_episodes=20,
        deterministic=True
    )
    
    logger.info(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
    
    # Print statistics
    logger.info("\n" + "=" * 60)
    logger.info("Training Summary")
    logger.info("=" * 60)
    logger.info(f"Algorithm: {args.algorithm}")
    logger.info(f"Total timesteps: {args.timesteps}")
    logger.info(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
    logger.info(f"Model saved: {args.save_path}")
    logger.info(f"Logs: {args.log_dir}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
