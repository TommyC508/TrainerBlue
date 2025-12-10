"""Run a full battle between two RL agents with detailed output."""
import random
from src.ml import RLAgent, PokemonBattleEnv
from src.data.models import Pokemon
from src.data.type_effectiveness import get_type_effectiveness
from src.data.type_effectiveness import get_type_effectiveness

def create_random_team(team_name: str) -> list:
    """Create a random team of 6 Pokemon with real moves."""
    # Pokemon with their types and signature moves
    pokemon_data = {
        "Charizard": {"types": ["Fire", "Flying"], "moves": ["Flamethrower", "Air Slash", "Dragon Claw", "Heat Wave"]},
        "Blastoise": {"types": ["Water"], "moves": ["Hydro Pump", "Ice Beam", "Surf", "Flash Cannon"]},
        "Venusaur": {"types": ["Grass", "Poison"], "moves": ["Solar Beam", "Sludge Bomb", "Giga Drain", "Earth Power"]},
        "Pikachu": {"types": ["Electric"], "moves": ["Thunderbolt", "Thunder", "Iron Tail", "Volt Tackle"]},
        "Gengar": {"types": ["Ghost", "Poison"], "moves": ["Shadow Ball", "Sludge Bomb", "Dazzling Gleam", "Focus Blast"]},
        "Dragonite": {"types": ["Dragon", "Flying"], "moves": ["Dragon Claw", "Outrage", "Hurricane", "Earthquake"]},
        "Mewtwo": {"types": ["Psychic"], "moves": ["Psychic", "Psystrike", "Aura Sphere", "Shadow Ball"]},
        "Alakazam": {"types": ["Psychic"], "moves": ["Psychic", "Psyshock", "Shadow Ball", "Focus Blast"]},
        "Machamp": {"types": ["Fighting"], "moves": ["Close Combat", "Dynamic Punch", "Stone Edge", "Earthquake"]},
        "Gyarados": {"types": ["Water", "Flying"], "moves": ["Waterfall", "Aqua Tail", "Ice Fang", "Earthquake"]},
        "Lapras": {"types": ["Water", "Ice"], "moves": ["Hydro Pump", "Ice Beam", "Thunder", "Freeze-Dry"]},
        "Snorlax": {"types": ["Normal"], "moves": ["Body Slam", "Heavy Slam", "Earthquake", "Crunch"]},
        "Tyranitar": {"types": ["Rock", "Dark"], "moves": ["Stone Edge", "Crunch", "Earthquake", "Fire Blast"]},
        "Garchomp": {"types": ["Dragon", "Ground"], "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Fire Fang"]},
        "Metagross": {"types": ["Steel", "Psychic"], "moves": ["Meteor Mash", "Zen Headbutt", "Earthquake", "Bullet Punch"]},
        "Salamence": {"types": ["Dragon", "Flying"], "moves": ["Dragon Claw", "Outrage", "Earthquake", "Fire Blast"]},
        "Lucario": {"types": ["Fighting", "Steel"], "moves": ["Close Combat", "Flash Cannon", "Aura Sphere", "Earthquake"]},
        "Togekiss": {"types": ["Fairy", "Flying"], "moves": ["Air Slash", "Dazzling Gleam", "Aura Sphere", "Flamethrower"]}
    }
    
    selected = random.sample(list(pokemon_data.keys()), 6)
    team = []
    
    for i, species in enumerate(selected):
        hp = random.randint(250, 350)
        data = pokemon_data[species]
        pokemon = Pokemon(
            species=species,
            level=50,
            hp=hp,
            max_hp=hp,
            status="",
            active=(i == 0),
            types=data["types"],
            stats={
                "atk": random.randint(80, 150),
                "def": random.randint(70, 130),
                "spa": random.randint(80, 150),
                "spd": random.randint(70, 130),
                "spe": random.randint(60, 140)
            },
            moves=data["moves"]
        )
        team.append(pokemon)
    
    return team

def print_pokemon_status(pokemon: Pokemon, side: str):
    """Print a Pokemon's status."""
    status = f"{'❤️' * (pokemon.hp // 30)}"
    fainted = " [FAINTED]" if pokemon.fainted else ""
    active_marker = " 🎯" if pokemon.active else ""
    print(f"    {pokemon.species:15} HP: {pokemon.hp:3}/{pokemon.max_hp:3} {status}{fainted}{active_marker}")

def print_battle_state(state, turn: int, show_full: bool = False):
    """Print the current battle state."""
    if show_full:
        print("\n" + "="*70)
        print(f"TURN {turn}")
        print("="*70)
        
        print("\n🔵 YOUR TEAM:")
        for pkmn in state.our_side.team:
            print_pokemon_status(pkmn, "Your")
        
        print("\n🔴 OPPONENT TEAM:")
        for pkmn in state.opponent_side.team:
            print_pokemon_status(pkmn, "Opp")
        
        our_alive = state.our_side.count_alive()
        opp_alive = state.opponent_side.count_alive()
        print(f"\n📊 Score: Your team: {our_alive} alive | Opponent: {opp_alive} alive")

