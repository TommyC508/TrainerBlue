# Pokemon Showdown Battle System Implementation

This project now includes an **accurate Pokemon battle simulator** based on the official [Pokemon Showdown](https://github.com/smogon/pokemon-showdown) battle engine.

## Overview

The battle system implements Pokemon Showdown's damage calculation formula and battle mechanics with high accuracy. This replaces the previous simplified mock battle system.

## Key Components

### 1. Damage Calculator (`src/battle/damage_calculator.py`)

Implements the **official Pokemon Showdown damage formula**:

```
baseDamage = floor(floor(floor(floor(2 * level / 5 + 2) * basePower * attack) / defense) / 50)
```

Then applies modifiers in the correct order:
1. **Weather modifier** (1.5x for favorable weather, 0.5x for unfavorable)
2. **Critical hit** (1.5x in Gen 6+, 2x in earlier gens)
3. **Random factor** (85-100% random variance)
4. **STAB** (Same Type Attack Bonus: 1.5x if move type matches attacker)
5. **Type effectiveness** (0x, 0.25x, 0.5x, 1x, 2x, 4x based on type chart)
6. **Burn modifier** (0.5x for physical moves if burned)
7. **Final modifiers** (items, abilities - to be implemented)

#### Features:
- **Accurate stat calculations** from base stats, IVs, EVs, and nature
- **16-bit and 32-bit truncation** matching game behavior
- **Type effectiveness system** with 18 Pokemon types
- **Generation-aware** calculations (currently Gen 9)

### 2. Battle Simulator (`src/battle/simulator.py`)

Full battle simulation system with:

#### Pokemon State Management:
- **HP tracking** with automatic fainting
- **Stat boosts** (-6 to +6 for all stats)
- **Status conditions** (burn, paralysis, sleep, etc.)
- **Actual stats calculated** from base stats using official formulas

#### Move Execution:
- **Accuracy checks** with boost modifiers
- **Priority system** (moves like Quick Attack go first)
- **Speed ties** resolved randomly
- **Critical hit chances** (1/24 by default)

#### Battle Flow:
- Turn-based combat
- Move ordering by priority → speed → random
- Damage application with type effectiveness messages
- Fainting detection

## Code Structure

```
src/battle/
├── damage_calculator.py     # Core damage formula and stat calculations
└── simulator.py             # Battle simulation engine
```

## Usage Example

```python
from src.battle.simulator import BattleSimulator, BattlePokemon, Move

# Create Pokemon with real stats
charizard = BattlePokemon(
    species="Charizard",
    level=50,
    types=["Fire", "Flying"],
    base_hp=78, base_atk=84, base_def=78,
    base_spa=109, base_spd=85, base_spe=100
)

# Create move
flamethrower = Move(
    name="Flamethrower",
    type="Fire",
    category="Special",
    base_power=90,
    accuracy=100,
    pp=15, max_pp=15
)

# Simulate battle
simulator = BattleSimulator(gen=9)
logs = simulator.simulate_turn(charizard, flamethrower, opponent, opponent_move)
```

## Demo

Run the demo to see the system in action:

```bash
python scripts/demo_showdown_battle.py
```

**Output shows:**
- Pokemon stats calculated from base stats
- Turn-by-turn battle log
- Accurate damage calculations
- Type effectiveness messages
- Critical hits
- HP bars and percentages
- Battle result

## Accuracy Verification

The implementation matches Pokemon Showdown's battle engine:

### Damage Formula
✅ **Base damage calculation** using exact PS formula  
✅ **Truncation behavior** (integer division at each step)  
✅ **Modifier order** matches Gen 5+ mechanics  
✅ **16-bit truncation** for final damage

### Type System
✅ **18 Pokemon types** (Normal, Fire, Water, etc.)  
✅ **324 type interactions** in effectiveness chart  
✅ **Immunity** (0x effectiveness)  
✅ **Resistance stacking** (e.g., 4x weakness)

### Battle Mechanics
✅ **Stat calculation** from base stats, level, IVs, EVs, nature  
✅ **Stat boosts** (-6 to +6 with correct multipliers)  
✅ **Speed calculation** with boost modifiers  
✅ **Priority system** for move ordering  
✅ **Accuracy/Evasion** with boost modifiers

### Status Effects (Implemented)
✅ **Burn** (halves physical attack damage)  
⏳ **Paralysis** (quarters speed, 25% immobilize chance)  
⏳ **Sleep** (can't move for 1-3 turns)  
⏳ **Freeze** (can't move, 20% thaw chance)  
⏳ **Poison** (loses 1/8 HP per turn)

## Comparison to Previous System

| Feature | Old Mock System | New PS System |
|---------|----------------|---------------|
| Damage Formula | Random 10-40 | Official PS formula |
| Type Effectiveness | Not used | Full 18-type chart |
| Critical Hits | Not implemented | 1/24 chance, 1.5x |
| STAB | Not implemented | 1.5x bonus |
| Stat Calculation | Random | From base stats |
| Accuracy | Always hit | Real accuracy checks |
| Weather | Not implemented | Damage modifiers |
| Priority | Not implemented | Move priority system |

## Integration with RL Environment

The new battle system can be integrated into the RL environment:

```python
# In pokemon_env.py
from src.battle.simulator import BattleSimulator, BattlePokemon, Move

class PokemonBattleEnv(gym.Env):
    def __init__(self):
        self.simulator = BattleSimulator(gen=9)
        # ... rest of initialization
    
    def _execute_action(self, action):
        # Use accurate damage calculation
        logs = self.simulator.simulate_turn(
            self.team1[self.active1], move1,
            self.team2[self.active2], move2
        )
        # Update battle state from logs
```

## Future Enhancements

Planned features to complete PS accuracy:

### Abilities
- Pressure (doubles PP usage)
- Intimidate (lowers attack on switch-in)
- Levitate (immune to Ground moves)
- Blaze/Torrent/Overgrow (1.5x power at low HP)
- Weather-setting abilities (Drought, Drizzle)

### Items
- Choice Band/Specs/Scarf
- Life Orb
- Leftovers
- Focus Sash
- Type-boosting items (Charcoal, Mystic Water, etc.)

### Advanced Mechanics
- Switching
- Weather effects (duration, damage)
- Terrain effects
- Entry hazards (Stealth Rock, Spikes)
- Protect/Detect
- Multi-hit moves
- Recoil moves
- Draining moves

### Move Categories
- **Status moves** (stat changes, status infliction)
- **Multi-hit moves** (2-5 hits)
- **Priority moves** (Quick Attack, Mach Punch)
- **OHKO moves** (Fissure, Sheer Cold)

## References

- **Pokemon Showdown**: https://github.com/smogon/pokemon-showdown
- **Damage Formula**: `sim/battle-actions.ts` lines 1709-1719
- **Type Chart**: `data/typechart.ts`
- **Stat Calculation**: `sim/pokemon.ts`

## Testing

The system has been validated against:
- ✅ Pokemon Showdown source code
- ✅ Manual damage calculations
- ✅ Type effectiveness chart
- ✅ Stat calculation formulas

## Conclusion

This implementation provides a **highly accurate** Pokemon battle simulator that can be used for:
- **RL agent training** with realistic battles
- **Battle analysis** and strategy testing
- **Pokemon AI development**
- **Competitive Pokemon research**

The system is extensible and can be enhanced with additional Pokemon Showdown features as needed.
