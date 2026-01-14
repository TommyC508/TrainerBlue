# RL Training Guide

Complete guide for training reinforcement learning agents for Pokemon Showdown battles.

## Overview

The project uses **StableBaselines3** with **Gymnasium** to train intelligent Pokemon battle agents. The RL system supports multiple algorithms (PPO, DQN, A2C) and includes comprehensive training infrastructure.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Basic Training

```bash
python scripts/train_rl.py --algorithm PPO --timesteps 100000 --n-envs 4
```

### 2b. Run Training on the Official Showdown Engine (Recommended)

```bash
python scripts/train_rl.py --backend showdown --format gen9randombattle --algorithm PPO --timesteps 100000 --n-envs 4
```

### 3. Evaluate Trained Agent

```bash
python scripts/evaluate_rl.py --model-path models/rl_agent.zip --episodes 100
```

## Architecture

### Components

1. **PokemonBattleEnv** (`src/ml/environment.py`)
    - Gymnasium environment backed by the in-repo Python simulator
    - Observation space: Box(202,) - flattened battle state
    - Action space: Discrete(9) - 4 moves + up to 5 switches

2. **ShowdownPokemonBattleEnv** (`src/ml/showdown_env.py`)
    - Gymnasium environment backed by the official Pokémon Showdown engine (`simulate-battle`)
    - Observation/action shapes match the Python env so training scripts can switch backends

3. **RLAgent** (`src/ml/rl_agent.py`)
   - Wrapper for StableBaselines3 algorithms
   - Supports PPO, DQN, A2C
   - Handles model save/load
    - Accepts a training env + an evaluation env (used by EvalCallback)

4. **Training Script** (`scripts/train_rl.py`)
   - CLI for training agents
   - Parallel environment support
   - Tensorboard logging
   - Checkpoint saving

### Backend Selection

`scripts/train_rl.py` supports two backends:

- `--backend python`: in-repo environment (fast iteration)
- `--backend showdown`: official Showdown engine (highest fidelity)

You can select the format used by the official engine with `--format` (example: `gen9randombattle`).

## Training Configuration

### Algorithm Selection

**PPO (Proximal Policy Optimization)** - Recommended
- Best for continuous training
- Stable and robust
- Good sample efficiency

```bash
python scripts/train_rl.py --algorithm PPO
```

**DQN (Deep Q-Network)**
- Good for discrete action spaces
- Off-policy learning
- Requires more memory

```bash
python scripts/train_rl.py --algorithm DQN
```

**A2C (Advantage Actor-Critic)**
- Faster than PPO
- Less stable
- Good for quick experiments

```bash
python scripts/train_rl.py --algorithm A2C
```

### Hyperparameters

#### Learning Rate
Controls how quickly the agent learns. Start with 3e-4 and adjust:

```bash
python scripts/train_rl.py --learning-rate 3e-4  # Default
python scripts/train_rl.py --learning-rate 1e-3  # Faster learning
python scripts/train_rl.py --learning-rate 1e-4  # More stable
```

#### Batch Size
Number of samples per gradient update:

```bash
python scripts/train_rl.py --batch-size 64   # Default
python scripts/train_rl.py --batch-size 128  # Larger (more stable)
python scripts/train_rl.py --batch-size 32   # Smaller (faster)
```

#### Training Steps
Total environment steps (not episodes):

```bash
python scripts/train_rl.py --timesteps 100000   # Quick test
python scripts/train_rl.py --timesteps 1000000  # Full training
python scripts/train_rl.py --timesteps 10000000 # Extended training
```

#### Parallel Environments
Use multiple environments for faster training:

```bash
python scripts/train_rl.py --n-envs 1   # Single environment
python scripts/train_rl.py --n-envs 4   # 4 parallel (recommended)
python scripts/train_rl.py --n-envs 8   # 8 parallel (more CPU)
```

### Device Selection

```bash
python scripts/train_rl.py --device auto  # Auto-detect GPU/CPU
python scripts/train_rl.py --device cuda  # Force GPU
python scripts/train_rl.py --device cpu   # Force CPU
```

## Training Workflow

### Step 1: Initial Training

Train from scratch with default hyperparameters:

```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 500000 \
    --n-envs 4 \
    --save-path models/ppo_v1
```

### Step 2: Monitor Progress

View training in Tensorboard:

```bash
tensorboard --logdir logs/rl
```

Open http://localhost:6006 to see:
- Episode rewards
- Episode lengths
- Win rates
- Value function estimates

### Step 3: Evaluate Performance

Test the trained agent:

```bash
python scripts/evaluate_rl.py \
    --model-path models/ppo_v1.zip \
    --episodes 100 \
    --opponent heuristic
```

### Step 4: Resume Training

Continue training from checkpoint:

```bash
python scripts/train_rl.py \
    --resume models/ppo_v1.zip \
    --timesteps 500000 \
    --save-path models/ppo_v2
```

## Reward Shaping

The environment uses reward shaping to guide learning:

