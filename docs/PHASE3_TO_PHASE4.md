# Phase 3 → Phase 4 Transition Guide

## Quick Start for Phase 4

Phase 3 is complete! Here's everything you need to continue to Phase 4.

## What Was Completed in Phase 3

✅ **Training Infrastructure**
- PPO training pipeline with Stable-Baselines3
- Parallel environment support (4-8 envs)
- TensorBoard logging
- Model checkpointing

✅ **Models Trained**
- `models/ppo_phase3/final_model` (100k timesteps)
- `models/ppo_phase3_500k/final_model` (500k timesteps)

✅ **Benchmarking System**
- Automated evaluation against multiple opponents
- Statistical reporting (win rate, rewards, episode length)
- JSON export for tracking progress

✅ **Key Results**
- Reward improved 156% (from -51.67 to 132.13)
- Training stable and scalable
- Infrastructure ready for advanced work

## Phase 3 Benchmark Results

| Model | Timesteps | vs Random | vs Heuristic |
|-------|-----------|-----------|--------------|
| Phase 3 (500k) | 500,000 | 0% win | 0% win |
| Avg Reward | - | 132.13 | 141.92 |

**Key Insight:** Model is learning (reward improving) but environment simulation needs enhancement for competitive play.

## Why 0% Win Rate?

The environment simulation is simplified:
1. No real type effectiveness
2. Random damage calculation
3. Simplified turn mechanics
4. No move effects or abilities
5. Reward function doesn't correlate with wins

**This is expected and fixable in Phase 4!**

## Phase 4 Objectives

### 🔴 Critical (Must Do)

1. **Enhanced Environment Simulation**
   ```python
   # Integrate real damage calculator
   # Implement type effectiveness
   # Add status conditions
   # Proper turn order (speed-based)
   ```

2. **Improved Reward Function**
   ```python
   # Win: +100, Loss: -100
   # HP advantage: +0.5 per % difference
   # KO bonus: +5
   # Efficiency bonus: -0.1 per turn
   ```

3. **Action Masking**
   ```python
   # Mask illegal moves dynamically
   # Prevent fainted Pokemon switches
   # Ensure only valid actions
   ```

### 🟡 Important (Should Do)

4. **Extended Training**
   - Train for 1M-5M timesteps
   - Use 16 parallel environments
   - Implement better checkpointing

5. **Curriculum Learning**
   - Stage 1: Basic mechanics (100k)
   - Stage 2: vs Random (300k)
   - Stage 3: vs Heuristic (500k)
   - Stage 4: Self-play (1M+)

6. **Hyperparameter Tuning**
   - Try different learning rates
   - Adjust batch sizes
   - Optimize network architecture

### 🟢 Nice to Have

7. **Algorithm Comparison**
   - Test DQN with prioritized replay
   - Try A2C for comparison
   - Consider SAC

8. **Advanced Features**
   - Opponent modeling
   - Team diversity
   - Battle format variety

## Quick Commands Reference

### Train New Model
```bash
# Standard training (1M timesteps)
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 1000000 \
    --n-envs 16 \
    --save-path models/ppo_phase4 \
    --log-dir logs/phase4

# With curriculum learning
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 1000000 \
    --n-envs 16 \
    --curriculum \
    --save-path models/ppo_phase4_curriculum
```

### Evaluate Model
```bash
# Quick evaluation
python scripts/evaluate_rl.py \
    --model models/ppo_phase3_500k/final_model \
    --algorithm PPO \
    --opponent random \
    --episodes 100

# Comprehensive benchmark
python scripts/benchmark_phase3.py \
    --model models/ppo_phase4/final_model \
    --algorithm PPO \
    --episodes 200 \
    --output logs/phase4_benchmark.json
```

### Monitor Training
```bash
# TensorBoard
tensorboard --logdir logs/phase4

# Watch logs
tail -f logs/phase4_training.log

# Check GPU usage (if available)
watch -n 1 nvidia-smi
```

### Resume Training
```bash
# Resume from checkpoint
python scripts/train_rl.py \
    --algorithm PPO \
    --timesteps 1000000 \
    --resume models/ppo_phase3_500k/final_model \
    --save-path models/ppo_phase4_continued
```

## File Locations

### Important Files
- **Training Script:** `scripts/train_rl.py`
- **Environment:** `src/ml/environment.py` ⚠️ Needs enhancement
- **RL Agent:** `src/ml/rl_agent.py`
- **Benchmark:** `scripts/benchmark_phase3.py`

