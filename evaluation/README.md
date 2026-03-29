# Running the Evaluation

## Prerequisites

1. **Docker Desktop** — must be installed and running. Verify: `docker info`
2. **Harbor 0.2.0** — installed in the `after_query` conda environment
3. **OpenRouter API key** — one key covers all 3 models

## Setup

```bash
conda activate after_query

# Fill in your OpenRouter key
vim evaluation/.env        # set OPENROUTER_API_KEY=sk-or-v1-...
```

## Run All 3 Models

```bash
# 3 models × 3 trials = 9 trials, run 3 at a time
harbor run -c evaluation/job.yaml --env-file evaluation/.env
```

## Run a Single Model (quick test)

```bash
harbor run -p ./harbor-task -a terminus-2 -m openrouter/anthropic/claude-opus-4.6 --env-file evaluation/.env -e docker 2>&1
```

Replace `openrouter/anthropic/claude-opus-4.6` with any OpenRouter model ID:
- `openrouter/openai/gpt-5.4`
- `openrouter/google/gemini-3.1-pro-preview`

## Viewing Results

```bash
# List completed trials
harbor trials list

# Check scores
cat evaluation/results/3d-voxel-packing-frontier-eval/*/verifier/reward.txt

# Inspect a trial's solution voxels
cat evaluation/results/3d-voxel-packing-frontier-eval/<trial-id>/artifacts/solution.json

# Export agent trajectories (for trace analysis)
harbor traces export --sharegpt
```

## Model ID Mapping

| Evaluation Target | OpenRouter Model ID |
|---|---|
| GPT 5.4 | `openrouter/openai/gpt-5.4` |
| Opus 4.6 | `openrouter/anthropic/claude-opus-4.6` |
| Gemini 3.1 Pro | `openrouter/google/gemini-3.1-pro-preview` |

## Manual Verifier Test

```bash
python3 harbor-task/tests/verifier.py \
  visualizer/gemini.json \
  harbor-task/objects.json
```
