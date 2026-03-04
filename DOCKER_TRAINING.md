# Docker Training (Phase 3 Showdown)

Use this when training on a server where you want a reproducible container environment.

## 1) Ensure submodule is present

```bash
git submodule update --init --recursive
```

## 2) Build the training image

```bash
docker compose -f docker-compose.train.yml build
```

## 3) Start training

```bash
docker compose -f docker-compose.train.yml up -d
```

This runs:

```bash
python scripts/train_phase3_showdown.py --timesteps 2000000 --n-envs 4 --save-path models/ppo_phase3_showdown_new --log-dir logs/phase3_showdown_new
```

## 4) Monitor progress

```bash
docker compose -f docker-compose.train.yml logs -f
```

To watch TensorBoard locally from host logs:

```bash
tensorboard --logdir logs/phase3_showdown_new
```

## 5) Stop training

```bash
docker compose -f docker-compose.train.yml stop
```

## 6) Resume/change settings

Edit `docker-compose.train.yml` command arguments (for example `--timesteps` or `--n-envs`) and run `up -d` again.

## Notes

- Models are persisted to `./models` on the host.
- Logs are persisted to `./logs` on the host.
- A separate Showdown server container is **not** required for this script; it uses `simulate-battle` locally in the same container.
