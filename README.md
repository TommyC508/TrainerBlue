# Pokemon Showdown AI Agent 🎮⚡

An autonomous AI agent that plays Pokemon Showdown battles using rule-based heuristics and reinforcement learning.

## 🌟 Features

- **WebSocket Connection**: Real-time communication with Pokemon Showdown servers
- **Battle State Management**: Complete tracking of battle state, Pokemon, moves, and field conditions
- **Multiple Agent Types**:
  - **Random Agent**: Baseline that chooses random legal actions
  - **Heuristic Agent**: Rule-based decision making with type effectiveness and damage calculations
  - **RL Agent**: Reinforcement learning with PPO, DQN, and A2C (NEW!)
- **Damage Calculator**: Accurate Pokemon damage formula implementation
- **Type Effectiveness**: Complete type chart with STAB calculations
- **RL Training System**: Complete training pipeline with StableBaselines3 and Gymnasium
- **Extensible Architecture**: Easy to add new agents and training methods

## 🆕 What's New - RL Implementation

**Complete reinforcement learning system now available!**

- ✅ Gymnasium environment for Pokemon battles
- ✅ StableBaselines3 integration (PPO, DQN, A2C)
- ✅ Training script with parallel environments
- ✅ Evaluation script for testing agents
- ✅ Tensorboard logging
- ✅ Comprehensive training guide

See [RL Implementation Summary](RL_IMPLEMENTATION_SUMMARY.md) for details.

## 📋 Project Structure

```
pokemon-showdown-agent/
├── src/
│   ├── connection/          # Pokemon Showdown WebSocket client
│   ├── battle/              # Battle state management
│   ├── agents/              # AI agents (random, heuristic)
│   ├── ml/                  # RL environment and agents (NEW!)
│   ├── data/                # Data models and calculations
│   ├── utils/               # Utilities (logging, config)
│   ├── battle_handler.py    # Coordinates agent and battle
│   └── main.py              # Entry point
├── scripts/                 # Training and evaluation scripts (NEW!)
├── tests/                   # Unit tests (19 passing)
├── docs/                    # Documentation
├── config/                  # Configuration files
├── logs/                    # Log files and Tensorboard logs
└── models/                  # Saved RL models
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Pokemon Showdown account (can use guest account)

### Installation

1. **Clone the repository**:
```bash
cd /workspaces/Black
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

3. **Set up environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
PS_USERNAME=your_username
PS_PASSWORD=your_password  # Optional for guest
PS_SERVER_URL=sim3.psim.us:8000
```

### Running the Agent

**Option 1: Rule-Based Agents**

Play battles with heuristic agent:
```bash
python -m src.main --agent heuristic --battles 5
```

Play with random agent:
```bash
python -m src.main --agent random --battles 3
```

Specify battle format:
```bash
python -m src.main --agent heuristic --format gen9ou --battles 10
```

**Option 2: Train RL Agents (NEW!)**

Train a reinforcement learning agent:
```bash
# Quick training (5 minutes)
python scripts/train_rl.py --algorithm PPO --timesteps 50000 --n-envs 4

# Full training (2-3 hours)
python scripts/train_rl.py --algorithm PPO --timesteps 1000000 --n-envs 8

