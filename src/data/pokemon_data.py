"""Real Pokemon data for battles."""

POKEMON_DATA = {
    # Generation 1 starters and popular Pokemon
    "Pikachu": {
        "types": ["Electric"],
        "base_stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90},
        "moves": ["Thunderbolt", "Quick Attack", "Iron Tail", "Thunder Wave"]
    },
    "Charizard": {
        "types": ["Fire", "Flying"],
        "base_stats": {"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100},
        "moves": ["Flamethrower", "Air Slash", "Dragon Claw", "Fire Blast"]
    },
    "Blastoise": {
        "types": ["Water"],
        "base_stats": {"hp": 79, "atk": 83, "def": 100, "spa": 85, "spd": 105, "spe": 78},
        "moves": ["Surf", "Ice Beam", "Hydro Pump", "Aqua Tail"]
    },
    "Venusaur": {
        "types": ["Grass", "Poison"],
        "base_stats": {"hp": 80, "atk": 82, "def": 83, "spa": 100, "spd": 100, "spe": 80},
        "moves": ["Solar Beam", "Sludge Bomb", "Earthquake", "Energy Ball"]
    },
    "Gengar": {
        "types": ["Ghost", "Poison"],
        "base_stats": {"hp": 60, "atk": 65, "def": 60, "spa": 130, "spd": 75, "spe": 110},
        "moves": ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Focus Blast"]
    },
    "Alakazam": {
        "types": ["Psychic"],
        "base_stats": {"hp": 55, "atk": 50, "def": 45, "spa": 135, "spd": 95, "spe": 120},
        "moves": ["Psychic", "Shadow Ball", "Focus Blast", "Dazzling Gleam"]
    },
    "Machamp": {
        "types": ["Fighting"],
        "base_stats": {"hp": 90, "atk": 130, "def": 80, "spa": 65, "spd": 85, "spe": 55},
        "moves": ["Close Combat", "Stone Edge", "Earthquake", "Bullet Punch"]
    },
    "Gyarados": {
        "types": ["Water", "Flying"],
        "base_stats": {"hp": 95, "atk": 125, "def": 79, "spa": 60, "spd": 100, "spe": 81},
        "moves": ["Waterfall", "Earthquake", "Ice Fang", "Dragon Dance"]
    },
    "Dragonite": {
        "types": ["Dragon", "Flying"],
        "base_stats": {"hp": 91, "atk": 134, "def": 95, "spa": 100, "spd": 100, "spe": 80},
        "moves": ["Dragon Claw", "Earthquake", "Fire Punch", "Extreme Speed"]
    },
    "Tyranitar": {
        "types": ["Rock", "Dark"],
        "base_stats": {"hp": 100, "atk": 134, "def": 110, "spa": 95, "spd": 100, "spe": 61},
        "moves": ["Stone Edge", "Crunch", "Earthquake", "Ice Punch"]
    },
    "Garchomp": {
        "types": ["Dragon", "Ground"],
        "base_stats": {"hp": 108, "atk": 130, "def": 95, "spa": 80, "spd": 85, "spe": 102},
        "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Fire Fang"]
    },
    "Lucario": {
        "types": ["Fighting", "Steel"],
        "base_stats": {"hp": 70, "atk": 110, "def": 70, "spa": 115, "spd": 70, "spe": 90},
        "moves": ["Close Combat", "Flash Cannon", "Aura Sphere", "Extreme Speed"]
    },
    "Metagross": {
        "types": ["Steel", "Psychic"],
        "base_stats": {"hp": 80, "atk": 135, "def": 130, "spa": 95, "spd": 90, "spe": 70},
        "moves": ["Meteor Mash", "Earthquake", "Zen Headbutt", "Bullet Punch"]
    },
    "Salamence": {
        "types": ["Dragon", "Flying"],
        "base_stats": {"hp": 95, "atk": 135, "def": 80, "spa": 110, "spd": 80, "spe": 100},
        "moves": ["Dragon Claw", "Earthquake", "Fire Blast", "Fly"]
    },
    "Blaziken": {
        "types": ["Fire", "Fighting"],
        "base_stats": {"hp": 80, "atk": 120, "def": 70, "spa": 110, "spd": 70, "spe": 80},
        "moves": ["Flare Blitz", "Close Combat", "Stone Edge", "Earthquake"]
    },
    "Swampert": {
        "types": ["Water", "Ground"],
        "base_stats": {"hp": 100, "atk": 110, "def": 90, "spa": 85, "spd": 90, "spe": 60},
        "moves": ["Earthquake", "Waterfall", "Ice Punch", "Stone Edge"]
    },
    "Sceptile": {
        "types": ["Grass"],
        "base_stats": {"hp": 70, "atk": 85, "def": 65, "spa": 105, "spd": 85, "spe": 120},
        "moves": ["Leaf Blade", "Dragon Pulse", "Earthquake", "Focus Blast"]
    },
    "Aggron": {
        "types": ["Steel", "Rock"],
        "base_stats": {"hp": 70, "atk": 110, "def": 180, "spa": 60, "spd": 60, "spe": 50},
        "moves": ["Iron Head", "Stone Edge", "Earthquake", "Ice Punch"]
    },
}

