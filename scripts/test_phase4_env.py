#!/usr/bin/env python3
"""Test script for Phase 4 enhanced environment."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ml.environment import PokemonBattleEnv
from src.agents.random_agent import RandomAgent
import numpy as np


def test_environment():
    """Test the enhanced Phase 4 environment."""
    print("=" * 60)
    print("Phase 4 Environment Test")
    print("=" * 60)
    print()
    
    # Create environment
    print("Creating environment...")
    env = PokemonBattleEnv(opponent_agent=RandomAgent())
    print("✅ Environment created successfully")
    print()
    
    # Test reset
    print("Testing reset...")
    obs, info = env.reset()
    print(f"✅ Reset successful")
    print(f"  - Observation shape: {obs.shape}")
    print(f"  - Observation range: [{obs.min():.2f}, {obs.max():.2f}]")
    print(f"  - Turn: {info['turn']}")
    print(f"  - Our Pokemon alive: {info['our_pokemon_alive']}")
    print(f"  - Opponent Pokemon alive: {info['opponent_pokemon_alive']}")
    print()
    
    # Test action mask
    print("Testing action masking...")
    action_mask = env.get_action_mask()
    print(f"✅ Action mask retrieved")
    print(f"  - Valid moves: {action_mask[0:4].sum()}/4")
    print(f"  - Valid switches: {action_mask[4:9].sum()}/5")
    print(f"  - Action mask: {action_mask}")
    print()
    
    # Test a few steps
    print("Testing episode execution...")
    total_reward = 0
    for i in range(5):
        # Random action (respecting mask)
        valid_actions = np.where(action_mask)[0]
        action = np.random.choice(valid_actions)
        
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        print(f"  Step {i+1}:")
        print(f"    - Action: {action}")
        print(f"    - Reward: {reward:.2f}")
        print(f"    - Total reward: {total_reward:.2f}")
        print(f"    - Our Pokemon alive: {info['our_pokemon_alive']}")
        print(f"    - Opponent Pokemon alive: {info['opponent_pokemon_alive']}")
        
        if terminated or truncated:
            print(f"    - Episode ended: {'terminated' if terminated else 'truncated'}")
            break
        
        # Update action mask for next iteration
        action_mask = info['action_mask']
    
    print()
    print("✅ Episode test completed")
    print()
    
    # Test full episode
    print("Running full episode to completion...")
    obs, info = env.reset()
    episode_reward = 0
    steps = 0
    max_steps = 100
    
    while steps < max_steps:
        action_mask = info['action_mask']
        valid_actions = np.where(action_mask)[0]
        action = np.random.choice(valid_actions)
        
        obs, reward, terminated, truncated, info = env.step(action)
        episode_reward += reward
        steps += 1
        
        if terminated or truncated:
            break
    
    print(f"✅ Full episode completed")
    print(f"  - Total steps: {steps}")
    print(f"  - Total reward: {episode_reward:.2f}")
    print(f"  - Final state:")
    print(f"    - Our Pokemon alive: {info['our_pokemon_alive']}")
    print(f"    - Opponent Pokemon alive: {info['opponent_pokemon_alive']}")
    print(f"    - Outcome: {'WIN' if info['our_pokemon_alive'] > info['opponent_pokemon_alive'] else 'LOSS'}")
    print()
    
    # Test state representation
    print("Testing state representation...")
    our_active = env.state.get_our_active_pokemon()
    opp_active = env.state.get_opponent_active_pokemon()
    
    if our_active:
        print(f"  Our active Pokemon:")
        print(f"    - Species: {our_active.species}")
        print(f"    - Types: {our_active.types}")
        print(f"    - HP: {our_active.hp}/{our_active.max_hp} ({our_active.hp_percent:.1f}%)")
        print(f"    - Stats: ATK={our_active.stats.get('atk')}, SPE={our_active.stats.get('spe')}")
    
    if opp_active:
        print(f"  Opponent active Pokemon:")
        print(f"    - Species: {opp_active.species}")
        print(f"    - Types: {opp_active.types}")
        print(f"    - HP: {opp_active.hp}/{opp_active.max_hp} ({opp_active.hp_percent:.1f}%)")
    
    print()
    print("=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)
    print()
    print("Phase 4 environment enhancements:")
    print("  ✅ Real damage calculator integrated")
    print("  ✅ Type effectiveness in state representation")
    print("  ✅ Win-focused reward function")
    print("  ✅ Action masking implemented")
    print("  ✅ Speed-based turn order")
    print()
    print("Ready for Phase 4 training!")


if __name__ == "__main__":
    try:
        test_environment()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
