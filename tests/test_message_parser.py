"""Tests for message parser."""
import pytest
from src.connection.message_parser import MessageParser


def test_parse_player():
    """Test parsing player message."""
    parser = MessageParser()
    line = "|player|p1|TestUser|1|1500"
    
    result = parser.parse_battle_line(line)
    
    assert result["type"] == "player"
    assert result["player_id"] == "p1"
    assert result["username"] == "TestUser"
    assert result["avatar"] == "1"
    assert result["rating"] == "1500"


def test_parse_pokemon_details():
    """Test parsing Pokemon details."""
    parser = MessageParser()
    
    # Basic details
    result = parser.parse_pokemon_details("Pikachu, L50")
    assert result["species"] == "Pikachu"
    assert result["level"] == 50
    assert result["gender"] is None
    
    # With gender
    result = parser.parse_pokemon_details("Charizard, L100, M")
    assert result["species"] == "Charizard"
    assert result["level"] == 100
    assert result["gender"] == "M"
    
    # Female
    result = parser.parse_pokemon_details("Pikachu, L25, F")
    assert result["gender"] == "F"


def test_parse_hp_status():
    """Test parsing HP/status string."""
    parser = MessageParser()
    
    # Full HP
    result = parser.parse_hp_status("100/100")
    assert result["hp"] == 100
    assert result["max_hp"] == 100
    assert result["hp_percent"] == 100.0
    assert result["status"] is None
    
    # Damaged
    result = parser.parse_hp_status("50/100")
    assert result["hp"] == 50
    assert result["hp_percent"] == 50.0
    
    # With status
    result = parser.parse_hp_status("75/100 par")
    assert result["hp"] == 75
    assert result["status"] == "par"
    
    # Fainted
    result = parser.parse_hp_status("0 fnt")
    assert result["hp"] == 0
    assert result["status"] == "fnt"


def test_parse_move():
    """Test parsing move message."""
    parser = MessageParser()
    line = "|move|p1a: Pikachu|Thunderbolt|p2a: Charizard"
    
    result = parser.parse_battle_line(line)
    
    assert result["type"] == "move"
    assert result["pokemon"] == "p1a: Pikachu"
    assert result["move"] == "Thunderbolt"
    assert result["target"] == "p2a: Charizard"


def test_parse_switch():
    """Test parsing switch message."""
    parser = MessageParser()
    line = "|switch|p1a: Pikachu|Pikachu, L50, M|100/100"
    
    result = parser.parse_battle_line(line)
    
    assert result["type"] == "switch"
    assert result["pokemon"] == "p1a: Pikachu"
    assert result["details"] == "Pikachu, L50, M"
    assert result["hp_status"] == "100/100"


def test_parse_damage():
    """Test parsing damage message."""
    parser = MessageParser()
    line = "|-damage|p2a: Charizard|50/100"
    
    result = parser.parse_battle_line(line)
    
    assert result["type"] == "damage"
    assert result["pokemon"] == "p2a: Charizard"
    assert result["hp_status"] == "50/100"


def test_parse_faint():
    """Test parsing faint message."""
    parser = MessageParser()
    line = "|faint|p2a: Charizard"
    
    result = parser.parse_battle_line(line)
    
    assert result["type"] == "faint"
    assert result["pokemon"] == "p2a: Charizard"


def test_parse_turn():
    """Test parsing turn message."""
    parser = MessageParser()
    line = "|turn|5"
    
    result = parser.parse_battle_line(line)
    
    assert result["type"] == "turn"
    assert result["turn_number"] == 5


def test_parse_win():
    """Test parsing win message."""
    parser = MessageParser()
    line = "|win|TestUser"
    
    result = parser.parse_battle_line(line)
    
    assert result["type"] == "win"
    assert result["winner"] == "TestUser"
