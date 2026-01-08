#!/usr/bin/env python3
"""
Phase 3 Benchmarking Script
Comprehensive evaluation of trained RL agents against baseline agents.
"""
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime

from src.utils import setup_logging
from src.ml import RLAgent, PokemonBattleEnv
from src.agents import RandomAgent, HeuristicAgent

logger = logging.getLogger(__name__)


def evaluate_agent(agent: RLAgent, opponent, opponent_name: str, n_episodes: int = 100):
    """
    Evaluate trained agent against opponent.
    
    Args:
        agent: Trained RL agent
        opponent: Opponent agent
        opponent_name: Name of opponent for logging
        n_episodes: Number of episodes to evaluate
        
    Returns:
        Dictionary with evaluation metrics
    """
    env = PokemonBattleEnv(opponent_agent=opponent)
    
    wins = 0
    total_rewards = []
    episode_lengths = []
    damage_dealt = []
    damage_taken = []
    
    logger.info(f"Evaluating against {opponent_name} for {n_episodes} episodes...")
    
    for episode in range(n_episodes):
        obs, info = env.reset()
        done = False
        episode_reward = 0
        steps = 0
        ep_damage_dealt = 0
        ep_damage_taken = 0
        
        while not done:
            # Get action from agent
            action, _ = agent.model.predict(obs, deterministic=True)
            
            # Step environment
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            episode_reward += reward
            steps += 1
        
        # Check result
        our_alive = info.get("our_pokemon_alive", 0)
        opp_alive = info.get("opponent_pokemon_alive", 0)
        
        if our_alive > opp_alive:
            wins += 1
        
        total_rewards.append(episode_reward)
        episode_lengths.append(steps)
        
        if (episode + 1) % 20 == 0:
            logger.info(f"Progress: {episode + 1}/{n_episodes} episodes")
    
    # Calculate metrics
    win_rate = (wins / n_episodes) * 100
    avg_reward = sum(total_rewards) / len(total_rewards)
    avg_length = sum(episode_lengths) / len(episode_lengths)
    std_reward = (sum((r - avg_reward) ** 2 for r in total_rewards) / len(total_rewards)) ** 0.5
    
    return {
        "opponent": opponent_name,
        "episodes": n_episodes,
        "wins": wins,
        "losses": n_episodes - wins,
        "win_rate": win_rate,
        "avg_reward": avg_reward,
        "std_reward": std_reward,
        "avg_episode_length": avg_length,
    }


def main():
    """Main benchmarking function."""
    parser = argparse.ArgumentParser(description="Phase 3 comprehensive benchmarking")
    parser.add_argument("--model", type=str, required=True,
                       help="Path to trained model")
    parser.add_argument("--algorithm", type=str, default="PPO",
                       choices=["PPO", "DQN", "A2C"],
                       help="RL algorithm used")
    parser.add_argument("--episodes", type=int, default=100,
                       help="Number of evaluation episodes per opponent")
    parser.add_argument("--output", type=str, default="logs/phase3_benchmark.json",
                       help="Output file for results")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level="INFO")
    
    logger.info("=" * 70)
    logger.info("PHASE 3 COMPREHENSIVE BENCHMARKING")
    logger.info("=" * 70)
    logger.info(f"Model: {args.model}")
    logger.info(f"Algorithm: {args.algorithm}")
    logger.info(f"Episodes per opponent: {args.episodes}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("")
    
    # Load trained agent
    logger.info("Loading trained RL agent...")
    env = PokemonBattleEnv()
    agent = RLAgent(
        algorithm=args.algorithm,
        model_path=args.model,
        env=env
    )
    logger.info("✓ Agent loaded successfully")
    logger.info("")
    
    # Benchmark results
    results = {
        "model": args.model,
        "algorithm": args.algorithm,
        "timestamp": datetime.now().isoformat(),
        "evaluations": []
    }
    
    # Evaluate against Random Agent
    logger.info("=" * 70)
    logger.info("EVALUATION 1: Random Agent Baseline")
    logger.info("=" * 70)
    random_agent = RandomAgent()
    random_results = evaluate_agent(agent, random_agent, "Random", args.episodes)
    results["evaluations"].append(random_results)
    
    logger.info("\nResults:")
    logger.info(f"  Win Rate: {random_results['win_rate']:.2f}%")
    logger.info(f"  Wins: {random_results['wins']}/{random_results['episodes']}")
    logger.info(f"  Avg Reward: {random_results['avg_reward']:.2f} ± {random_results['std_reward']:.2f}")
    logger.info(f"  Avg Episode Length: {random_results['avg_episode_length']:.1f} turns")
    logger.info("")
    
    # Evaluate against Heuristic Agent
    logger.info("=" * 70)
    logger.info("EVALUATION 2: Heuristic Agent")
    logger.info("=" * 70)
    heuristic_agent = HeuristicAgent()
    heuristic_results = evaluate_agent(agent, heuristic_agent, "Heuristic", args.episodes)
    results["evaluations"].append(heuristic_results)
    
    logger.info("\nResults:")
    logger.info(f"  Win Rate: {heuristic_results['win_rate']:.2f}%")
    logger.info(f"  Wins: {heuristic_results['wins']}/{heuristic_results['episodes']}")
    logger.info(f"  Avg Reward: {heuristic_results['avg_reward']:.2f} ± {heuristic_results['std_reward']:.2f}")
    logger.info(f"  Avg Episode Length: {heuristic_results['avg_episode_length']:.1f} turns")
    logger.info("")
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"✓ Results saved to {output_path}")
    logger.info("")
    
    # Print summary table
    logger.info("=" * 70)
    logger.info("PHASE 3 BENCHMARK SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"{'Opponent':<20} {'Win Rate':<15} {'Avg Reward':<20} {'Avg Length':<15}")
    logger.info("-" * 70)
    
    for eval_result in results["evaluations"]:
        logger.info(
            f"{eval_result['opponent']:<20} "
            f"{eval_result['win_rate']:>6.2f}%        "
            f"{eval_result['avg_reward']:>7.2f} ± {eval_result['std_reward']:<5.2f}    "
            f"{eval_result['avg_episode_length']:>6.1f} turns"
        )
    
    logger.info("-" * 70)
    logger.info("")
    
    # Performance assessment
    logger.info("PERFORMANCE ASSESSMENT:")
    logger.info("")
    
    random_wr = random_results['win_rate']
    heuristic_wr = heuristic_results['win_rate']
    
    if random_wr >= 70:
        logger.info("✓ Random Agent: EXCELLENT (≥70% win rate)")
    elif random_wr >= 50:
        logger.info("✓ Random Agent: GOOD (≥50% win rate)")
    elif random_wr >= 30:
        logger.info("⚠ Random Agent: MODERATE (≥30% win rate)")
    else:
        logger.info("✗ Random Agent: NEEDS IMPROVEMENT (<30% win rate)")
    
    if heuristic_wr >= 50:
        logger.info("✓ Heuristic Agent: EXCELLENT (≥50% win rate)")
    elif heuristic_wr >= 30:
        logger.info("✓ Heuristic Agent: GOOD (≥30% win rate)")
    elif heuristic_wr >= 15:
        logger.info("⚠ Heuristic Agent: MODERATE (≥15% win rate)")
    else:
        logger.info("✗ Heuristic Agent: NEEDS IMPROVEMENT (<15% win rate)")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("PHASE 3 BENCHMARKING COMPLETE")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
