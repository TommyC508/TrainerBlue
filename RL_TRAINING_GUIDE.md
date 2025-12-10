# Reinforcement Learning Training Guide

## 🤖 Overview

This guide explains how to train a Pokemon Showdown agent using **Stable-Baselines3** reinforcement learning algorithms.

### Supported Algorithms
- **PPO** (Proximal Policy Optimization) - Recommended for beginners
- **DQN** (Deep Q-Network) - Good for discrete actions
- **A2C** (Advantage Actor-Critic) - Faster but less stable

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install stable-baselines3 tensorboard gymnasium
```

### 2. Train Your First Agent (PPO)
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 100000 \
    --n-envs 4
```

### 3. Test the Trained Agent
```bash
python scripts/test_rl.py models/rl_agent/best_model.zip \
    --algorithm PPO \
    --episodes 10 \
    --render
```

### 4. View Training Progress
```bash
tensorboard --logdir logs/rl
```
Then open http://localhost:6006 in your browser

---

## 📊 Environment Details

### Observation Space (200 features)
- **Our Active Pokemon** (50 features)
  - HP ratio, level, active status, fainted status
  - Status conditions (burn, paralysis, etc.)
  - Stats (Attack, Defense, Sp.Atk, Sp.Def, Speed)
  - Stat boosts (-6 to +6)
  - Number of moves

- **Opponent Active Pokemon** (50 features)
  - Same features as our Pokemon

- **Field Conditions** (20 features)
  - Trick Room, Gravity, Magic Room, Wonder Room
  - Weather (Sun, Rain, Sandstorm, Hail)
  - Terrain (Electric, Grassy, Misty, Psychic)

- **Our Team Summary** (40 features)
  - Number of Pokemon alive
  - Hazards (Spikes, Toxic Spikes, Stealth Rock, Sticky Web)
  - Screens (Light Screen, Reflect, Aurora Veil)
  - Average team HP

- **Opponent Team Summary** (40 features)
  - Same as our team summary

### Action Space (9 actions)
- Actions 0-3: Use moves 1-4
- Actions 4-8: Switch to Pokemon 2-6

### Reward Structure
The agent receives rewards based on:
- **Positive rewards:**
  - Dealing damage to opponent
  - Using super-effective moves
  - Knocking out opponent Pokemon
  - Winning the battle

- **Negative rewards:**
  - Taking damage
  - Losing Pokemon
  - Losing the battle

---

## 🎓 Training Examples

### Basic Training (PPO - Recommended)
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 500000 \
    --learning-rate 3e-4 \
    --n-envs 8
```

### Fast Training (A2C)
```bash
python scripts/train_rl.py \
    --algorithm A2C \
    --timesteps 200000 \
    --learning-rate 7e-4 \
    --n-envs 16
```

### Value-Based (DQN)
```bash
python scripts/train_rl.py \
    --algorithm DQN \
    --timesteps 1000000 \
    --learning-rate 1e-4 \
    --batch-size 32
```

### Resume Training
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 500000 \
    --resume models/rl_agent/best_model.zip
```

### GPU Training
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 1000000 \
    --device cuda \
    --n-envs 16
```

---

## 🔧 Advanced Configuration

### Hyperparameter Tuning

**PPO (Default - Good Starting Point)**
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --learning-rate 3e-4 \
    --batch-size 64 \
    --n-envs 8
```

**PPO (Aggressive Learning)**
```bash
python scripts/train_rl.py \
    --algorithm PPO \
    --learning-rate 1e-3 \
    --batch-size 128 \
    --n-envs 16
```

**DQN (Exploration Focus)**
```bash
python scripts/train_rl.py \
    --algorithm DQN \
    --learning-rate 5e-4 \
    --batch-size 64
```

---

## 📈 Monitoring Training

### TensorBoard
Start TensorBoard to monitor training progress:
```bash
tensorboard --logdir logs/rl
```

