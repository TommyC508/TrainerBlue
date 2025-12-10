#!/usr/bin/env python3
"""Test trained RL agent."""
import argparse
import logging
from pathlib import Path

from src.ml import RLAgent, PokemonBattleEnv
from src.utils import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Test RL agent."""
    parser = argparse.ArgumentParser(description="Test RL agent")
    parser.add_argument("model_path", type=str,
                       help="Path to trained model")
    parser.add_argument("--algorithm", type=str, default="PPO",
                       choices=["PPO", "DQN", "A2C"],
                       help="RL algorithm")
    parser.add_argument("--episodes", type=int, default=10,
                       help="Number of test episodes")
    parser.add_argument("--render", action="store_true",
                       help="Render episodes")
    parser.add_argument("--device", type=str, default="cpu",
                       help="Device to use")
    args = parser.parse_args()
    
    setup_logging(level="INFO")
    
    logger.info("=" * 60)
    logger.info("Testing RL Agent")
    logger.info("=" * 60)
    logger.info(f"Model: {args.model_path}")
    logger.info(f"Algorithm: {args.algorithm}")
    logger.info(f"Episodes: {args.episodes}")
    
    # Create agent
    agent = RLAgent(
        algorithm=args.algorithm,
        model_path=args.model_path,
        device=args.device
    )
    
    # Create environment
    env = PokemonBattleEnv(render_mode="human" if args.render else None)
    
    # Test episodes
    episode_rewards = []
    episode_lengths = []
    
    for episode in range(args.episodes):
        obs, info = env.reset()
        episode_reward = 0
        episode_length = 0
        done = False
        
        logger.info(f"\nEpisode {episode + 1}/{args.episodes}")
        
        while not done:
            # Predict action
            action, _states = agent.model.predict(obs, deterministic=True)
            
            # Take step
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            episode_reward += reward
            episode_length += 1
            
            if args.render:
                env.render()
        
        episode_rewards.append(episode_reward)
        episode_lengths.append(episode_length)
        
        logger.info(f"Reward: {episode_reward:.2f}, Length: {episode_length}")
    
    # Print summary
    import numpy as np
    
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Episodes: {args.episodes}")
    logger.info(f"Mean reward: {np.mean(episode_rewards):.2f} +/- {np.std(episode_rewards):.2f}")
    logger.info(f"Mean length: {np.mean(episode_lengths):.2f} +/- {np.std(episode_lengths):.2f}")
    logger.info(f"Min reward: {np.min(episode_rewards):.2f}")
    logger.info(f"Max reward: {np.max(episode_rewards):.2f}")
    logger.info("=" * 60)
    
    env.close()


if __name__ == "__main__":
    main()
