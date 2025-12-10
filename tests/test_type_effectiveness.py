"""Tests for type effectiveness calculations."""
import pytest
from src.data.type_effectiveness import (
    get_type_effectiveness,
    is_super_effective,
    is_not_very_effective,
    is_immune,
    get_stab_multiplier
)


def test_super_effective():
    """Test super effective moves."""
    # Fire vs Grass
    assert get_type_effectiveness("Fire", ["Grass"]) == 2.0
    assert is_super_effective("Fire", ["Grass"])
    
    # Water vs Fire/Rock (double super effective)
    assert get_type_effectiveness("Water", ["Fire", "Rock"]) == 4.0
    
    # Electric vs Flying
    assert get_type_effectiveness("Electric", ["Flying"]) == 2.0


def test_not_very_effective():
    """Test not very effective moves."""
    # Water vs Grass
    assert get_type_effectiveness("Water", ["Grass"]) == 0.5
    assert is_not_very_effective("Water", ["Grass"])
    
    # Fire vs Fire/Water (double resisted)
    assert get_type_effectiveness("Fire", ["Fire", "Water"]) == 0.25


def test_immune():
    """Test immunity."""
    # Ground vs Flying
    assert get_type_effectiveness("Ground", ["Flying"]) == 0.0
    assert is_immune("Ground", ["Flying"])
    
    # Normal vs Ghost
    assert get_type_effectiveness("Normal", ["Ghost"]) == 0.0


def test_neutral():
    """Test neutral effectiveness."""
    # Normal vs Normal
    assert get_type_effectiveness("Normal", ["Normal"]) == 1.0
    
    # Fire vs Electric
    assert get_type_effectiveness("Fire", ["Electric"]) == 1.0


def test_stab():
    """Test STAB multiplier."""
    # Fire move used by Fire type
    assert get_stab_multiplier("Fire", ["Fire"]) == 1.5
    
    # Fire move used by Fire/Flying
    assert get_stab_multiplier("Fire", ["Fire", "Flying"]) == 1.5
    
    # Fire move used by Water type
    assert get_stab_multiplier("Fire", ["Water"]) == 1.0