MOVE_DATA = {
    # Electric moves
    "Thunderbolt": {"type": "Electric", "category": "Special", "power": 90, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "status": "par"}},
    "Thunder Wave": {"type": "Electric", "category": "Status", "power": 0, "accuracy": 90, "priority": 0, "secondary": {"chance": 100, "status": "par"}},
    
    # Fire moves
    "Flamethrower": {"type": "Fire", "category": "Special", "power": 90, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "status": "brn"}},
    "Fire Blast": {"type": "Fire", "category": "Special", "power": 110, "accuracy": 85, "priority": 0, "secondary": {"chance": 10, "status": "brn"}},
    "Flare Blitz": {"type": "Fire", "category": "Physical", "power": 120, "accuracy": 100, "priority": 0, "recoil": [33, 100], "secondary": {"chance": 10, "status": "brn"}},
    "Fire Punch": {"type": "Fire", "category": "Physical", "power": 75, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "status": "brn"}},
    "Fire Fang": {"type": "Fire", "category": "Physical", "power": 65, "accuracy": 95, "priority": 0, "secondary": {"chance": 10, "status": "brn"}},
    
    # Water moves
    "Surf": {"type": "Water", "category": "Special", "power": 90, "accuracy": 100, "priority": 0},
    "Hydro Pump": {"type": "Water", "category": "Special", "power": 110, "accuracy": 80, "priority": 0},
    "Waterfall": {"type": "Water", "category": "Physical", "power": 80, "accuracy": 100, "priority": 0, "secondary": {"chance": 20, "volatileStatus": "flinch"}},
    "Aqua Tail": {"type": "Water", "category": "Physical", "power": 90, "accuracy": 90, "priority": 0},
    
    # Grass moves
    "Solar Beam": {"type": "Grass", "category": "Special", "power": 120, "accuracy": 100, "priority": 0},
    "Energy Ball": {"type": "Grass", "category": "Special", "power": 90, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "boosts": {"spd": -1}}},
    "Leaf Blade": {"type": "Grass", "category": "Physical", "power": 90, "accuracy": 100, "priority": 0, "critRatio": 2},
    
    # Fighting moves
    "Close Combat": {"type": "Fighting", "category": "Physical", "power": 120, "accuracy": 100, "priority": 0, "self": {"boosts": {"def": -1, "spd": -1}}},
    "Aura Sphere": {"type": "Fighting", "category": "Special", "power": 80, "accuracy": 999, "priority": 0},
    "Focus Blast": {"type": "Fighting", "category": "Special", "power": 120, "accuracy": 70, "priority": 0, "secondary": {"chance": 10, "boosts": {"spd": -1}}},
    
    # Flying moves
    "Air Slash": {"type": "Flying", "category": "Special", "power": 75, "accuracy": 95, "priority": 0, "secondary": {"chance": 30, "volatileStatus": "flinch"}},
    "Fly": {"type": "Flying", "category": "Physical", "power": 90, "accuracy": 95, "priority": 0},
    
    # Psychic moves
    "Psychic": {"type": "Psychic", "category": "Special", "power": 90, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "boosts": {"spd": -1}}},
    "Zen Headbutt": {"type": "Psychic", "category": "Physical", "power": 80, "accuracy": 90, "priority": 0, "secondary": {"chance": 20, "volatileStatus": "flinch"}},
    
    # Ghost moves
    "Shadow Ball": {"type": "Ghost", "category": "Special", "power": 80, "accuracy": 100, "priority": 0, "secondary": {"chance": 20, "boosts": {"spd": -1}}},
    
    # Dragon moves
    "Dragon Claw": {"type": "Dragon", "category": "Physical", "power": 80, "accuracy": 100, "priority": 0},
    "Dragon Pulse": {"type": "Dragon", "category": "Special", "power": 85, "accuracy": 100, "priority": 0},
    
    # Dark moves
    "Crunch": {"type": "Dark", "category": "Physical", "power": 80, "accuracy": 100, "priority": 0, "secondary": {"chance": 20, "boosts": {"def": -1}}},
    
    # Steel moves
    "Iron Head": {"type": "Steel", "category": "Physical", "power": 80, "accuracy": 100, "priority": 0, "secondary": {"chance": 30, "volatileStatus": "flinch"}},
    "Iron Tail": {"type": "Steel", "category": "Physical", "power": 100, "accuracy": 75, "priority": 0, "secondary": {"chance": 30, "boosts": {"def": -1}}},
    "Flash Cannon": {"type": "Steel", "category": "Special", "power": 80, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "boosts": {"spd": -1}}},
    "Meteor Mash": {"type": "Steel", "category": "Physical", "power": 90, "accuracy": 90, "priority": 0, "secondary": {"chance": 20, "self": {"boosts": {"atk": 1}}}},
    "Bullet Punch": {"type": "Steel", "category": "Physical", "power": 40, "accuracy": 100, "priority": 1},
    
    # Ground moves
    "Earthquake": {"type": "Ground", "category": "Physical", "power": 100, "accuracy": 100, "priority": 0},
    
    # Rock moves
    "Stone Edge": {"type": "Rock", "category": "Physical", "power": 100, "accuracy": 80, "priority": 0, "critRatio": 2},
    
    # Ice moves
    "Ice Beam": {"type": "Ice", "category": "Special", "power": 90, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "status": "frz"}},
    "Ice Punch": {"type": "Ice", "category": "Physical", "power": 75, "accuracy": 100, "priority": 0, "secondary": {"chance": 10, "status": "frz"}},
    "Ice Fang": {"type": "Ice", "category": "Physical", "power": 65, "accuracy": 95, "priority": 0, "secondary": {"chance": 10, "status": "frz"}},
    
    # Poison moves
    "Sludge Bomb": {"type": "Poison", "category": "Special", "power": 90, "accuracy": 100, "priority": 0, "secondary": {"chance": 30, "status": "psn"}},
    
    # Fairy moves
    "Dazzling Gleam": {"type": "Fairy", "category": "Special", "power": 80, "accuracy": 100, "priority": 0},
    
    # Normal moves
    "Quick Attack": {"type": "Normal", "category": "Physical", "power": 40, "accuracy": 100, "priority": 1},
    "Extreme Speed": {"type": "Normal", "category": "Physical", "power": 80, "accuracy": 100, "priority": 2},
    "Dragon Dance": {"type": "Dragon", "category": "Status", "power": 0, "accuracy": 999, "priority": 0, "boosts": {"atk": 1, "spe": 1}},
}


