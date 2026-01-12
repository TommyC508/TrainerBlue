#!/usr/bin/env python3
"""
Demo battle with real Pokemon species and proper battle mechanics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.pokemon_data import create_pokemon_from_data, get_random_pokemon_team, get_move_data
from src.data.damage_calculator import DamageCalculator
from src.data.secondary_effects import SecondaryEffects
import random


def print_pokemon_status(pokemon, side_name):
    """Print current Pokemon status."""
    hp_bar_length = 20
    hp_pct = pokemon.hp / pokemon.max_hp
    filled = int(hp_bar_length * hp_pct)
    empty = hp_bar_length - filled
    hp_bar = "█" * filled + "░" * empty
    
    status_icon = "💀" if pokemon.fainted else "✅"
    status_text = ""
    if pokemon.status == "par":
        status_text = " [PAR]"
    elif pokemon.status == "brn":
        status_text = " [BRN]"
    elif pokemon.status == "psn":
        status_text = " [PSN]"
    elif pokemon.status == "slp":
        status_text = " [SLP]"
    elif pokemon.status == "frz":
        status_text = " [FRZ]"
    
    print(f"{status_icon} {side_name}: {pokemon.species}{status_text} | HP: {hp_bar} {pokemon.hp}/{pokemon.max_hp}")


def print_team_overview(team, side_name):
    """Print overview of team."""
    print(f"\n{side_name} Team:")
    for i, pokemon in enumerate(team):
        status = "💀 FAINTED" if pokemon.fainted or pokemon.hp == 0 else f"✅ {pokemon.hp}/{pokemon.max_hp} HP"
        print(f"  {i+1}. {pokemon.species} ({'/'.join(pokemon.types)}) - {status}")


def find_next_alive(team, current_idx):
    """Find next alive Pokemon."""
    for i in range(len(team)):
        if i != current_idx and team[i].hp > 0 and not team[i].fainted:
            return i
    return None


def simulate_battle():
    """Simulate a battle with real Pokemon."""
    print("=" * 60)
    print("🎮 POKEMON BATTLE SIMULATOR - REAL POKEMON EDITION")
    print("=" * 60)
    
    # Create teams
    print("\n📋 Creating teams...")
    rl_species = get_random_pokemon_team(6)
    opp_species = get_random_pokemon_team(6)
    
    rl_team = [create_pokemon_from_data(species) for species in rl_species]
    opp_team = [create_pokemon_from_data(species) for species in opp_species]
    
    print_team_overview(rl_team, "RL Agent")
    print_team_overview(opp_team, "Opponent")
    
    # Initialize battle
    rl_active_idx = 0
    opp_active_idx = 0
    turn = 0
    max_turns = 100
    
    calc = DamageCalculator()
    
    print("\n" + "=" * 60)
    print("⚔️  BATTLE START!")
    print("=" * 60)
    
    while turn < max_turns:
        turn += 1
        
        # Check for auto-switching
        if rl_team[rl_active_idx].hp == 0 or rl_team[rl_active_idx].fainted:
            next_idx = find_next_alive(rl_team, rl_active_idx)
            if next_idx is not None:
                old_pokemon = rl_team[rl_active_idx]
                old_pokemon.fainted = True
                rl_active_idx = next_idx
                print(f"🔄 RL Agent: {old_pokemon.species} fainted! Go, {rl_team[rl_active_idx].species}!")
            else:
                print("\n💥 RL Agent has no Pokemon left!")
                break
        
        if opp_team[opp_active_idx].hp == 0 or opp_team[opp_active_idx].fainted:
            next_idx = find_next_alive(opp_team, opp_active_idx)
            if next_idx is not None:
                old_pokemon = opp_team[opp_active_idx]
                old_pokemon.fainted = True
                opp_active_idx = next_idx
                print(f"🔄 Opponent: {old_pokemon.species} fainted! Go, {opp_team[opp_active_idx].species}!")
            else:
                print("\n💥 Opponent has no Pokemon left!")
                break
        
        # Get current Pokemon
        rl_pokemon = rl_team[rl_active_idx]
        opp_pokemon = opp_team[opp_active_idx]
        
        print(f"\n{'─' * 60}")
        print(f"Turn {turn}")
        print(f"{'─' * 60}")
        
        print_pokemon_status(rl_pokemon, "RL Agent")
        print_pokemon_status(opp_pokemon, "Opponent")
        
        # Choose moves (random for demo)
        rl_move_name = random.choice(rl_pokemon.moves)
        opp_move_name = random.choice(opp_pokemon.moves)
        
        rl_move = get_move_data(rl_move_name)
        opp_move = get_move_data(opp_move_name)
        
        print(f"\n🎯 RL Agent's {rl_pokemon.species} uses {rl_move_name}!")
        print(f"🎯 Opponent's {opp_pokemon.species} uses {opp_move_name}!")
        
        # Check paralysis (25% chance to be fully paralyzed)
        rl_paralyzed = rl_pokemon.status == "par" and random.random() < 0.25
        opp_paralyzed = opp_pokemon.status == "par" and random.random() < 0.25
        
        if rl_paralyzed:
            print(f"⚡ {rl_pokemon.species} is paralyzed! It can't move!")
        if opp_paralyzed:
            print(f"⚡ {opp_pokemon.species} is paralyzed! It can't move!")
        
        # Determine speed order (considering priority)
        rl_priority = rl_move.priority
        opp_priority = opp_move.priority
        
        if rl_priority != opp_priority:
            rl_goes_first = rl_priority > opp_priority
        else:
            rl_goes_first = calc.calculate_speed_order(rl_pokemon, opp_pokemon)
        
        # Execute moves in order
        if rl_goes_first:  # RL Agent goes first
            if not rl_paralyzed:
                print(f"⚡ {rl_pokemon.species} is faster!")
                
                # RL Agent attacks
                if rl_move.power > 0:
                    damage_range = calc.calculate_damage(
                        attacker=rl_pokemon,
                        defender=opp_pokemon,
                        move=rl_move,
                        is_critical=random.random() < 0.0625
                    )
                    damage = int(damage_range.average)
                    opp_pokemon.hp = max(0, opp_pokemon.hp - damage)
                    print(f"💥 Dealt {damage} damage to {opp_pokemon.species}!")
                    
                    # Apply secondary effects
                    effects = SecondaryEffects.apply_secondary_effects(rl_move, rl_pokemon, opp_pokemon, damage)
                    for effect_type, value in effects.items():
                        if effect_type == "status":
                            print(f"⚡ {opp_pokemon.species} {SecondaryEffects.get_status_message(value)}")
                        elif effect_type.startswith("boost_"):
                            stat = effect_type.replace("boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, False)}")
                        elif effect_type.startswith("self_boost_"):
                            stat = effect_type.replace("self_boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                        elif effect_type == "recoil":
                            print(f"💢 {rl_pokemon.species} was hurt by recoil! ({value} damage)")
                    
                    if opp_pokemon.hp == 0:
                        opp_pokemon.fainted = True
                        print(f"💀 {opp_pokemon.species} fainted!")
                elif rl_move.category == "Status":
                    # Apply status move effects
                    self_effects = SecondaryEffects.apply_self_effects(rl_move, rl_pokemon)
                    if self_effects:
                        for effect_type, value in self_effects.items():
                            if effect_type.startswith("boost_"):
                                stat = effect_type.replace("boost_", "")
                                print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                    elif "Thunder Wave" in rl_move.name:
                        if not opp_pokemon.status:
                            if "Electric" not in opp_pokemon.types and "Ground" not in opp_pokemon.types:
                                opp_pokemon.status = "par"
                                print(f"⚡ {opp_pokemon.species} {SecondaryEffects.get_status_message('par')}")
                            else:
                                print(f"❌ It doesn't affect {opp_pokemon.species}...")
                        else:
                            print(f"❌ But it failed!")
            
            # Opponent attacks if still alive
            if opp_pokemon.hp > 0 and not opp_paralyzed:
                if opp_move.power > 0:
                    damage_range = calc.calculate_damage(
                        attacker=opp_pokemon,
                        defender=rl_pokemon,
                        move=opp_move,
                        is_critical=random.random() < 0.0625
                    )
                    damage = int(damage_range.average)
                    rl_pokemon.hp = max(0, rl_pokemon.hp - damage)
                    print(f"💥 {opp_pokemon.species} dealt {damage} damage!")
                    
                    # Apply secondary effects
                    effects = SecondaryEffects.apply_secondary_effects(opp_move, opp_pokemon, rl_pokemon, damage)
                    for effect_type, value in effects.items():
                        if effect_type == "status":
                            print(f"⚡ {rl_pokemon.species} {SecondaryEffects.get_status_message(value)}")
                        elif effect_type.startswith("boost_"):
                            stat = effect_type.replace("boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, False)}")
                        elif effect_type.startswith("self_boost_"):
                            stat = effect_type.replace("self_boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                        elif effect_type == "recoil":
                            print(f"💢 {opp_pokemon.species} was hurt by recoil! ({value} damage)")
                    
                    if rl_pokemon.hp == 0:
                        rl_pokemon.fainted = True
                        print(f"💀 {rl_pokemon.species} fainted!")
                elif opp_move.category == "Status":
                    # Apply status move effects
                    self_effects = SecondaryEffects.apply_self_effects(opp_move, opp_pokemon)
                    if self_effects:
                        for effect_type, value in self_effects.items():
                            if effect_type.startswith("boost_"):
                                stat = effect_type.replace("boost_", "")
                                print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                    elif "Thunder Wave" in opp_move.name:
                        if not rl_pokemon.status:
                            if "Electric" not in rl_pokemon.types and "Ground" not in rl_pokemon.types:
                                rl_pokemon.status = "par"
                                print(f"⚡ {rl_pokemon.species} {SecondaryEffects.get_status_message('par')}")
                            else:
                                print(f"❌ It doesn't affect {rl_pokemon.species}...")
                        else:
                            print(f"❌ But it failed!")
        
        else:  # Opponent goes first
            if not opp_paralyzed:
                print(f"⚡ {opp_pokemon.species} is faster!")
                
                # Opponent attacks
                if opp_move.power > 0:
                    damage_range = calc.calculate_damage(
                        attacker=opp_pokemon,
                        defender=rl_pokemon,
                        move=opp_move,
                        is_critical=random.random() < 0.0625
                    )
                    damage = int(damage_range.average)
                    rl_pokemon.hp = max(0, rl_pokemon.hp - damage)
                    print(f"💥 Dealt {damage} damage to {rl_pokemon.species}!")
                    
                    # Apply secondary effects
                    effects = SecondaryEffects.apply_secondary_effects(opp_move, opp_pokemon, rl_pokemon, damage)
                    for effect_type, value in effects.items():
                        if effect_type == "status":
                            print(f"⚡ {rl_pokemon.species} {SecondaryEffects.get_status_message(value)}")
                        elif effect_type.startswith("boost_"):
                            stat = effect_type.replace("boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, False)}")
                        elif effect_type.startswith("self_boost_"):
                            stat = effect_type.replace("self_boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                        elif effect_type == "recoil":
                            print(f"💢 {opp_pokemon.species} was hurt by recoil! ({value} damage)")
                    
                    if rl_pokemon.hp == 0:
                        rl_pokemon.fainted = True
                        print(f"💀 {rl_pokemon.species} fainted!")
                elif opp_move.category == "Status":
                    # Apply status move effects
                    self_effects = SecondaryEffects.apply_self_effects(opp_move, opp_pokemon)
                    if self_effects:
                        for effect_type, value in self_effects.items():
                            if effect_type.startswith("boost_"):
                                stat = effect_type.replace("boost_", "")
                                print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                    elif "Thunder Wave" in opp_move.name:
                        if not rl_pokemon.status:
                            if "Electric" not in rl_pokemon.types and "Ground" not in rl_pokemon.types:
                                rl_pokemon.status = "par"
                                print(f"⚡ {rl_pokemon.species} {SecondaryEffects.get_status_message('par')}")
                            else:
                                print(f"❌ It doesn't affect {rl_pokemon.species}...")
                        else:
                            print(f"❌ But it failed!")
            
            # RL Agent attacks if still alive
            if rl_pokemon.hp > 0 and not rl_paralyzed:
                if rl_move.power > 0:
                    damage_range = calc.calculate_damage(
                        attacker=rl_pokemon,
                        defender=opp_pokemon,
                        move=rl_move,
                        is_critical=random.random() < 0.0625
                    )
                    damage = int(damage_range.average)
                    opp_pokemon.hp = max(0, opp_pokemon.hp - damage)
                    print(f"💥 {rl_pokemon.species} dealt {damage} damage!")
                    
                    # Apply secondary effects
                    effects = SecondaryEffects.apply_secondary_effects(rl_move, rl_pokemon, opp_pokemon, damage)
                    for effect_type, value in effects.items():
                        if effect_type == "status":
                            print(f"⚡ {opp_pokemon.species} {SecondaryEffects.get_status_message(value)}")
                        elif effect_type.startswith("boost_"):
                            stat = effect_type.replace("boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, False)}")
                        elif effect_type.startswith("self_boost_"):
                            stat = effect_type.replace("self_boost_", "")
                            print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                        elif effect_type == "recoil":
                            print(f"💢 {rl_pokemon.species} was hurt by recoil! ({value} damage)")
                    
                    if opp_pokemon.hp == 0:
                        opp_pokemon.fainted = True
                        print(f"💀 {opp_pokemon.species} fainted!")
                elif rl_move.category == "Status":
                    # Apply status move effects
                    self_effects = SecondaryEffects.apply_self_effects(rl_move, rl_pokemon)
                    if self_effects:
                        for effect_type, value in self_effects.items():
                            if effect_type.startswith("boost_"):
                                stat = effect_type.replace("boost_", "")
                                print(f"📊 {SecondaryEffects.get_boost_message(stat, value, True)}")
                    elif "Thunder Wave" in rl_move.name:
                        if not opp_pokemon.status:
                            if "Electric" not in opp_pokemon.types and "Ground" not in opp_pokemon.types:
                                opp_pokemon.status = "par"
                                print(f"⚡ {opp_pokemon.species} {SecondaryEffects.get_status_message('par')}")
                            else:
                                print(f"❌ It doesn't affect {opp_pokemon.species}...")
                        else:
                            print(f"❌ But it failed!")
        
        # Apply end-of-turn status damage
        rl_status_dmg = SecondaryEffects.apply_status_damage(rl_pokemon)
        if rl_status_dmg > 0:
            print(f"💢 {rl_pokemon.species} took {rl_status_dmg} damage from {rl_pokemon.status.upper()}!")
            if rl_pokemon.hp == 0:
                rl_pokemon.fainted = True
                print(f"💀 {rl_pokemon.species} fainted from status damage!")
        
        opp_status_dmg = SecondaryEffects.apply_status_damage(opp_pokemon)
        if opp_status_dmg > 0:
            print(f"💢 {opp_pokemon.species} took {opp_status_dmg} damage from {opp_pokemon.status.upper()}!")
            if opp_pokemon.hp == 0:
                opp_pokemon.fainted = True
                print(f"💀 {opp_pokemon.species} fainted from status damage!")
        
        # Check if battle is over
        rl_alive = sum(1 for p in rl_team if p.hp > 0 and not p.fainted)
        opp_alive = sum(1 for p in opp_team if p.hp > 0 and not p.fainted)
        
        if rl_alive == 0 or opp_alive == 0:
            break
    
    # Final results
    print("\n" + "=" * 60)
    print("🏁 BATTLE END!")
    print("=" * 60)
    
    rl_alive = sum(1 for p in rl_team if p.hp > 0 and not p.fainted)
    opp_alive = sum(1 for p in opp_team if p.hp > 0 and not p.fainted)
    
    print_team_overview(rl_team, "RL Agent")
    print_team_overview(opp_team, "Opponent")
    
    print(f"\nFinal Score: RL Agent {rl_alive} - {opp_alive} Opponent")
    
    if rl_alive > opp_alive:
        print("🏆 RL AGENT WINS!")
    elif opp_alive > rl_alive:
        print("💀 OPPONENT WINS!")
    else:
        print("🤝 DRAW!")
    
    print(f"\nBattle lasted {turn} turns")


if __name__ == "__main__":
    simulate_battle()
