"""Protocol constants and types for Pokemon Showdown."""
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class MessageType(Enum):
    """Types of messages from Pokemon Showdown."""
    CHALLENGE_STRINGS = "challstr"
    UPDATE_USER = "updateuser"
    FORMATS = "formats"
    UPDATE_SEARCH = "updatesearch"
    BATTLE_INIT = "init"
    BATTLE_TITLE = "title"
    PLAYER = "player"
    TEAM_SIZE = "teamsize"
    GAME_TYPE = "gametype"
    GEN = "gen"
    TIER = "tier"
    RATED = "rated"
    RULE = "rule"
    CLEAR_POKE = "clearpoke"
    POKE = "poke"
    TEAM_PREVIEW = "teampreview"
    START = "start"
    REQUEST = "request"
    INACTIVE = "inactive"
    INACTIVE_OFF = "inactiveoff"
    UPKEEP = "upkeep"
    TURN = "turn"
    WIN = "win"
    TIE = "tie"
    MOVE = "move"
    SWITCH = "switch"
    DRAG = "drag"
    DETAIL_CHANGE = "detailchange"
    CANT = "cant"
    FAINT = "faint"
    DAMAGE = "-damage"
    HEAL = "-heal"
    STATUS = "-status"
    CURE_STATUS = "-curestatus"
    BOOST = "-boost"
    UNBOOST = "-unboost"
    WEATHER = "-weather"
    FIELD_START = "-fieldstart"
    FIELD_END = "-fieldend"
    SIDE_START = "-sidestart"
    SIDE_END = "-sideend"
    VOLATILE_START = "-start"
    VOLATILE_END = "-end"
    CRIT = "-crit"
    SUPEREFFECTIVE = "-supereffective"
    RESISTED = "-resisted"
    IMMUNE = "-immune"
    ITEM = "-item"
    END_ITEM = "-enditem"
    ABILITY = "-ability"
    END_ABILITY = "-endability"
    TRANSFORM = "-transform"
    MEGA = "-mega"
    PRIMAL = "-primal"
    BURST = "-burst"
    Z_POWER = "-zpower"
    Z_BROKEN = "-zbroken"
    ACTIVATE = "-activate"
    HINT = "-hint"
    CENTER = "-center"
    MESSAGE = "-message"
    COMBINE = "-combine"
    WAITING = "-waiting"
    PREPARE = "-prepare"
    MUST_RECHARGE = "-mustrecharge"
    NOTHING = "-nothing"
    HITCOUNT = "-hitcount"
    SINGLE_MOVE = "-singlemove"
    SINGLE_TURN = "-singleturn"
    

class Action(BaseModel):
    """Represents an action to send to Pokemon Showdown."""
    type: str  # "move", "switch", "team", "default"
    value: Optional[str] = None  # Move index, switch index, or team order
    
    def to_showdown_format(self) -> str:
        """Convert action to Pokemon Showdown protocol format."""
        if self.type == "move":
            return f"/choose move {self.value}"
        elif self.type == "switch":
            return f"/choose switch {self.value}"
        elif self.type == "team":
            return f"/choose team {self.value}"
        elif self.type == "default":
            return "/choose default"
        else:
            raise ValueError(f"Unknown action type: {self.type}")


class BattleMessage(BaseModel):
    """Base class for parsed battle messages."""
    room_id: str
    raw: str
