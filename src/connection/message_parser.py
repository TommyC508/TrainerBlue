"""Message parser for Pokemon Showdown protocol."""
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MessageParser:
    """Parse Pokemon Showdown protocol messages."""
    
    @staticmethod
    def parse_request(request_data: str) -> Optional[Dict[str, Any]]:
        """
        Parse a request message (contains battle state and available actions).
        
        Args:
            request_data: JSON string from |request| message
            
        Returns:
            Parsed request dictionary or None if invalid
        """
        try:
            data = json.loads(request_data)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse request: {e}")
            return None
    
    @staticmethod
    def parse_battle_line(line: str) -> Dict[str, Any]:
        """
        Parse a single battle log line.
        
        Args:
            line: Single line from battle log
            
        Returns:
            Dictionary with parsed information
        """
        parts = line.split("|")
        
        if len(parts) < 2:
            return {"type": "unknown", "raw": line}
        
        msg_type = parts[1]
        
        # Parse different message types
        if msg_type == "player":
            return {
                "type": "player",
                "player_id": parts[2],
                "username": parts[3],
                "avatar": parts[4] if len(parts) > 4 else None,
                "rating": parts[5] if len(parts) > 5 else None,
            }
        
        elif msg_type == "teamsize":
            return {
                "type": "teamsize",
                "player_id": parts[2],
                "size": int(parts[3]),
            }
        
        elif msg_type == "gametype":
            return {
                "type": "gametype",
                "gametype": parts[2],
            }
        
        elif msg_type == "gen":
            return {
                "type": "gen",
                "gen": int(parts[2]),
            }
        
        elif msg_type == "tier":
            return {
                "type": "tier",
                "tier": parts[2],
            }
        
        elif msg_type == "rated":
            return {
                "type": "rated",
                "rated": parts[2] if len(parts) > 2 else True,
            }
        
        elif msg_type == "rule":
            return {
                "type": "rule",
                "rule": parts[2],
                "description": parts[3] if len(parts) > 3 else None,
            }
        
        elif msg_type == "clearpoke":
            return {
                "type": "clearpoke",
            }
        
        elif msg_type == "poke":
            return {
                "type": "poke",
                "player_id": parts[2],
                "details": parts[3],
                "item": parts[4] == "item" if len(parts) > 4 else False,
            }
        
        elif msg_type == "teampreview":
            return {
                "type": "teampreview",
                "seconds": int(parts[2]) if len(parts) > 2 else None,
            }
        
        elif msg_type == "start":
            return {
                "type": "start",
            }
        
        elif msg_type == "turn":
            return {
                "type": "turn",
                "turn_number": int(parts[2]),
            }
        
        elif msg_type == "move":
            return {
                "type": "move",
                "pokemon": parts[2],
                "move": parts[3],
                "target": parts[4] if len(parts) > 4 else None,
            }
        
        elif msg_type in ["switch", "drag"]:
            return {
                "type": msg_type,
                "pokemon": parts[2],
                "details": parts[3],
                "hp_status": parts[4] if len(parts) > 4 else None,
            }
        
        elif msg_type == "faint":
            return {
                "type": "faint",
                "pokemon": parts[2],
            }
        
        elif msg_type == "-damage":
            return {
                "type": "damage",
                "pokemon": parts[2],
                "hp_status": parts[3],
                "from": parts[4] if len(parts) > 4 and parts[4].startswith("[from]") else None,
            }
        
        elif msg_type == "-heal":
            return {
                "type": "heal",
                "pokemon": parts[2],
                "hp_status": parts[3],
                "from": parts[4] if len(parts) > 4 and parts[4].startswith("[from]") else None,
            }
        
        elif msg_type == "-status":
            return {
                "type": "status",
                "pokemon": parts[2],
                "status": parts[3],
            }
        
        elif msg_type == "-curestatus":
            return {
                "type": "curestatus",
                "pokemon": parts[2],
                "status": parts[3],
            }
        
        elif msg_type == "-boost":
            return {
                "type": "boost",
                "pokemon": parts[2],
                "stat": parts[3],
                "amount": int(parts[4]),
            }
        
        elif msg_type == "-unboost":
            return {
                "type": "unboost",
                "pokemon": parts[2],
                "stat": parts[3],
                "amount": int(parts[4]),
            }
        
        elif msg_type == "-weather":
            return {
                "type": "weather",
                "weather": parts[2],
            }
        
        elif msg_type in ["-fieldstart", "-fieldend"]:
            return {
                "type": msg_type[1:],  # Remove leading dash
                "condition": parts[2],
            }
        
        elif msg_type in ["-sidestart", "-sideend"]:
            return {
                "type": msg_type[1:],
                "player_id": parts[2],
                "condition": parts[3],
            }
        
        elif msg_type in ["-start", "-end"]:
            return {
                "type": "volatile" + msg_type,  # volatilestart, volatileend
                "pokemon": parts[2],
                "effect": parts[3],
            }
        
        elif msg_type == "-supereffective":
            return {
                "type": "supereffective",
                "pokemon": parts[2],
            }
        
        elif msg_type == "-resisted":
            return {
                "type": "resisted",
                "pokemon": parts[2],
            }
        
        elif msg_type == "-immune":
            return {
                "type": "immune",
                "pokemon": parts[2],
            }
        
        elif msg_type == "-crit":
            return {
                "type": "crit",
                "pokemon": parts[2],
            }
        
        elif msg_type == "win":
            return {
                "type": "win",
                "winner": parts[2],
            }
        
        elif msg_type == "tie":
            return {
                "type": "tie",
            }
        
        elif msg_type == "request":
            return {
                "type": "request",
                "request_json": parts[2] if len(parts) > 2 else None,
            }
        
        elif msg_type == "":
            # Empty message type, might be a text message
            return {
                "type": "message",
                "text": "|".join(parts[2:]),
            }
        
        else:
            # Unknown message type, return raw
            return {
                "type": msg_type,
                "raw": line,
                "parts": parts[2:],
            }
    
    @staticmethod
    def parse_pokemon_details(details: str) -> Dict[str, Any]:
        """
        Parse Pokemon details string.
        
        Format: "Pikachu, L50" or "Pikachu, L50, M" or "Charizard, L100, F"
        
        Args:
            details: Pokemon details string
            
        Returns:
            Dictionary with species, level, gender, shiny
        """
        parts = [p.strip() for p in details.split(",")]
        
        species = parts[0]
        level = 100  # Default level
        gender = None
        shiny = False
        
        for part in parts[1:]:
            if part.startswith("L"):
                level = int(part[1:])
            elif part in ["M", "F"]:
                gender = part
            elif part == "shiny":
                shiny = True
        
        return {
            "species": species,
            "level": level,
            "gender": gender,
            "shiny": shiny,
        }
    
    @staticmethod
    def parse_hp_status(hp_status: str) -> Dict[str, Any]:
        """
        Parse HP and status string.
        
        Format: "100/100" or "50/100 par" or "0 fnt"
        
        Args:
            hp_status: HP/status string
            
        Returns:
            Dictionary with hp, max_hp, status
        """
        parts = hp_status.split()
        hp_part = parts[0]
        status = parts[1] if len(parts) > 1 else None
        
        if hp_part == "0":
            return {
                "hp": 0,
                "max_hp": 0,
                "hp_percent": 0,
                "status": "fnt",
            }
        
        if "/" in hp_part:
            hp, max_hp = hp_part.split("/")
            hp = int(hp)
            max_hp = int(max_hp)
            hp_percent = (hp / max_hp * 100) if max_hp > 0 else 0
        else:
            # Percentage format (used in some situations)
            hp_percent = int(hp_part)
            hp = hp_percent
            max_hp = 100
        
        return {
            "hp": hp,
            "max_hp": max_hp,
            "hp_percent": hp_percent,
            "status": status,
        }