### Documentation
- **Phase 3 Progress:** `docs/PHASE3_PROGRESS.md`
- **Phase 3 Completion:** `docs/PHASE3_COMPLETION.md`
- **RL Training Guide:** `docs/RL_TRAINING_GUIDE.md`
- **This Guide:** `docs/PHASE3_TO_PHASE4.md`

### Models
- **100k model:** `models/ppo_phase3/final_model`
- **500k model:** `models/ppo_phase3_500k/final_model`
- **Phase 4 models:** Will be in `models/ppo_phase4/`

### Logs
- **Phase 3 logs:** `logs/phase3/` and `logs/phase3_extended/`
- **Benchmark results:** `logs/phase3_final_benchmark.json`
- **Phase 4 logs:** Will be in `logs/phase4/`

## Environment Enhancement Priority

Here's the specific code that needs work for Phase 4:

### 1. Fix Battle Simulation (`src/ml/environment.py`)

**Current (Simplified):**
```python
# Random damage
damage = np.random.randint(20, 40)
```

**Needed (Real):**
```python
# Use damage calculator
from ..data.damage_calculator import DamageCalculator
damage = self.damage_calc.calculate_damage(
    attacker=our_active,
    defender=opp_active,
    move=move_data,
    field=self.state.field
)
```

### 2. Implement Type Effectiveness
```python
# Add to state representation
type_matchup = get_type_effectiveness(
    our_active.types,
    opp_active.types
)
features.append(type_matchup)
```

### 3. Fix Reward Function
```python
# Battle outcome
if battle_over:
    if our_alive > opp_alive:
        reward += 100  # Win
    else:
        reward -= 100  # Loss

# HP advantage
hp_diff = our_active.hp_percent - opp_active.hp_percent
reward += hp_diff * 0.5

# KO rewards
if opp_active.hp == 0:
    reward += 5
if our_active.hp == 0:
    reward -= 5
```

## Expected Phase 4 Results

With enhanced environment and training:

| Metric | Phase 3 | Phase 4 Target |
|--------|---------|----------------|
| vs Random | 0% | >70% |
| vs Heuristic | 0% | >40% |
| Avg Reward | 132 | >200 |
| Training Time | 5 min | 20-60 min |

## Troubleshooting

### If Training Hangs
```bash
# Check if process is running
ps aux | grep train_rl

# Kill if necessary
pkill -f train_rl.py

# Reduce parallel environments
--n-envs 4  # instead of 16
```

### If Out of Memory
```bash
# Reduce batch size
--batch-size 1024  # instead of 2048

# Reduce parallel environments
--n-envs 4
```

### If Win Rate Still 0%
1. Check environment simulation is using real damage
2. Verify reward function rewards wins
3. Ensure action masking prevents illegal moves
4. Train longer (1M+ timesteps)
5. Check TensorBoard for learning curves

## Success Criteria for Phase 4

| Criterion | Target | How to Verify |
|-----------|--------|---------------|
| vs Random Agent | >70% win rate | `benchmark_phase3.py` |
| vs Heuristic | >40% win rate | `benchmark_phase3.py` |
| Reward improvement | >50% increase | Compare to Phase 3 |
| Training stability | No crashes | Check logs |
| Environment realism | Real mechanics | Manual testing |

## Next Actions

1. ✅ Review Phase 3 results (You are here!)
2. ⏳ Enhance environment simulation in `src/ml/environment.py`
3. ⏳ Update reward function
4. ⏳ Train new model with 1M timesteps
5. ⏳ Benchmark and compare to Phase 3
6. ⏳ Document Phase 4 results

## Getting Help

- **View training logs:** `tail -f logs/phase4_training.log`
- **Check TensorBoard:** `tensorboard --logdir logs/phase4`
- **Review environment:** `src/ml/environment.py`
- **Test environment:** `python scripts/test_env_integration.py`
- **Run quick test:** `python scripts/train_rl.py --timesteps 1000 --n-envs 1`

## Additional Resources

- **Stable-Baselines3 Docs:** https://stable-baselines3.readthedocs.io/
- **PPO Paper:** Schulman et al., 2017
- **Pokemon Damage Calc:** Already in `src/data/damage_calculator.py`
- **Type Effectiveness:** Already in `src/data/type_effectiveness.py`

---

**Phase 3 Status:** ✅ Complete  
**Phase 4 Status:** 🚀 Ready to Start  
**Estimated Time:** 2-3 hours

Good luck with Phase 4! The infrastructure is solid, now we just need to enhance the environment simulation for competitive play.

*"The only way to do great work is to love what you do."* - Steve Jobs
