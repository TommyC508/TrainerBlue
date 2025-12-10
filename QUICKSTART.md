# Quick Start Guide

## 1. Setup Environment

```bash
# Run the setup script
bash setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure Credentials

Edit `.env` file:
```env
PS_USERNAME=your_username
PS_PASSWORD=your_password  # Optional, leave blank for guest
```

## 3. Run Your First Battle

```bash
# Activate virtual environment
source venv/bin/activate

# Run with heuristic agent
python -m src.main --agent heuristic --battles 1 --format gen9randombattle
```

## 4. Run Tests

```bash
pytest tests/ -v
```

## Battle Formats

Common formats you can try:
- `gen9randombattle` - Random battles (recommended for testing)
- `gen9ou` - OverUsed tier (bring your own team)
- `gen9uu` - UnderUsed tier
- `gen9nu` - NeverUsed tier
- `gen9doublesou` - Doubles battles

## Agents

- `random` - Chooses random moves (baseline)
- `heuristic` - Uses rules and damage calculations (better)

## Command Line Options

```bash
python -m src.main \
  --agent heuristic \        # Agent type (random, heuristic)
  --battles 5 \              # Number of battles to play
  --format gen9randombattle \ # Battle format
  --log-level INFO           # Logging level (DEBUG, INFO, WARNING, ERROR)
```

## Example Sessions

### Single test battle with debug logging
```bash
python -m src.main --agent heuristic --battles 1 --log-level DEBUG
```

### Multiple battles to test win rate
```bash
python -m src.main --agent heuristic --battles 10
```

### Compare random vs heuristic
```bash
# Run random agent
python -m src.main --agent random --battles 10

# Run heuristic agent
python -m src.main --agent heuristic --battles 10
```

## Troubleshooting

### Connection Issues
- Check that your username/password are correct in `.env`
- Try using a guest account (leave password blank)
- Check that `PS_SERVER_URL` is set correctly

### Battle Not Starting
- Random battles might take a few seconds to find a match
- Try a different format like `gen9randombattle`
- Check the logs for error messages

### Import Errors
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Run from project root directory

## Next Steps

1. **Improve the Agent**: Edit `src/agents/heuristic_agent.py` to add better strategies
2. **Add Move Data**: Load actual Pokemon/move data for better decisions
3. **Implement ML**: Follow the plan in `POKEMON_SHOWDOWN_AGENT_PLAN.md`
4. **Compete on Ladder**: Use real teams and climb the ladder

Have fun! 🎮⚡