def get_move_type(move_name: str) -> str:
    """Get the type of a move."""
    move_types = {
        # Fire
        "Flamethrower": "Fire", "Heat Wave": "Fire", "Fire Blast": "Fire", "Fire Fang": "Fire",
        # Water
        "Hydro Pump": "Water", "Surf": "Water", "Waterfall": "Water", "Aqua Tail": "Water",
        # Grass
        "Solar Beam": "Grass", "Giga Drain": "Grass",
        # Electric
        "Thunderbolt": "Electric", "Thunder": "Electric", "Volt Tackle": "Electric",
        # Ice
        "Ice Beam": "Ice", "Ice Fang": "Ice", "Freeze-Dry": "Ice",
        # Fighting
        "Close Combat": "Fighting", "Dynamic Punch": "Fighting", "Aura Sphere": "Fighting",
        # Poison
        "Sludge Bomb": "Poison",
        # Ground
        "Earthquake": "Ground", "Earth Power": "Ground",
        # Flying
        "Air Slash": "Flying", "Hurricane": "Flying",
        # Psychic
        "Psychic": "Psychic", "Psystrike": "Psychic", "Psyshock": "Psychic", "Zen Headbutt": "Psychic",
        # Bug
        # Rock
        "Stone Edge": "Rock",
        # Ghost
        "Shadow Ball": "Ghost",
        # Dragon
        "Dragon Claw": "Dragon", "Outrage": "Dragon",
        # Dark
        "Crunch": "Dark",
        # Steel
        "Flash Cannon": "Steel", "Meteor Mash": "Steel", "Iron Tail": "Steel", "Bullet Punch": "Steel",
        # Fairy
        "Dazzling Gleam": "Fairy",
        # Normal
        "Body Slam": "Normal", "Heavy Slam": "Steel",
        # Multi-type
        "Focus Blast": "Fighting",
    }
    return move_types.get(move_name, "Normal")

def get_effectiveness_message(effectiveness: float) -> str:
    """Get effectiveness message based on multiplier."""
    if effectiveness == 0:
        return "❌ It had no effect!"
    elif effectiveness <= 0.25:
        return "🛡️  It's barely effective..."
    elif effectiveness <= 0.5:
        return "🛡️  It's not very effective..."
    elif effectiveness < 1.0:
        return "🛡️  It's not very effective..."
    elif effectiveness >= 4.0:
        return "💥 It's SUPER DUPER EFFECTIVE!"
    elif effectiveness >= 2.0:
        return "⚡ It's super effective!"
    elif effectiveness > 1.0:
        return "✓ It's effective!"
    return ""

def action_to_string(action: int, state) -> tuple:
    """Convert action number to human-readable string and move type."""
    if action < 4:
        our_pokemon = state.get_our_active_pokemon()
        if our_pokemon and len(our_pokemon.moves) > action:
            move_name = our_pokemon.moves[action]
            move_type = get_move_type(move_name)
            return f"uses {move_name}", move_type
        return f"uses move {action + 1}", "Normal"
    else:
        switch_idx = action - 3
        if switch_idx < len(state.our_side.team):
            return f"switches to {state.our_side.team[switch_idx].species}", None
        return f"switches to Pokemon {switch_idx}", None

