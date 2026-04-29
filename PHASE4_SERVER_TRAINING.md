# Phase 4 Server Training Guide

## What Was Fixed

The training script at [train_phase4_server.py](train_phase4_server.py) now includes critical fixes to the reward function:

### Key Changes
1. **KO Bonus**: Increased from 5 → **50** (heavily incentivize actual knockouts)
2. **Turn Limit**: Reduced from 100 → **50** turns (faster battles)
3. **Turn Limit Penalty**: Added **-25 reward** for timeout draws (punish stalling)
4. **HP Advantage Weight**: Reduced from 0.5 → **0.2** (KOs matter more than HP)

### Result
The model will now learn to finish battles decisively with KOs instead of surviving until the turn limit.

---

## Server Training Setup

### Quick Start

```bash
# Clone/pull the latest code
git pull origin main

# Activate your environment
source .venv/bin/activate

# Run training (starts with Phase 3 best model, generates Phase 4)
PYTHONPATH=. python train_phase4_server.py \
  --timesteps 1000000 \
  --n-envs 16 \
  --opponent random
```

### Command Line Options

```bash
usage: train_phase4_server.py [-h] [--algorithm {PPO,A2C,DQN}]
                              [--timesteps TIMESTEPS] 
                              [--n-envs N_ENVS]
                              [--save-path SAVE_PATH] 
                              [--log-dir LOG_DIR]
                              [--checkpoint-freq CHECKPOINT_FREQ]
                              [--eval-freq EVAL_FREQ] 
                              [--resume RESUME]
                              [--opponent {random,heuristic}]

Options:
  --algorithm {PPO,A2C,DQN}      RL algorithm (default: PPO)
  --timesteps TIMESTEPS          Total training steps (default: 1000000)
  --n-envs N_ENVS                Parallel environments (default: 16)
  --save-path SAVE_PATH          Model save location
  --opponent {random,heuristic}  Training opponent (default: random)
  --resume RESUME                Path to model to resume from (without .zip)
```

### Common Training Scenarios

#### Scenario 1: Quick Test Run (4 hours)
```bash
PYTHONPATH=. python train_phase4_server.py \
  --timesteps 100000 \
  --n-envs 4 \
  --opponent random
```
Output: `models/ppo_phase4_fixed_reward/`

#### Scenario 2: Full Training (overnight, ~12-16 hours)
```bash
PYTHONPATH=. python train_phase4_server.py \
  --timesteps 1000000 \
  --n-envs 16 \
  --opponent random
```
Output: `models/ppo_phase4_fixed_reward/`

#### Scenario 3: Resume from Phase 3 Checkpoint
```bash
PYTHONPATH=. python train_phase4_server.py \
  --resume models/ppo_phase3_showdown_new/best_model \
  --timesteps 500000 \
  --n-envs 16 \
  --opponent random
```

#### Scenario 4: Train Against Heuristic (harder baseline)
```bash
PYTHONPATH=. python train_phase4_server.py \
  --timesteps 1000000 \
  --n-envs 8 \
  --opponent heuristic
```
Output: `models/ppo_phase4_fixed_reward/`

---

## Monitoring Progress

### With TensorBoard (Real-time)
```bash
tensorboard --logdir logs/phase4_fixed_reward
```
Then open http://localhost:6006

Watch for:
- `env/episode_reward`: Should increase over time
- `rollout/ep_len_mean`: Should trend downward (faster wins)
- `eval/mean_reward`: Evaluation performance

### Check Intermediate Checkpoints
```bash
PYTHONPATH=. python scripts/evaluate_rl.py \
  --model models/ppo_phase4_fixed_reward/checkpoint_500000_steps \
  --algorithm PPO \
  --episodes 20 \
  --opponent random
```

This shows finish modes (KO vs TurnLimit %) at each checkpoint.

---

## After Training Completes

### Evaluate Final Model
```bash
PYTHONPATH=. python scripts/evaluate_rl.py \
  --model models/ppo_phase4_fixed_reward/final_model \
  --algorithm PPO \
  --episodes 50 \
  --opponent random
```

Expected output shows:
```
Win Rate: XX%
Wins: XX
Losses: XX
Draws: XX
Average Reward: XXXX
Finish Modes: KO=XX (XX%), TurnLimit=YY (YY%)
```

**Success metric**: >30% KO finishes (was 0% before fix)

### Test Against Heuristic
```bash
PYTHONPATH=. python scripts/evaluate_rl.py \
  --model models/ppo_phase4_fixed_reward/final_model \
  --algorithm PPO \
  --episodes 50 \
  --opponent heuristic
```

**Target**: >50% win rate with mostly KO finishes

---

## Hardware Recommendations

| Configuration | Timesteps | Duration | GPU |
|---|---|---|---|
| n_envs=4 | 100k | ~4h | Optional |
| n_envs=8 | 500k | ~12h | Optional |
| n_envs=16 | 1M | ~16h | Optional (faster with GPU) |
| n_envs=32 | 2M | ~24h | Recommended |

**Tips:**
- Increase `n_envs` if you have CPU cores (8+ cores → use 16+ envs)
- GPU helps if you have CUDA available
- Script auto-detects: `device=auto`

---

## Troubleshooting

### Out of Memory
Reduce `n_envs`:
```bash
python train_phase4_server.py --n-envs 4 --timesteps 1000000
```

### CPU Maxed Out
Reduce `n_envs` (too many parallel processes).

### Takes Too Long
Increase `n_envs` (if CPU/RAM available).

### Training Crashes
Check logs:
```bash
tail -100 logs/phase4_fixed_reward/progress.txt
```

---

## File Structure

After training, you'll have:
```
models/ppo_phase4_fixed_reward/
  ├── best_model.zip              # Best evaluation checkpoint
  ├── final_model.zip             # Final model after training
  ├── checkpoint_50000_steps.zip  # Intermediate checkpoints
  ├── checkpoint_100000_steps.zip
  ├── checkpoint_150000_steps.zip
  └── metadata.json               # Training metadata

logs/phase4_fixed_reward/
  ├── PPO_1/                      # TensorBoard event files
  └── evaluations.npz             # Evaluation results
```

---

## Next Steps After Phase 4

1. **Phase 4D**: Add curriculum learning (progressive opponent difficulty)
2. **Phase 4E**: Implement self-play with policy pool
3. **Phase 5**: Deploy to live Pokemon Showdown ladder

See project proposal in [README.md](README.md) for full roadmap.

---

## Questions?

- Check [README.md](README.md) for project overview
- Review [scripts/evaluate_rl.py](scripts/evaluate_rl.py) for evaluation details
- Check [src/ml/environment.py](src/ml/environment.py) for reward function details
