"""Tests for damage calculator."""
import pytest
from src.data.models import Pokemon, Move
from src.data.damage_calculator import DamageCalculator, DamageRange


def test_basic_damage():
    """Test basic damage calculation."""
    calc = DamageCalculator()
    
    # Create attacker and defender
    attacker = Pokemon(
        species="Pikachu",
        level=50,
        stats={"atk": 100, "def": 100, "spa": 100, "spd": 100, "spe": 100}
    )
    
    defender = Pokemon(
        species="Charizard",
        level=50,
        stats={"atk": 100, "def": 100, "spa": 100, "spd": 100, "spe": 100}
    )
    
    # Create move
    move = Move(
        name="Thunderbolt",
        type="Electric",
        category="Special",
        power=90,
        accuracy=100
    )
    
    # Calculate damage
    damage = calc.calculate_damage(attacker, defender, move)
    
    assert isinstance(damage, DamageRange)
    assert damage.min > 0
    assert damage.max >= damage.min


def test_super_effective_damage():
    """Test damage with type effectiveness."""
    calc = DamageCalculator()
    
    attacker = Pokemon(species="Pikachu", level=50)
    attacker.stats = {"atk": 100, "spa": 100, "spd": 100, "def": 100, "spe": 100}
    
    defender = Pokemon(species="Gyarados", level=50)
    defender.stats = {"atk": 100, "spa": 100, "spd": 100, "def": 100, "spe": 100}
    
    move = Move(name="Thunder", type="Electric", category="Special", power=110)
    
    # Electric is super effective against Water/Flying
    damage = calc.calculate_damage(
        attacker, defender, move,
        user_types=["Electric"],
        target_types=["Water", "Flying"]
    )
    
    # Should deal 4x damage (2x from each type)
    assert damage.min > 0


def test_status_move_damage():
    """Test that status moves deal no damage."""
    calc = DamageCalculator()
    
    attacker = Pokemon(species="Pikachu", level=50)
    defender = Pokemon(species="Charizard", level=50)
    
    move = Move(name="Thunder Wave", type="Electric", category="Status", power=0)
    
    damage = calc.calculate_damage(attacker, defender, move)
    
    assert damage.min == 0
    assert damage.max == 0


def test_critical_hit():
    """Test critical hit damage."""
    calc = DamageCalculator()
    
    attacker = Pokemon(species="Pikachu", level=50)
    attacker.stats = {"atk": 100, "spa": 100, "spd": 100, "def": 100, "spe": 100}
    
    defender = Pokemon(species="Charizard", level=50)
    defender.stats = {"atk": 100, "spa": 100, "spd": 100, "def": 100, "spe": 100}
    
    move = Move(name="Thunderbolt", type="Electric", category="Special", power=90)
    
    normal_damage = calc.calculate_damage(attacker, defender, move, is_critical=False)
    crit_damage = calc.calculate_damage(attacker, defender, move, is_critical=True)
    
    # Critical hits should deal more damage
    assert crit_damage.average > normal_damage.average


def test_damage_range_ko():
    """Test KO calculations."""
    damage = DamageRange(50, 60)
    
    # Should KO if HP is 50 or less
    assert damage.guarantees_ko(50)
    assert damage.guarantees_ko(40)
    assert not damage.guarantees_ko(60)
    assert not damage.guarantees_ko(70)
    
    # Check hits to KO
    min_hits, max_hits = damage.rolls_to_ko(100)
    assert min_hits == 2  # 60 damage * 2 = 120
    assert max_hits == 2  # 50 damage * 2 = 100