```python
# Base rewards
+1.0   # Win the battle
-1.0   # Lose the battle
0.0    # Ongoing battle

# HP-based rewards
+0.1   # Damage dealt (per 10% HP)
-0.1   # Damage taken (per 10% HP)

# Strategic rewards
+0.5   # KO opponent's Pokemon
-0.5   # Your Pokemon faints

# Turn penalty
-0.01  # Small penalty per turn (encourage efficiency)
```

Customize rewards in `src/ml/environment.py`:

```python
def _calculate_reward(self):
    reward = 0.0
    
    # Add custom reward logic
    if self.battle_won:
        reward += 10.0  # Increase win reward
    
    # Reward type advantage
    if move_has_super_effective:
        reward += 0.2
    
    return reward
```

## Observation Space

The agent observes a 195-dimensional vector containing:

### Your Team (96 dimensions)
- Pokemon stats (HP, Atk, Def, SpA, SpD, Spe) × 6 = 36
- Type encodings (18 types, one-hot) × 6 = 108... wait, that's wrong

Actually:
- Active Pokemon HP (1)
- Active Pokemon stats (6)
- Active Pokemon types (2, encoded)
- Active Pokemon status (7 one-hot)
- Active Pokemon boosts (7)
- Team preview (6 Pokemon × 7 features) = 42
- Available moves (4 × 8 features) = 32

### Opponent Team (96 dimensions)
- Same structure as your team

### Battle State (3 dimensions)
- Turn number (1)
- Weather (1, encoded)
- Terrain (1, encoded)

**Total: 195 dimensions**

## Action Space

Discrete action space with 10 possible actions:

```
0-3: Use moves 1-4
4-9: Switch to Pokemon 2-7 (slot 1 is active)
```

The environment automatically handles:
- Invalid action masking
- Move PP checking
- Fainted Pokemon
- Choice item locking

## Training Tips

### For Beginners

1. Start with PPO algorithm (most stable)
2. Use 4-8 parallel environments
3. Train for 1M timesteps minimum
4. Monitor Tensorboard frequently
5. Save checkpoints every 100k steps

### For Advanced Users

1. **Curriculum Learning**: Train against progressively stronger opponents
   ```python
   # Start with random opponent
   python scripts/train_rl.py --opponent random --timesteps 500000
   
   # Then train against heuristic
   python scripts/train_rl.py --opponent heuristic --resume models/stage1.zip
   ```

2. **Hyperparameter Tuning**: Use Optuna for optimization
   ```python
   # TODO: Add optuna_tune.py script
   ```

3. **Multi-Agent Training**: Train against other RL agents
   ```python
   # TODO: Add self-play capability
   ```

4. **Custom Reward Functions**: Modify reward calculation
   ```python
   # Edit src/ml/environment.py
   def _calculate_reward(self):
       # Your custom logic
       pass
   ```

## Troubleshooting

### Training is Slow

- Increase `--n-envs` (more parallel environments)
- Use GPU with `--device cuda`
- Reduce `--batch-size` for faster updates
- Decrease logging frequency

### Agent Not Learning

- Check Tensorboard - is reward increasing?
- Try different learning rate (1e-3 or 1e-4)
- Increase training timesteps (10M+)
- Verify reward function is correct
- Check observation space normalization

### Out of Memory

- Reduce `--n-envs`
- Reduce `--batch-size`
- Use CPU instead of GPU
- Disable replay buffer (for PPO)

### Agent Makes Invalid Moves

- Environment should mask invalid actions
- Check `get_legal_actions()` in battle state
- Verify action space mapping in agent

## Example Training Runs

### Quick Test (5 minutes)
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 50000 \
    --n-envs 4 \
    --save-path models/test
```

### Standard Training (2-3 hours)
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 1000000 \
    --learning-rate 3e-4 \
    --n-envs 8 \
    --batch-size 64 \
    --save-path models/ppo_1m
```

### Extended Training (overnight)
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 10000000 \
    --learning-rate 1e-4 \
    --n-envs 16 \
    --batch-size 128 \
    --save-path models/ppo_10m
```

## Evaluation Metrics

### Win Rate
Percentage of battles won:
```bash
python scripts/evaluate_rl.py --model-path models/ppo.zip --episodes 100
```

Target: >80% vs random, >50% vs heuristic

### Average Reward
Mean episode reward over evaluation:
```bash
# Shown in evaluation output
```

Target: >0.5 average reward

### Episode Length
Average turns per battle:
```bash
# Shorter = more efficient play
```

Target: 10-20 turns per battle

## Next Steps

1. **Self-Play**: Implement training against other RL agents
2. **Team Builder**: Train agents to select optimal teams
3. **Multi-Format**: Support different battle formats (Doubles, VGC)
4. **Showdown Integration**: Connect to real Pokemon Showdown servers
5. **Distributed Training**: Use Ray RLlib for large-scale training

## References

- [StableBaselines3 Docs](https://stable-baselines3.readthedocs.io/)
- [Gymnasium Docs](https://gymnasium.farama.org/)
- [Pokemon Showdown Protocol](https://github.com/smogon/pokemon-showdown/blob/master/PROTOCOL.md)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
- [DQN Paper](https://arxiv.org/abs/1312.5602)
