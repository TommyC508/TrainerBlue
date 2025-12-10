"""Data models for Pokemon, moves, abilities, and items."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class StatName(str, Enum):
    """Stat names."""
    HP = "hp"
    ATK = "atk"
    DEF = "def"
    SPA = "spa"
    SPD = "spd"
    SPE = "spe"


class MoveCategory(str, Enum):
    """Move categories."""
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    STATUS = "Status"


class PokemonType(str, Enum):
    """Pokemon types."""
    NORMAL = "Normal"
    FIRE = "Fire"
    WATER = "Water"
    ELECTRIC = "Electric"
    GRASS = "Grass"
    ICE = "Ice"
    FIGHTING = "Fighting"
    POISON = "Poison"
    GROUND = "Ground"
    FLYING = "Flying"
    PSYCHIC = "Psychic"
    BUG = "Bug"
    ROCK = "Rock"
    GHOST = "Ghost"
    DRAGON = "Dragon"
    DARK = "Dark"
    STEEL = "Steel"
    FAIRY = "Fairy"


class StatusCondition(str, Enum):
    """Status conditions."""
    HEALTHY = ""
    BURN = "brn"
    FREEZE = "frz"
    PARALYSIS = "par"
    POISON = "psn"
    TOXIC = "tox"
    SLEEP = "slp"
    FAINT = "fnt"


class Weather(str, Enum):
    """Weather conditions."""
    NONE = ""
    SUN = "sunnyday"
    RAIN = "raindance"
    SANDSTORM = "sandstorm"
    HAIL = "hail"
    SNOW = "snow"
    HARSH_SUNSHINE = "desolateland"
    HEAVY_RAIN = "primordialsea"
    STRONG_WINDS = "deltastream"


class Terrain(str, Enum):
    """Terrain conditions."""
    NONE = ""
    ELECTRIC = "electricterrain"
    GRASSY = "grassyterrain"
    MISTY = "mistyterrain"
    PSYCHIC = "psychicterrain"


class PokemonSpecies(BaseModel):
    """Pokemon species data."""
    name: str
    types: List[str]
    base_stats: Dict[str, int] = Field(default_factory=dict)
    abilities: List[str] = Field(default_factory=list)
    height_m: float = 0.0
    weight_kg: float = 0.0
    
    class Config:
        use_enum_values = True


class Move(BaseModel):
    """Move data."""
    name: str
    type: str
    category: str  # Physical, Special, Status
    power: Optional[int] = None
    accuracy: Optional[int] = None
    pp: int = 1
    priority: int = 0
    flags: Dict[str, bool] = Field(default_factory=dict)
    secondary: Optional[Dict[str, Any]] = None
    target: str = "normal"
    
    class Config:
        use_enum_values = True


class Ability(BaseModel):
    """Ability data."""
    name: str
    description: str = ""
    
    class Config:
        use_enum_values = True


class Item(BaseModel):
    """Item data."""
    name: str
    description: str = ""
    
    class Config:
        use_enum_values = True


class Pokemon(BaseModel):
    """Pokemon in battle."""
    species: str
    level: int = 100
    gender: Optional[str] = None
    shiny: bool = False
    
    # Types
    types: List[str] = Field(default_factory=lambda: ["Normal"])
    
    # Battle state
    hp: int = 100
    max_hp: int = 100
    status: str = ""  # brn, par, psn, tox, slp, frz, fnt
    
    # Stats (actual calculated stats)
    stats: Dict[str, int] = Field(default_factory=lambda: {
        "atk": 100, "def": 100, "spa": 100, "spd": 100, "spe": 100
    })
    
    # Stat boosts (-6 to +6)
    boosts: Dict[str, int] = Field(default_factory=lambda: {
        "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0, "accuracy": 0, "evasion": 0
    })
    
    # Moves, ability, item
    moves: List[str] = Field(default_factory=list)
    ability: Optional[str] = None
    item: Optional[str] = None
    base_ability: Optional[str] = None  # Original ability before transform
    
    # Volatile status
    volatile_status: List[str] = Field(default_factory=list)
    
    # Tracking
    active: bool = False
    fainted: bool = False
    turns_asleep: int = 0
    
    @property
    def hp_percent(self) -> float:
        """Get HP as percentage."""
        if self.max_hp == 0:
            return 0.0
        return (self.hp / self.max_hp) * 100
    
    def is_alive(self) -> bool:
        """Check if Pokemon is alive."""
        return not self.fainted and self.hp > 0
    
    def can_move(self) -> bool:
        """Check if Pokemon can move this turn."""
        if not self.is_alive():
            return False
        if self.status == "slp":
            # Simplified: assume can't move if asleep
            return False
        if self.status == "frz":
            # Simplified: assume can't move if frozen
            return False
        return True
    
    class Config:
        use_enum_values = True


class Side(BaseModel):
    """One side of the battle (player's team)."""
    player_id: str  # "p1" or "p2"
    username: str = ""
    team: List[Pokemon] = Field(default_factory=list)
    active_pokemon: List[int] = Field(default_factory=list)  # Indices of active Pokemon
    
    # Side conditions
    spikes: int = 0
    toxic_spikes: int = 0
    stealth_rock: bool = False
    sticky_web: bool = False
    light_screen: int = 0
    reflect: int = 0
    aurora_veil: int = 0
    tailwind: int = 0
    
    def get_active_pokemon(self) -> List[Pokemon]:
        """Get active Pokemon."""
        return [self.team[i] for i in self.active_pokemon if i < len(self.team)]
    
    def get_alive_pokemon(self) -> List[Pokemon]:
        """Get all alive Pokemon."""
        return [p for p in self.team if p.is_alive()]
    
    def count_alive(self) -> int:
        """Count alive Pokemon."""
        return len(self.get_alive_pokemon())
    
    class Config:
        use_enum_values = True


class Field(BaseModel):
    """Field conditions."""
    weather: str = ""
    terrain: str = ""
    trick_room: bool = False
    gravity: bool = False
    magic_room: bool = False
    wonder_room: bool = False
    
    class Config:
        use_enum_values = True
