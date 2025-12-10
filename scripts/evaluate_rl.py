"""Evaluation script for trained RL agent."""
import argparse
import logging
from pathlib import Path

from src.utils import setup_logging
from src.ml import RLAgent, PokemonBattleEnv
from src.agents import RandomAgent, HeuristicAgent

logger = logging.getLogger(__name__)


def evaluate_agent(agent: RLAgent, opponent, n_episodes: int = 100):
    """
    Evaluate trained agent against opponent.
    
    Args:
        agent: Trained RL agent
        opponent: Opponent agent
        n_episodes: Number of episodes to evaluate
        
    Returns:
        Dictionary with evaluation metrics
    """
    env = PokemonBattleEnv(opponent_agent=opponent)
    
    wins = 0
    total_rewards = []
    episode_lengths = []
    
    logger.info(f"Evaluating for {n_episodes} episodes...")
    
    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0
        steps = 0
        
        while not done:
            # Get action from agent
            action, _ = agent.model.predict(obs, deterministic=True)
            
            # Step environment
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            episode_reward += reward
            steps += 1
        
        # Check if won
        if info.get("our_alive", 0) > info.get("opp_alive", 0):
            wins += 1
        
        total_rewards.append(episode_reward)
        episode_lengths.append(steps)
        
        if (episode + 1) % 10 == 0:
            logger.info(f"Episode {episode + 1}/{n_episodes}")
    
    # Calculate metrics
    win_rate = (wins / n_episodes) * 100
    avg_reward = sum(total_rewards) / len(total_rewards)
    avg_length = sum(episode_lengths) / len(episode_lengths)
    
    return {
        "win_rate": win_rate,
        "avg_reward": avg_reward,
        "avg_episode_length": avg_length,
        "wins": wins,
        "losses": n_episodes - wins,
    }


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate trained RL agent")
    parser.add_argument("--model", type=str, required=True,
                       help="Path to trained model")
    parser.add_argument("--algorithm", type=str, default="PPO",
                       choices=["PPO", "DQN", "A2C"],
                       help="RL algorithm used")
    parser.add_argument("--opponent", type=str, default="random",
                       choices=["random", "heuristic"],
                       help="Opponent agent type")
    parser.add_argument("--episodes", type=int, default=100,
                       help="Number of evaluation episodes")
    parser.add_argument("--log-level", type=str, default="INFO",
                       help="Logging level")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    
    logger.info("=== RL Agent Evaluation ===")
    logger.info(f"Model: {args.model}")
    logger.info(f"Algorithm: {args.algorithm}")
    logger.info(f"Opponent: {args.opponent}")
    logger.info(f"Episodes: {args.episodes}")
    
    # Check if model exists
    if not Path(args.model + ".zip").exists():
        logger.error(f"Model not found: {args.model}")
        return
    
    # Create opponent
    if args.opponent == "random":
        opponent = RandomAgent()
    elif args.opponent == "heuristic":
        opponent = HeuristicAgent()
    else:
        opponent = None
    
    logger.info(f"Opponent: {opponent.name if opponent else 'None'}")
    
    # Load trained agent
    agent = RLAgent(algorithm=args.algorithm, model_path=args.model)
    logger.info("Model loaded successfully")
    
    # Evaluate
    results = evaluate_agent(agent, opponent, n_episodes=args.episodes)
    
    # Print results
    logger.info("\n=== Evaluation Results ===")
    logger.info(f"Win Rate: {results['win_rate']:.1f}%")
    logger.info(f"Wins: {results['wins']}")
    logger.info(f"Losses: {results['losses']}")
    logger.info(f"Average Reward: {results['avg_reward']:.2f}")
    logger.info(f"Average Episode Length: {results['avg_episode_length']:.1f}")


if __name__ == "__main__":
    main()
