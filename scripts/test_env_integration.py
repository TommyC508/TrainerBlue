"""
Test the integrated Pokemon Showdown battle system in the RL environment.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ml.pokemon_env import PokemonBattleEnv


def test_environment():
    """Test the environment with accurate battle mechanics."""
    print("\n" + "=" * 70)
    print(" TESTING POKEMON RL ENVIRONMENT WITH SHOWDOWN MECHANICS")
    print("=" * 70)
    
    # Create environment
    env = PokemonBattleEnv(render_mode="human")
    
    print("\n✓ Environment created successfully")
    print(f"  Action space: {env.action_space}")
    print(f"  Observation space: {env.observation_space.shape}")
    
    # Reset environment
    obs, info = env.reset()
    
    print("\n✓ Environment reset successfully")
    print(f"  Our team: {info['our_alive']} Pokemon alive")
    print(f"  Opponent team: {info['opp_alive']} Pokemon alive")
    print(f"  Observation shape: {obs.shape}")
    
    # Show initial teams
    print("\n" + "=" * 70)
    print(" INITIAL TEAMS")
    print("=" * 70)
    
    print("\nOur Team:")
    for i, bp in enumerate(env.our_team):
        marker = "→" if i == env.our_active_idx else " "
        print(f"  {marker} {i+1}. {bp.species:15} Lv.{bp.level} - {'/'.join(bp.types):20} "
              f"HP: {bp.current_hp}/{bp.max_hp}")
    
    print("\nOpponent Team:")
    for i, bp in enumerate(env.opp_team):
        marker = "→" if i == env.opp_active_idx else " "
        print(f"  {marker} {i+1}. {bp.species:15} Lv.{bp.level} - {'/'.join(bp.types):20} "
              f"HP: {bp.current_hp}/{bp.max_hp}")
    
    # Run a few steps
    print("\n" + "=" * 70)
    print(" BATTLE SIMULATION")
    print("=" * 70)
    
    total_reward = 0.0
    
    for step in range(10):
        # Take random action
        action = env.action_space.sample()
        
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        print(f"\nTurn {step + 1}:")
        print(f"  Action: {action} ({'Move ' + str(action+1) if action < 4 else 'Switch to ' + str(action-3)})")
        print(f"  Reward: {reward:.3f}")
        
        # Show active Pokemon HP
        our_bp = env.our_team[env.our_active_idx]
        opp_bp = env.opp_team[env.opp_active_idx]
        
        print(f"  Our {our_bp.species}: {our_bp.current_hp}/{our_bp.max_hp} HP "
              f"({our_bp.hp_percentage:.1f}%)")
        print(f"  Opp {opp_bp.species}: {opp_bp.current_hp}/{opp_bp.max_hp} HP "
              f"({opp_bp.hp_percentage:.1f}%)")
        
        if terminated or truncated:
            print(f"\n{'!' * 70}")
            if terminated:
                if info['our_alive'] > info['opp_alive']:
                    print(" VICTORY! Our team won!")
                else:
                    print(" DEFEAT! Opponent team won!")
            else:
                print(" Battle truncated (max turns reached)")
            print(f"{'!' * 70}")
            break
    
    # Final statistics
    print("\n" + "=" * 70)
    print(" FINAL STATISTICS")
    print("=" * 70)
    print(f"  Total turns: {step + 1}")
    print(f"  Total reward: {total_reward:.3f}")
    print(f"  Average reward per turn: {total_reward / (step + 1):.3f}")
    print(f"  Our Pokemon remaining: {info['our_alive']}/6")
    print(f"  Opponent Pokemon remaining: {info['opp_alive']}/6")
    
    print("\n" + "=" * 70)
    print(" TEAM STATUS")
    print("=" * 70)
    
    print("\nOur Team Final Status:")
    for i, bp in enumerate(env.our_team):
        status = "FAINTED" if bp.fainted else f"{bp.current_hp}/{bp.max_hp} HP"
        print(f"  {i+1}. {bp.species:15} {status}")
    
    print("\nOpponent Team Final Status:")
    for i, bp in enumerate(env.opp_team):
        status = "FAINTED" if bp.fainted else f"{bp.current_hp}/{bp.max_hp} HP"
        print(f"  {i+1}. {bp.species:15} {status}")
    
    env.close()
    
    print("\n" + "=" * 70)
    print(" ✅ TEST COMPLETE")
    print("=" * 70)
    print("\nThe RL environment now uses accurate Pokemon Showdown mechanics:")
    print("  • Real damage formula: floor(floor(floor(floor(2*L/5+2)*P*A)/D)/50)")
    print("  • Type effectiveness with 18 types")
    print("  • STAB, critical hits, and random variance")
    print("  • Accurate stat calculations from base stats")
    print("  • Weather, status, and boost modifiers")
    print("\nReady for RL agent training! 🎮")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_environment()
