# Getting Started with Your Pokemon Showdown Agent

Welcome! Your Pokemon Showdown AI agent is ready to battle. Follow these steps to get started.

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install pydantic websockets aiohttp python-dotenv pyyaml pytest
```

### Step 2: Set Up Credentials

Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
PS_USERNAME=YourUsername
PS_PASSWORD=YourPassword
PS_SERVER_URL=sim3.psim.us:8000
```

**Don't have an account?** You can use a guest account by leaving the password blank.

### Step 3: Run Your First Battle!
```bash
python -m src.main --agent heuristic --battles 1 --format gen9randombattle
```

That's it! Your agent is now playing Pokemon Showdown! 🎉

---

## 📖 Understanding the Output

When you run a battle, you'll see:

```
=== Pokemon Showdown Agent ===
Agent type: heuristic
Format: gen9randombattle
Battles: 1

Username: YourUsername
Connected and logged in successfully
Searching for gen9randombattle battle...

HeuristicAgent starting battle
Chose action: move 1
... (battle progresses)
Battle finished! Winner: YourUsername

=== Battle Statistics ===
Agent: HeuristicAgent
Battles played: 1
Battles won: 1
Win rate: 100.0%
```

---

## 🎮 Battle Formats

### Recommended for Testing
- **gen9randombattle** - Random teams, great for testing
- **gen9unratedrandombattle** - Random battles, unrated

### Competitive Formats (Bring Your Own Team)
- **gen9ou** - OverUsed tier
- **gen9uu** - UnderUsed tier  
- **gen9ru** - RarelyUsed tier
- **gen9nu** - NeverUsed tier

### Doubles
- **gen9doublesou** - Doubles OverUsed
- **gen9vgc2024** - VGC format

---

## 🤖 Choosing an Agent

### Random Agent
```bash
python -m src.main --agent random --battles 5
```
- Chooses random legal moves
- Good baseline to compare against
- Expected win rate: ~50% vs other random

### Heuristic Agent (Recommended)
```bash
python -m src.main --agent heuristic --battles 5
```
- Uses strategic rules and damage calculations
- Considers type effectiveness
- Makes switching decisions
- Expected win rate: 70-80% vs random

---

## 🎯 Common Use Cases

### Test the Agent
```bash
python -m src.main --agent heuristic --battles 1 --log-level DEBUG
```

### Compare Agents
```bash
# Test random agent
python -m src.main --agent random --battles 10

# Test heuristic agent
python -m src.main --agent heuristic --battles 10
```

### Long Training Session
```bash
python -m src.main --agent heuristic --battles 50
```

### Specific Format
```bash
python -m src.main --agent heuristic --battles 5 --format gen9ou
```

---

## 🔍 Debugging

### Enable Debug Logging
```bash
python -m src.main --agent heuristic --battles 1 --log-level DEBUG
```

### Check Log Files
```bash
cat logs/agent.log
```

### Run Tests
```bash
pytest tests/ -v
```

---

## 🛠️ Customizing the Agent

### Modify Heuristics

Edit `src/agents/heuristic_agent.py`:

```python
def _evaluate_move(self, move_name, our_pokemon, opp_pokemon, state):
    score = 0.0
    
    # Add your custom logic here!
    if "thunder" in move_name.lower():
        score += 100  # Prefer electric moves
    
    return score
```

### Create Your Own Agent

```python
# src/agents/my_agent.py
from .base_agent import Agent
from ..battle.state import BattleState
from ..connection.protocol import Action

class MyCustomAgent(Agent):
    def __init__(self):
        super().__init__(name="MyCustomAgent")
    
    def choose_move(self, state: BattleState) -> Action:
        # Your strategy here
        legal_actions = state.get_legal_actions()
        
        # Implement your logic
        # ...
        
        return chosen_action
```

Register in `src/main.py`:
```python
from .agents import MyCustomAgent

# In main():
if args.agent == "mycustom":
    agent = MyCustomAgent()
```

---

## 📊 Monitoring Performance