**Metrics to watch:**
- `rollout/ep_rew_mean` - Average episode reward (should increase)
- `rollout/ep_len_mean` - Average episode length
- `train/loss` - Training loss (should decrease)
- `train/explained_variance` - Model quality (closer to 1 is better)

### Training Progress
Typical training progress:
- **0-50k steps:** Random exploration, low rewards
- **50k-200k steps:** Learning basic strategies
- **200k-500k steps:** Improving decision making
- **500k+ steps:** Refined strategies, higher win rate

---

## 🧪 Testing & Evaluation

### Test Trained Model
```bash
python scripts/test_rl.py models/rl_agent/best_model.zip \
    --algorithm PPO \
    --episodes 20
```

### Test with Rendering
```bash
python scripts/test_rl.py models/rl_agent/best_model.zip \
    --algorithm PPO \
    --episodes 5 \
    --render
```

### Compare Multiple Models
```bash
# Test baseline
python scripts/test_rl.py models/rl_agent/checkpoint_100k.zip --episodes 50

# Test improved
python scripts/test_rl.py models/rl_agent/checkpoint_500k.zip --episodes 50

# Test best
python scripts/test_rl.py models/rl_agent/best_model.zip --episodes 50
```

---

## 🎯 Using RL Agent in Battles

### Integrate with Main Application

Update `src/main.py` to add RL agent option:

```python
from src.ml import RLAgent

# In main():
if args.agent == "rl":
    agent = RLAgent(
        algorithm="PPO",
        model_path="models/rl_agent/best_model.zip"
    )
```

### Run Battles with RL Agent
```bash
python -m src.main \
    --agent rl \
    --battles 10 \
    --format gen9randombattle
```

---

## 💡 Tips for Better Training

### 1. Start Small
```bash
# Quick test with few timesteps
python scripts/train_rl.py --timesteps 10000 --n-envs 2
```

### 2. Use Multiple Environments
```bash
# More environments = faster training
python scripts/train_rl.py --n-envs 16
```

### 3. Save Checkpoints
The trainer automatically saves:
- `best_model.zip` - Best performing model
- `final_model.zip` - Final model after training

### 4. Monitor GPU Usage
```bash
# Check GPU utilization
nvidia-smi -l 1
```

### 5. Experiment with Hyperparameters
- Higher learning rate = faster learning but less stable
- More environments = faster training but more memory
- Larger batch size = more stable but slower

---

## 🐛 Troubleshooting

### Out of Memory
```bash
# Reduce number of environments
python scripts/train_rl.py --n-envs 4

# Or use CPU
python scripts/train_rl.py --device cpu
```

### Training Too Slow
```bash
# Use more environments
python scripts/train_rl.py --n-envs 16

# Use GPU
python scripts/train_rl.py --device cuda
```

### Poor Performance
- Train longer (increase `--timesteps`)
- Adjust learning rate
- Try different algorithm
- Check reward function in environment

---

## 📊 Expected Performance

### Training Time
- **100k steps:** ~10-30 minutes (4 envs, CPU)
- **500k steps:** ~1-2 hours (8 envs, CPU)
- **1M steps:** ~2-4 hours (16 envs, CPU)
- **GPU:** 3-5x faster than CPU

### Win Rate Progression
- **Random:** ~50% vs random
- **100k steps:** ~55-60% vs random
- **500k steps:** ~65-75% vs random
- **1M steps:** ~75-85% vs random

---

## 🚀 Next Steps

1. **Train baseline model** (100k steps)
2. **Evaluate performance** vs random agent
3. **Tune hyperparameters**
4. **Train longer** (500k-1M steps)
5. **Test on ladder** (real battles)

---

## 📚 Additional Resources

- [Stable-Baselines3 Docs](https://stable-baselines3.readthedocs.io/)
- [RL Algorithms Explained](https://spinningup.openai.com/)
- [Hyperparameter Tuning](https://stable-baselines3.readthedocs.io/en/master/guide/tuning.html)

---

Happy training! 🎮🤖⚡