def get_random_pokemon_team(num_pokemon=6):
    """Generate a random team of Pokemon."""
    import random
    available = list(POKEMON_DATA.keys())
    team_species = random.sample(available, min(num_pokemon, len(available)))
    return team_species


def create_pokemon_from_data(species_name, level=100):
    """Create a Pokemon instance from data."""
    from ..data.models import Pokemon
    
    if species_name not in POKEMON_DATA:
        raise ValueError(f"Unknown Pokemon: {species_name}")
    
    data = POKEMON_DATA[species_name]
    base_stats = data["base_stats"]
    
    # Calculate actual stats (simplified formula for level 100)
    hp = int((2 * base_stats["hp"] + 100) * level / 100 + level + 10)
    stats = {
        "atk": int((2 * base_stats["atk"] + 100) * level / 100 + 5),
        "def": int((2 * base_stats["def"] + 100) * level / 100 + 5),
        "spa": int((2 * base_stats["spa"] + 100) * level / 100 + 5),
        "spd": int((2 * base_stats["spd"] + 100) * level / 100 + 5),
        "spe": int((2 * base_stats["spe"] + 100) * level / 100 + 5),
    }
    
    return Pokemon(
        species=species_name,
        level=level,
        types=data["types"],
        hp=hp,
        max_hp=hp,
        stats=stats,
        moves=data["moves"]
    )


def get_move_data(move_name):
    """Get move data."""
    from ..data.models import Move
    
    if move_name not in MOVE_DATA:
        # Return a default move if not found
        return Move(
            name=move_name,
            type="Normal",
            category="Physical",
            power=50,
            accuracy=100,
            priority=0
        )
    
    data = MOVE_DATA[move_name]
    move_dict = {
        "name": move_name,
        "type": data["type"],
        "category": data["category"],
        "power": data.get("power"),
        "accuracy": data["accuracy"],
        "priority": data["priority"]
    }
    
    # Add secondary effects if they exist
    if "secondary" in data:
        move_dict["secondary"] = data["secondary"]
    if "self" in data:
        if "secondary" not in move_dict:
            move_dict["secondary"] = {}
        move_dict["secondary"]["self"] = data["self"]
    if "boosts" in data:
        move_dict["secondary"] = {"boosts": data["boosts"], "self": True}
    if "recoil" in data:
        if "secondary" not in move_dict:
            move_dict["secondary"] = {}
        move_dict["secondary"]["recoil"] = data["recoil"]
    if "critRatio" in data:
        if "flags" not in move_dict:
            move_dict["flags"] = {}
        move_dict["flags"]["highCritRatio"] = True
    
    return Move(**move_dict)
