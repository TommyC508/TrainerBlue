"""Test script to verify team variety with expanded Pokemon roster."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ml.pokemon_env import PokemonBattleEnv

def main():
    """Test that teams vary between episodes."""
    env = PokemonBattleEnv()
    
    print("\n" + "="*60)
    print("TESTING TEAM VARIETY (24 Pokemon Pool)")
    print("="*60 + "\n")
    
    # Track unique Pokemon seen
    seen_pokemon = set()
    
    # Reset 5 times and show different teams
    for episode in range(5):
        obs, info = env.reset()
        
        print(f"Episode {episode + 1} Teams:")
        print("-" * 60)
        
        # Show our team
        print("Our Team:")
        for i, pkmn in enumerate(env.state.our_side.team, 1):
            types = f"{pkmn.types[0]}/{pkmn.types[1]}" if len(pkmn.types) > 1 else pkmn.types[0]
            print(f"  {i}. {pkmn.species:<15} Lv.{pkmn.level} - {types:<20} HP: {pkmn.current_hp}/{pkmn.max_hp}")
            seen_pokemon.add(pkmn.species)
            
            # Show first 2 moves
            moves_str = ", ".join([m.name for m in pkmn.moves[:2]])
            print(f"     Moves: {moves_str}, ...")
        
        print()
        
        # Show opponent team
        print("Opponent Team:")
        for i, pkmn in enumerate(env.state.opponent_side.team, 1):
            types = f"{pkmn.types[0]}/{pkmn.types[1]}" if len(pkmn.types) > 1 else pkmn.types[0]
            print(f"  {i}. {pkmn.species:<15} Lv.{pkmn.level} - {types:<20} HP: {pkmn.current_hp}/{pkmn.max_hp}")
            seen_pokemon.add(pkmn.species)
        
        print("\n")
    
    print("="*60)
    print(f"SUMMARY: Saw {len(seen_pokemon)} unique Pokemon across 5 episodes")
    print(f"Pokemon pool size: 24")
    print(f"Variety rate: {len(seen_pokemon)/24*100:.1f}%")
    print("="*60)
    
    # Show which Pokemon were seen
    print("\nPokemon Encountered:")
    for pkmn in sorted(seen_pokemon):
        print(f"  ✓ {pkmn}")
    
    print("\n✅ Team variety test complete!")

if __name__ == "__main__":
    main()