def main():
    """Run a full battle simulation."""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "POKEMON BATTLE SIMULATOR" + " "*29 + "║")
    print("║" + " "*20 + "RL Agent vs RL Agent" + " "*29 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Load two trained models
    print("🔄 Loading trained models...")
    try:
        agent1 = RLAgent(algorithm='PPO', model_path='models/final_test/final_model')
        print("✅ Agent 1 (Blue) loaded: models/final_test/final_model")
    except:
        print("⚠️  No saved model found, creating new agent 1...")
        agent1 = RLAgent(algorithm='PPO', verbose=0)
        agent1.train(total_timesteps=5000)
    
    try:
        agent2 = RLAgent(algorithm='PPO', model_path='models/ppo_100k/final_model')
        print("✅ Agent 2 (Red) loaded: models/ppo_100k/final_model")
    except:
        print("⚠️  No saved model found, creating new agent 2...")
        agent2 = RLAgent(algorithm='PPO', verbose=0)
        agent2.train(total_timesteps=5000)
    
    # Create environment
    env = PokemonBattleEnv()
    
    # Start battle
    print("\n🎲 Generating random teams...")
    obs, info = env.reset()
    
    # Replace with random teams
    env.state.our_side.team = create_random_team("Blue")
    env.state.opponent_side.team = create_random_team("Red")
    env.state.our_side.active_pokemon = [0]
    env.state.opponent_side.active_pokemon = [0]
    
    print(f"\n🔵 BLUE TEAM (Agent 1):")
    for pkmn in env.state.our_side.team:
        types_str = "/".join(pkmn.types) if hasattr(pkmn, 'types') else "Normal"
        moves_str = ", ".join(pkmn.moves[:2]) if pkmn.moves else "No moves"
        print(f"   • {pkmn.species:12} [{types_str:15}] HP: {pkmn.max_hp:3} | Moves: {moves_str}...")
    
    print(f"\n🔴 RED TEAM (Agent 2):")
    for pkmn in env.state.opponent_side.team:
        types_str = "/".join(pkmn.types) if hasattr(pkmn, 'types') else "Normal"
        moves_str = ", ".join(pkmn.moves[:2]) if pkmn.moves else "No moves"
        print(f"   • {pkmn.species:12} [{types_str:15}] HP: {pkmn.max_hp:3} | Moves: {moves_str}...")
    
    print("\n" + "🎮 BATTLE START! " + "⚔️"*10)
    
    # Battle loop with detailed tracking
    turn = 1
    done = False
    total_reward = 0
    move_history = []
    damage_stats = {"blue_dealt": 0, "blue_taken": 0, "red_dealt": 0, "red_taken": 0}
    ko_count = {"blue": 0, "red": 0}
    
    print("\n" + "="*70)
    print("BATTLE LOG - EVERY MOVE TRACKED")
    print("="*70)
    
    while not done and turn <= 100:
        # Show minimal turn header
        our_pokemon = env.state.get_our_active_pokemon()
        opp_pokemon = env.state.get_opponent_active_pokemon()
        
        if not our_pokemon or not opp_pokemon:
            break
            
        print(f"\n{'─'*70}")
        print(f"⏱️  TURN {turn}")
        print(f"   🔵 {our_pokemon.species} (HP: {our_pokemon.hp}/{our_pokemon.max_hp}) vs 🔴 {opp_pokemon.species} (HP: {opp_pokemon.hp}/{opp_pokemon.max_hp})")
        
        # Store HP before action
        our_hp_before = our_pokemon.hp
        opp_hp_before = opp_pokemon.hp
        
        # Agent 1 chooses action
        obs = env._get_observation()
        action1, _ = agent1.model.predict(obs, deterministic=True)
        
        action_str, move_type = action_to_string(action1, env.state)
        print(f"\n   ⚡ {our_pokemon.species} {action_str}!")
        
        # DEBUG: Print move type
        if action1 < 4:
            print(f"      [DEBUG] move_type={repr(move_type)}, action1={action1}")
        
        # Show type effectiveness prediction if it's an attacking move
        if move_type is not None and action1 < 4:
            defender_types = opp_pokemon.types if hasattr(opp_pokemon, 'types') and opp_pokemon.types else ["Normal"]
            print(f"      [DEBUG] defender_types={defender_types}")
            total_effectiveness = 1.0
            for def_type in defender_types:
                effectiveness = get_type_effectiveness(move_type, def_type)
                print(f"      [DEBUG] {move_type} vs {def_type} = {effectiveness}")
                total_effectiveness *= effectiveness
            
            print(f"      [DEBUG] total_effectiveness={total_effectiveness}")
            effectiveness_msg = get_effectiveness_message(total_effectiveness)
            print(f"      [DEBUG] effectiveness_msg={repr(effectiveness_msg)}")
            if effectiveness_msg:
                print(f"      {effectiveness_msg} (×{total_effectiveness})")
        
        # Execute action
        obs, reward, terminated, truncated, info = env.step(action1)
        total_reward += reward
        done = terminated or truncated
        
        # Check what happened
        new_our = env.state.get_our_active_pokemon()
        new_opp = env.state.get_opponent_active_pokemon()
        
        # Calculate damage
        our_damage_taken = 0
        opp_damage_taken = 0
        
        if new_our and our_pokemon:
            our_damage_taken = our_hp_before - new_our.hp
            if our_damage_taken > 0:
                damage_stats["blue_taken"] += our_damage_taken
                damage_stats["red_dealt"] += our_damage_taken
                print(f"      ↘️  {our_pokemon.species} took {our_damage_taken} damage! (HP: {our_hp_before} → {new_our.hp})")
        
        if new_opp and opp_pokemon:
            opp_damage_taken = opp_hp_before - new_opp.hp
            if opp_damage_taken > 0:
                damage_stats["blue_dealt"] += opp_damage_taken
                damage_stats["red_taken"] += opp_damage_taken
                print(f"      ↗️  {opp_pokemon.species} took {opp_damage_taken} damage! (HP: {opp_hp_before} → {new_opp.hp})")
        
        # Track KOs
        if opp_pokemon.fainted:
            ko_count["blue"] += 1
            print(f"      💀 {opp_pokemon.species} fainted! (Blue team KO #{ko_count['blue']})")
            if new_opp and new_opp != opp_pokemon:
                print(f"      ➡️  Red sends out {new_opp.species}! (HP: {new_opp.hp}/{new_opp.max_hp})")
        
        if our_pokemon.fainted:
            ko_count["red"] += 1
            print(f"      💀 {our_pokemon.species} fainted! (Red team KO #{ko_count['red']})")
            if new_our and new_our != our_pokemon:
                print(f"      ➡️  Blue sends out {new_our.species}! (HP: {new_our.hp}/{new_our.max_hp})")
        
        # Record move
        move_history.append({
            "turn": turn,
            "attacker": our_pokemon.species,
            "defender": opp_pokemon.species,
            "action": action_str,
            "damage_dealt": opp_damage_taken,
            "damage_taken": our_damage_taken,
            "reward": reward
        })
        
        if done:
            break
        
        turn += 1
    
    # Final results with detailed statistics
    print("\n" + "="*70)
    print("🏆 BATTLE RESULTS & STATISTICS")
    print("="*70)
    
    final_our_alive = env.state.our_side.count_alive()
    final_opp_alive = env.state.opponent_side.count_alive()
    
    print(f"\n📊 Final Score:")
    print(f"   🔵 Blue Team: {final_our_alive}/6 Pokemon remaining")
    print(f"   🔴 Red Team:  {final_opp_alive}/6 Pokemon remaining")
    print(f"   🎯 Total Turns: {turn}")
    print(f"   💰 Total Reward: {total_reward:.2f}")
    
    if final_our_alive > final_opp_alive:
        print(f"\n   🎉 WINNER: BLUE TEAM (Agent 1)! 🎉")
    elif final_opp_alive > final_our_alive:
        print(f"\n   🎉 WINNER: RED TEAM (Agent 2)! 🎉")
    else:
        print(f"\n   🤝 DRAW! 🤝")
    
    # Damage statistics
    print(f"\n💥 DAMAGE STATISTICS:")
    print(f"   🔵 Blue Team:")
    print(f"      • Damage Dealt: {damage_stats['blue_dealt']} HP")
    print(f"      • Damage Taken: {damage_stats['blue_taken']} HP")
    print(f"      • Net Damage: {damage_stats['blue_dealt'] - damage_stats['blue_taken']:+d} HP")
    print(f"   🔴 Red Team:")
    print(f"      • Damage Dealt: {damage_stats['red_dealt']} HP")
    print(f"      • Damage Taken: {damage_stats['red_taken']} HP")
    print(f"      • Net Damage: {damage_stats['red_dealt'] - damage_stats['red_taken']:+d} HP")
    
    # KO statistics
    print(f"\n⚔️  KNOCKOUT STATISTICS:")
    print(f"   🔵 Blue Team KOs: {ko_count['blue']}")
    print(f"   🔴 Red Team KOs: {ko_count['red']}")
    
    # Average damage per turn
    if turn > 0:
        print(f"\n📈 EFFICIENCY METRICS:")
        print(f"   • Average damage/turn (Blue): {damage_stats['blue_dealt']/turn:.1f} HP")
        print(f"   • Average damage/turn (Red): {damage_stats['red_dealt']/turn:.1f} HP")
        print(f"   • Average turns per KO: {turn/(ko_count['blue'] + ko_count['red']):.1f}")
    
    print("\n" + "="*70)
    
    # Show surviving Pokemon
    if final_our_alive > 0:
        print("\n🔵 Blue Team Survivors:")
        for pkmn in env.state.our_side.team:
            if not pkmn.fainted:
                print_pokemon_status(pkmn, "Blue")
    
    if final_opp_alive > 0:
        print("\n🔴 Red Team Survivors:")
        for pkmn in env.state.opponent_side.team:
            if not pkmn.fainted:
                print_pokemon_status(pkmn, "Red")
    
    # Move history summary
    print("\n" + "="*70)
    print("📜 COMPLETE MOVE HISTORY")
    print("="*70)
    
    for move in move_history[-20:]:  # Show last 20 moves
        dmg_str = f"dealt {move['damage_dealt']} dmg" if move['damage_dealt'] > 0 else "no damage"
        taken_str = f", took {move['damage_taken']} dmg" if move['damage_taken'] > 0 else ""
        print(f"Turn {move['turn']:2d}: {move['attacker']:15} {move['action']:20} → {dmg_str}{taken_str}")
    
    if len(move_history) > 20:
        print(f"\n... (showing last 20 of {len(move_history)} total moves)")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
