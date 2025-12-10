"""Battle state management."""
from typing import List, Optional, Dict, Any
import logging
from ..data.models import Pokemon, Side, Field
from ..connection.protocol import Action
from ..connection.message_parser import MessageParser

logger = logging.getLogger(__name__)


class BattleState:
    """Complete battle state representation."""
    
    def __init__(self, our_player_id: str = "p1"):
        """
        Initialize battle state.
        
        Args:
            our_player_id: Our player ID ("p1" or "p2")
        """
        self.our_player_id = our_player_id
        self.opponent_player_id = "p2" if our_player_id == "p1" else "p1"
        
        # Sides
        self.our_side = Side(player_id=our_player_id)
        self.opponent_side = Side(player_id=self.opponent_player_id)
        
        # Field
        self.field = Field()
        
        # Battle info
        self.turn = 0
        self.started = False
        self.finished = False
        self.winner: Optional[str] = None
        self.format = "unknown"
        self.rated = False
        
        # Request data (contains available actions)
        self.current_request: Optional[Dict[str, Any]] = None
        
        # Parser
        self.parser = MessageParser()
    
    def update(self, line: str):
        """
        Update state based on a battle log line.
        
        Args:
            line: Single line from battle log
        """
        parsed = self.parser.parse_battle_line(line)
        msg_type = parsed.get("type")
        
        try:
            if msg_type == "player":
                self._handle_player(parsed)
            elif msg_type == "teamsize":
                self._handle_teamsize(parsed)
            elif msg_type == "gametype":
                self.format = parsed.get("gametype", "unknown")
            elif msg_type == "gen":
                pass  # Generation info
            elif msg_type == "tier":
                self.format = parsed.get("tier", "unknown")
            elif msg_type == "rated":
                self.rated = True
            elif msg_type == "poke":
                self._handle_poke(parsed)
            elif msg_type == "teampreview":
                pass  # Team preview started
            elif msg_type == "start":
                self.started = True
                logger.info("Battle started!")
            elif msg_type == "turn":
                self.turn = parsed.get("turn_number", 0)
                logger.debug(f"Turn {self.turn}")
            elif msg_type == "switch" or msg_type == "drag":
                self._handle_switch(parsed)
            elif msg_type == "faint":
                self._handle_faint(parsed)
            elif msg_type == "damage":
                self._handle_damage(parsed)
            elif msg_type == "heal":
                self._handle_heal(parsed)
            elif msg_type == "status":
                self._handle_status(parsed)
            elif msg_type == "curestatus":
                self._handle_curestatus(parsed)
            elif msg_type == "boost":
                self._handle_boost(parsed)
            elif msg_type == "unboost":
                self._handle_unboost(parsed)
            elif msg_type == "weather":
                self._handle_weather(parsed)
            elif msg_type == "fieldstart":
                self._handle_field_start(parsed)
            elif msg_type == "fieldend":
                self._handle_field_end(parsed)
            elif msg_type == "sidestart":
                self._handle_side_start(parsed)
            elif msg_type == "sideend":
                self._handle_side_end(parsed)
            elif msg_type == "win":
                self._handle_win(parsed)
            elif msg_type == "tie":
                self._handle_tie()
            elif msg_type == "request":
                self._handle_request(parsed)
        except Exception as e:
            logger.error(f"Error handling message type {msg_type}: {e}", exc_info=True)
    
    def _handle_player(self, parsed: Dict[str, Any]):
        """Handle player message."""
        player_id = parsed.get("player_id")
        username = parsed.get("username", "")
        
        if player_id == self.our_player_id:
            self.our_side.username = username
        else:
            self.opponent_side.username = username
    
    def _handle_teamsize(self, parsed: Dict[str, Any]):
        """Handle team size message."""
        player_id = parsed.get("player_id")
        size = parsed.get("size", 0)
        
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        # Initialize team with placeholder Pokemon
        side.team = [
            Pokemon(species=f"Unknown{i+1}", level=100, hp=0, max_hp=100)
            for i in range(size)
        ]
    
    def _handle_poke(self, parsed: Dict[str, Any]):
        """Handle poke message (team preview)."""
        player_id = parsed.get("player_id")
        details = parsed.get("details", "")
        has_item = parsed.get("item", False)
        
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        # Parse Pokemon details
        poke_info = self.parser.parse_pokemon_details(details)
        
        # Add to team (find first unknown slot)
        for i, pokemon in enumerate(side.team):
            if pokemon.species.startswith("Unknown"):
                side.team[i] = Pokemon(
                    species=poke_info["species"],
                    level=poke_info["level"],
                    gender=poke_info["gender"],
                    shiny=poke_info["shiny"],
                    hp=100,
                    max_hp=100,
                )
                break
    
    def _handle_switch(self, parsed: Dict[str, Any]):
        """Handle switch/drag message."""
        pokemon_str = parsed.get("pokemon", "")
        details = parsed.get("details", "")
        hp_status = parsed.get("hp_status", "")
        
        # Parse which Pokemon switched in
        player_id, position = self._parse_pokemon_identifier(pokemon_str)
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        # Parse details
        poke_info = self.parser.parse_pokemon_details(details)
        hp_info = self.parser.parse_hp_status(hp_status) if hp_status else {}
        
        # Update Pokemon at position
        if position < len(side.team):
            pokemon = side.team[position]
            pokemon.species = poke_info["species"]
            pokemon.level = poke_info["level"]
            pokemon.gender = poke_info.get("gender")
            pokemon.active = True
            pokemon.fainted = False
            
            if hp_info:
                pokemon.hp = hp_info.get("hp", 100)
                pokemon.max_hp = hp_info.get("max_hp", 100)
                pokemon.status = hp_info.get("status", "")
            
            # Update active Pokemon list
            if position not in side.active_pokemon:
                side.active_pokemon = [position]
    
    def _handle_faint(self, parsed: Dict[str, Any]):
        """Handle faint message."""
        pokemon_str = parsed.get("pokemon", "")
        player_id, position = self._parse_pokemon_identifier(pokemon_str)
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if position < len(side.team):
            pokemon = side.team[position]
            pokemon.fainted = True
            pokemon.hp = 0
            pokemon.active = False
            logger.info(f"{pokemon.species} fainted!")
    
    def _handle_damage(self, parsed: Dict[str, Any]):
        """Handle damage message."""
        pokemon_str = parsed.get("pokemon", "")
        hp_status = parsed.get("hp_status", "")
        
        player_id, position = self._parse_pokemon_identifier(pokemon_str)
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if position < len(side.team) and hp_status:
            pokemon = side.team[position]
            hp_info = self.parser.parse_hp_status(hp_status)
            pokemon.hp = hp_info.get("hp", pokemon.hp)
            pokemon.max_hp = hp_info.get("max_hp", pokemon.max_hp)
            if hp_info.get("status"):
                pokemon.status = hp_info["status"]
    
    def _handle_heal(self, parsed: Dict[str, Any]):
        """Handle heal message."""
        self._handle_damage(parsed)  # Same logic
    
    def _handle_status(self, parsed: Dict[str, Any]):
        """Handle status message."""
        pokemon_str = parsed.get("pokemon", "")
        status = parsed.get("status", "")
        
        player_id, position = self._parse_pokemon_identifier(pokemon_str)
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if position < len(side.team):
            pokemon = side.team[position]
            pokemon.status = status
    
    def _handle_curestatus(self, parsed: Dict[str, Any]):
        """Handle cure status message."""
        pokemon_str = parsed.get("pokemon", "")
        
        player_id, position = self._parse_pokemon_identifier(pokemon_str)
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if position < len(side.team):
            pokemon = side.team[position]
            pokemon.status = ""
    
    def _handle_boost(self, parsed: Dict[str, Any]):
        """Handle boost message."""
        pokemon_str = parsed.get("pokemon", "")
        stat = parsed.get("stat", "")
        amount = parsed.get("amount", 0)
        
        player_id, position = self._parse_pokemon_identifier(pokemon_str)
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if position < len(side.team) and stat in side.team[position].boosts:
            pokemon = side.team[position]
            pokemon.boosts[stat] = min(6, pokemon.boosts.get(stat, 0) + amount)
    
    def _handle_unboost(self, parsed: Dict[str, Any]):
        """Handle unboost message."""
        pokemon_str = parsed.get("pokemon", "")
        stat = parsed.get("stat", "")
        amount = parsed.get("amount", 0)
        
        player_id, position = self._parse_pokemon_identifier(pokemon_str)
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if position < len(side.team) and stat in side.team[position].boosts:
            pokemon = side.team[position]
            pokemon.boosts[stat] = max(-6, pokemon.boosts.get(stat, 0) - amount)
    
    def _handle_weather(self, parsed: Dict[str, Any]):
        """Handle weather message."""
        weather = parsed.get("weather", "")
        if weather == "none":
            self.field.weather = ""
        else:
            self.field.weather = weather
    
    def _handle_field_start(self, parsed: Dict[str, Any]):
        """Handle field start message."""
        condition = parsed.get("condition", "")
        
        if "Trick Room" in condition:
            self.field.trick_room = True
        elif "Gravity" in condition:
            self.field.gravity = True
        elif "terrain" in condition.lower():
            self.field.terrain = condition.lower().replace("move: ", "")
    
    def _handle_field_end(self, parsed: Dict[str, Any]):
        """Handle field end message."""
        condition = parsed.get("condition", "")
        
        if "Trick Room" in condition:
            self.field.trick_room = False
        elif "Gravity" in condition:
            self.field.gravity = False
        elif "terrain" in condition.lower():
            self.field.terrain = ""
    
    def _handle_side_start(self, parsed: Dict[str, Any]):
        """Handle side start message (hazards, screens, etc.)."""
        player_id = parsed.get("player_id")
        condition = parsed.get("condition", "")
        
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if "Spikes" in condition:
            side.spikes = min(3, side.spikes + 1)
        elif "Toxic Spikes" in condition:
            side.toxic_spikes = min(2, side.toxic_spikes + 1)
        elif "Stealth Rock" in condition:
            side.stealth_rock = True
        elif "Sticky Web" in condition:
            side.sticky_web = True
        elif "Light Screen" in condition:
            side.light_screen = 5
        elif "Reflect" in condition:
            side.reflect = 5
        elif "Aurora Veil" in condition:
            side.aurora_veil = 5
        elif "Tailwind" in condition:
            side.tailwind = 4
    
    def _handle_side_end(self, parsed: Dict[str, Any]):
        """Handle side end message."""
        player_id = parsed.get("player_id")
        condition = parsed.get("condition", "")
        
        side = self.our_side if player_id == self.our_player_id else self.opponent_side
        
        if "Spikes" in condition:
            side.spikes = 0
        elif "Toxic Spikes" in condition:
            side.toxic_spikes = 0
        elif "Stealth Rock" in condition:
            side.stealth_rock = False
        elif "Sticky Web" in condition:
            side.sticky_web = False
    
    def _handle_win(self, parsed: Dict[str, Any]):
        """Handle win message."""
        winner = parsed.get("winner", "")
        self.finished = True
        self.winner = winner
        logger.info(f"Battle finished! Winner: {winner}")
    
    def _handle_tie(self):
        """Handle tie message."""
        self.finished = True
        self.winner = "tie"
        logger.info("Battle finished in a tie!")
    
    def _handle_request(self, parsed: Dict[str, Any]):
        """Handle request message (contains available actions)."""
        request_json = parsed.get("request_json")
        if request_json:
            self.current_request = self.parser.parse_request(request_json)
            
            # Update our team with request data
            if self.current_request and "side" in self.current_request:
                self._update_from_request(self.current_request)
    
    def _update_from_request(self, request: Dict[str, Any]):
        """Update our side from request data."""
        side_data = request.get("side", {})
        pokemon_data = side_data.get("pokemon", [])
        
        for i, poke_data in enumerate(pokemon_data):
            if i >= len(self.our_side.team):
                continue
            
            pokemon = self.our_side.team[i]
            
            # Update details
            details = poke_data.get("details", "")
            if details:
                poke_info = self.parser.parse_pokemon_details(details)
                pokemon.species = poke_info["species"]
                pokemon.level = poke_info["level"]
            
            # Update condition (HP/status)
            condition = poke_data.get("condition", "")
            if condition:
                hp_info = self.parser.parse_hp_status(condition)
                pokemon.hp = hp_info.get("hp", pokemon.hp)
                pokemon.max_hp = hp_info.get("max_hp", pokemon.max_hp)
                pokemon.status = hp_info.get("status", "")
                pokemon.fainted = (pokemon.hp == 0)
            
            # Update active status
            pokemon.active = poke_data.get("active", False)
            
            # Update stats
            if "stats" in poke_data:
                pokemon.stats = poke_data["stats"]
            
            # Update moves
            if "moves" in poke_data:
                pokemon.moves = poke_data["moves"]
            
            # Update ability and item
            if "ability" in poke_data:
                pokemon.ability = poke_data["ability"]
            if "item" in poke_data:
                pokemon.item = poke_data["item"]
    
    def _parse_pokemon_identifier(self, pokemon_str: str) -> tuple:
        """
        Parse Pokemon identifier string.
        
        Format: "p1a: Pikachu" or "p2a: Charizard"
        
        Returns:
            (player_id, position) tuple
        """
        parts = pokemon_str.split(":")
        if len(parts) < 1:
            return ("p1", 0)
        
        identifier = parts[0].strip()
        player_id = identifier[:2]  # "p1" or "p2"
        position_letter = identifier[2:3] if len(identifier) > 2 else "a"
        
        # Convert letter to position (a=0, b=1, c=2, etc.)
        position = ord(position_letter.lower()) - ord('a') if position_letter else 0
        
        return (player_id, position)
    
    def get_legal_actions(self) -> List[Action]:
        """
        Get list of legal actions for current turn.
        
        Returns:
            List of Action objects
        """
        if not self.current_request:
            return []
        
        actions = []
        
        # Check if we can make moves
        if "active" in self.current_request:
            active_data = self.current_request["active"][0]  # First active Pokemon
            
            # Add move actions
            if "moves" in active_data:
                for i, move in enumerate(active_data["moves"], 1):
                    if not move.get("disabled", False):
                        actions.append(Action(type="move", value=str(i)))
            
            # Check if we can switch
            if not active_data.get("trapped", False):
                # Add switch actions
                if "side" in self.current_request:
                    pokemon_list = self.current_request["side"].get("pokemon", [])
                    for i, poke in enumerate(pokemon_list, 1):
                        # Can switch if not active and not fainted
                        if not poke.get("active", False) and poke.get("condition", "").split()[0] != "0":
                            actions.append(Action(type="switch", value=str(i)))
        
        # Team preview
        if "forceSwitch" in self.current_request or self.current_request.get("wait"):
            # Team preview or forced switch
            pass
        
        return actions
    
    def get_our_active_pokemon(self) -> Optional[Pokemon]:
        """Get our currently active Pokemon."""
        if self.our_side.active_pokemon:
            idx = self.our_side.active_pokemon[0]
            if idx < len(self.our_side.team):
                return self.our_side.team[idx]
        return None
    
    def get_opponent_active_pokemon(self) -> Optional[Pokemon]:
        """Get opponent's currently active Pokemon."""
        if self.opponent_side.active_pokemon:
            idx = self.opponent_side.active_pokemon[0]
            if idx < len(self.opponent_side.team):
                return self.opponent_side.team[idx]
        return None