### View Statistics
The agent automatically tracks:
- Total battles played
- Battles won
- Win rate percentage

These are displayed after each session.

### Log Analysis
Check `logs/agent.log` for detailed battle information:
```bash
grep "Chose action" logs/agent.log
grep "Battle finished" logs/agent.log
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
pip install pydantic websockets aiohttp python-dotenv pyyaml
```

### "Connection refused" or "Can't connect"
- Check your internet connection
- Verify `PS_SERVER_URL` in `.env`
- Try: `sim3.psim.us:8000` or `sim.psim.us:8000`

### "Authentication failed"
- Check username/password in `.env`
- Try as guest (leave password blank)
- Make sure username doesn't have spaces

### Agent makes no moves
- Check that format is correct
- Enable debug logging: `--log-level DEBUG`
- Check logs for errors

### "No legal actions"
This is usually normal - it happens between turns or during team preview.

---

## 🎓 Learning More

### Understanding the Code
1. Start with `src/main.py` - Entry point
2. Read `src/battle_handler.py` - Battle coordination
3. Check `src/agents/heuristic_agent.py` - Decision making
4. Explore `src/battle/state.py` - State management

### Improving the Agent
1. **Better Move Evaluation**: Add move power, accuracy, effects
2. **Switching Logic**: Detect threats and switch proactively
3. **Setup Detection**: Recognize setup sweepers
4. **Prediction**: Anticipate opponent moves
5. **Team Building**: Create optimized teams

### Next Steps
- Read `POKEMON_SHOWDOWN_AGENT_PLAN.md` for ML implementation
- Check `PROJECT_STRUCTURE.md` for architecture details
- Review test files to understand components
- Join Pokemon Showdown community for strategies

---

## 💡 Pro Tips

1. **Start with Random Battles** - They're balanced and don't require team building
2. **Use Debug Logging** - See exactly what the agent is thinking
3. **Compare Agents** - Run random vs heuristic to see improvement
4. **Modify Gradually** - Make small changes and test
5. **Read Logs** - Learn from battle patterns
6. **Test Thoroughly** - Run pytest after changes

---

## 🎯 Goals to Achieve

### Beginner
- [x] Run your first battle
- [x] Win a battle with heuristic agent
- [ ] Win 3 battles in a row
- [ ] Achieve 60% win rate over 10 battles

### Intermediate
- [ ] Modify heuristics and improve win rate
- [ ] Understand all code components
- [ ] Create a custom agent
- [ ] Achieve 70% win rate vs random

### Advanced
- [ ] Implement minimax search
- [ ] Add move/Pokemon data loading
- [ ] Train an ML agent
- [ ] Compete on the ladder

---

## 🆘 Getting Help

### Resources
- **Documentation**: Read all .md files in project root
- **Code Comments**: Extensive inline documentation
- **Tests**: See `tests/` for usage examples
- **Pokemon Showdown**: https://play.pokemonshowdown.com
- **Smogon University**: https://www.smogon.com

### Common Questions

**Q: Can I use this on the ranked ladder?**
A: Yes! Use formats like `gen9ou` (but you'll need your own team).

**Q: How do I make it smarter?**
A: Improve heuristics, add move data, or implement ML (see plan).

**Q: Can it play doubles?**
A: The framework supports it, but you may need to adjust the agent.

**Q: Is this against the rules?**
A: Check Pokemon Showdown's terms of service. This is for educational purposes.

---

## ✅ Verification Checklist

Before starting, make sure:
- [x] Python 3.9+ installed
- [x] Dependencies installed (`pip install -r requirements.txt`)
- [x] `.env` file created with credentials
- [x] Tests pass (`pytest tests/`)
- [x] Can run: `python -m src.main --help`

---

## 🎉 Ready to Battle!

You're all set! Run your first battle:

```bash
python -m src.main --agent heuristic --battles 1
```

**Good luck, Trainer!** ⚡🎮

---

*Need more help? Check IMPLEMENTATION_SUMMARY.md for complete project overview*
