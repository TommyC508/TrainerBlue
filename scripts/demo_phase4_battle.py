#!/usr/bin/env python3
"""Demo battle with Phase 4 trained model."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ml import PokemonBattleEnv, RLAgent
from src.agents import RandomAgent
import time


def print_pokemon_status(pokemon, label):
    """Print Pokemon status."""
    hp_bar_length = 20
    hp_percent = pokemon.hp / pokemon.max_hp if pokemon.max_hp > 0 else 0
    filled = int(hp_bar_length * hp_percent)
    bar = '█' * filled + '░' * (hp_bar_length - filled)
    
    status_icon = ""
    if pokemon.status == "brn":
        status_icon = " 🔥"
    elif pokemon.status == "par":
        status_icon = " ⚡"
    elif pokemon.status == "psn":
        status_icon = " ☠️"
    
    print(f"{label}: {pokemon.species}")
    print(f"  Types: {', '.join(pokemon.types)}")
    print(f"  HP: [{bar}] {pokemon.hp}/{pokemon.max_hp}{status_icon}")
    print(f"  Stats: ATK={pokemon.stats.get('atk', 100)} DEF={pokemon.stats.get('def', 100)} SPE={pokemon.stats.get('spe', 100)}")


def main():
    print("=" * 70)
    print("PHASE 4 BATTLE DEMONSTRATION")
    print("=" * 70)
    print()
    print("Loading trained model...")
    
    # Create agents
    random_agent = RandomAgent()
    rl_agent = RLAgent(
        algorithm="PPO",
        model_path="models/ppo_phase4/final_model"
    )
    
    print("✅ Model loaded successfully!")
    print()
    print("=" * 70)
    print("BATTLE START!")
    print("=" * 70)
    print()
    
    # Create environment
    env = PokemonBattleEnv(opponent_agent=random_agent)
    obs, info = env.reset()
    
    # Show initial teams
    print("🤖 RL AGENT'S TEAM:")
    for i, pokemon in enumerate(env.state.our_side.team, 1):
        print(f"  {i}. {pokemon.species} ({', '.join(pokemon.types)}) - HP: {pokemon.hp}/{pokemon.max_hp}")
    print()
    
    print("🎲 RANDOM OPPONENT'S TEAM:")
    for i, pokemon in enumerate(env.state.opponent_side.team, 1):
        print(f"  {i}. {pokemon.species} ({', '.join(pokemon.types)}) - HP: {pokemon.hp}/{pokemon.max_hp}")
    print()
    
    print("=" * 70)
    print()
    
    turn = 0
    done = False
    total_reward = 0
    
    while not done and turn < 100:
        turn += 1
        
        # Get active Pokemon
        our_active = env.state.get_our_active_pokemon()
        opp_active = env.state.get_opponent_active_pokemon()
        
        if not our_active or not opp_active:
            break
        
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"TURN {turn}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        
        # Show current Pokemon
        print_pokemon_status(our_active, "🤖 RL AGENT")
        print()
        print_pokemon_status(opp_active, "🎲 OPPONENT")
        print()
        
        # Store HP before turn
        our_hp_before = our_active.hp
        opp_hp_before = opp_active.hp
        
        # Get action from RL agent
        action, _ = rl_agent.model.predict(obs, deterministic=True)
        
        # Describe action
        if action < 4:
            print(f"🤖 RL Agent uses Move {action + 1}")
        else:
            print(f"🤖 RL Agent switches to Pokemon {action - 3}")
        
        # Step environment
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward
        
        # Show damage dealt
        our_hp_after = env.state.get_our_active_pokemon().hp if env.state.get_our_active_pokemon() else 0
        opp_hp_after = env.state.get_opponent_active_pokemon().hp if env.state.get_opponent_active_pokemon() else 0
        
        opp_damage = opp_hp_before - opp_hp_after
        our_damage = our_hp_before - our_hp_after
        
        if opp_damage > 0:
            print(f"   💥 Dealt {opp_damage} damage to opponent!")
        if our_damage > 0:
            print(f"   💔 Took {our_damage} damage!")
        
        # Check for KOs
        if opp_hp_after == 0 and opp_hp_before > 0:
            print(f"   ⭐ Opponent's {env.state.get_opponent_active_pokemon().species if env.state.get_opponent_active_pokemon() else 'Pokemon'} fainted!")
        if our_hp_after == 0 and our_hp_before > 0:
            print(f"   ❌ RL Agent's {env.state.get_our_active_pokemon().species if env.state.get_our_active_pokemon() else 'Pokemon'} fainted!")
        
        print(f"   📊 Reward this turn: {reward:.2f}")
        print()
        
        # Check alive counts
        our_alive = info['our_pokemon_alive']
        opp_alive = info['opponent_pokemon_alive']
        
        print(f"   Pokemon Remaining - RL Agent: {our_alive} | Opponent: {opp_alive}")
        print()
        
        if done:
            break
        
        # Small delay for readability
        time.sleep(0.1)
    
    print("=" * 70)
    print("BATTLE END!")
    print("=" * 70)
    print()
    
    our_alive = info['our_pokemon_alive']
    opp_alive = info['opponent_pokemon_alive']
    
    if our_alive > opp_alive:
        print("🏆 RL AGENT WINS!")
    elif opp_alive > our_alive:
        print("😢 OPPONENT WINS!")
    else:
        print("🤝 DRAW!")
    
    print()
    print(f"Battle Statistics:")
    print(f"  Total Turns: {turn}")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Final Score - RL Agent: {our_alive} | Opponent: {opp_alive}")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBattle interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