# Monitor training with Tensorboard
tensorboard --logdir logs/rl
```

Evaluate trained agent:
```bash
python scripts/evaluate_rl.py --model models/ppo_1m/final_model --algorithm PPO --episodes 100
```

See [RL Training Guide](docs/RL_TRAINING_GUIDE.md) for detailed instructions.

**Enable debug logging**:
```bash
python -m src.main --agent heuristic --battles 1 --log-level DEBUG
```

## 🎯 How It Works

### 1. Connection Layer
The agent connects to Pokemon Showdown via WebSocket and handles:
- Authentication and login
- Battle search and matchmaking
- Message parsing (Protocol.md format)
- Action sending (moves, switches)

### 2. Battle State Management
Tracks complete battle state including:
- Both teams' Pokemon (HP, status, stats, boosts)
- Active Pokemon
- Field conditions (weather, terrain, trick room)
- Side conditions (hazards, screens)
- Turn number and battle status

### 3. Agent Decision Making

**Random Agent**: Chooses random legal actions (baseline)

**Heuristic Agent**: Uses rules like:
- Calculate expected damage for each move
- Consider type effectiveness
- Switch when in danger or bad matchup
- Prefer super-effective moves
- Consider HP percentages
- Prioritize KOs when possible

### 4. Damage Calculation
Implements Gen 9 damage formula:
```
Damage = ((2 * Level / 5 + 2) * Power * A/D / 50 + 2) * Modifiers
```

Modifiers include:
- Type effectiveness (0x, 0.25x, 0.5x, 1x, 2x, 4x)
- STAB (Same-Type Attack Bonus: 1.5x)
- Weather effects
- Critical hits (1.5x)
- Burn (0.5x for physical moves)
- Random factor (0.85-1.0)

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📊 Example Output

```
2024-11-14 10:30:15 - INFO - === Pokemon Showdown Agent ===
2024-11-14 10:30:15 - INFO - Agent type: heuristic
2024-11-14 10:30:15 - INFO - Format: gen9randombattle
2024-11-14 10:30:15 - INFO - Battles: 5
2024-11-14 10:30:16 - INFO - Connected and logged in successfully
2024-11-14 10:30:16 - INFO - Searching for gen9randombattle battle...
2024-11-14 10:30:20 - INFO - New battle detected: battle-gen9randombattle-12345
2024-11-14 10:30:20 - INFO - HeuristicAgent starting battle
2024-11-14 10:30:25 - INFO - Chose action: move 1
2024-11-14 10:32:45 - INFO - Battle finished! Winner: YourUsername
2024-11-14 10:32:45 - INFO - HeuristicAgent finished battle. Result: WIN. Record: 1/1 (100.0%)

=== Battle Statistics ===
Agent: HeuristicAgent
Battles played: 5
Battles won: 3
Win rate: 60.0%
```

## 🔧 Configuration

Edit `config/config.yaml`:
```yaml
showdown:
  server_url: "sim3.psim.us:8000"
  format: "gen9randombattle"

agent:
  type: "heuristic"
  search_depth: 2

logging:
  level: "INFO"
```

## 🎓 Extending the Agent

### Adding a New Agent

1. Create a new file in `src/agents/`:
```python
from .base_agent import Agent
from ..battle.state import BattleState
from ..connection.protocol import Action

class MyAgent(Agent):
    def __init__(self):
        super().__init__(name="MyAgent")
    
    def choose_move(self, state: BattleState) -> Action:
        # Your decision logic here
        legal_actions = state.get_legal_actions()
        # ... analyze and choose best action
        return chosen_action
```

2. Register in `src/agents/__init__.py`
3. Add to main.py agent choices

### Adding Machine Learning

The project is structured to easily add ML agents:
- State representation in `BattleState`
- Action space in `Action`
- Damage calculator for simulation
- Framework for experience collection

See `POKEMON_SHOWDOWN_AGENT_PLAN.md` for ML implementation details.

## 📚 Resources

- [Pokemon Showdown Protocol](https://github.com/smogon/pokemon-showdown/blob/master/PROTOCOL.md)
- [Pokemon Damage Calculator](https://calc.pokemonshowdown.com/)
- [Smogon University](https://www.smogon.com/) - Competitive Pokemon strategy

## 🛣️ Roadmap

- [x] WebSocket connection and authentication
- [x] Battle state tracking
- [x] Random agent baseline
- [x] Heuristic agent with damage calculation
- [x] Type effectiveness system
- [ ] Load actual move/Pokemon data from Showdown
- [ ] Minimax agent with game tree search
- [ ] Deep RL agent (DQN/PPO)
- [ ] Self-play training infrastructure
- [ ] Model checkpointing and evaluation
- [ ] Ladder climbing capability
- [ ] Team builder

## 🤝 Contributing

Contributions welcome! Areas to improve:
- Better heuristics
- More comprehensive testing
- ML agent implementations
- Performance optimizations
- Documentation

## 📝 License

MIT License - see LICENSE file for details

## 🎮 Have Fun!

This agent is for educational and research purposes. Enjoy building and improving your Pokemon AI agent!

---

**Built with ❤️ for Pokemon and AI enthusiasts**