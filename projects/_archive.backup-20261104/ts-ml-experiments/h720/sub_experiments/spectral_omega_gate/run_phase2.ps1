# Pinned launch wrapper — Phase 2 (disjoint4 default, <15 min CPU)
$env:TQDM_DISABLE = "1"
$env:HF_HUB_DISABLE_PROGRESS_BARS = "1"
$VENV_PY = "C:\Users\Mateusz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
# Default: disjoint4 decision path (4 origins, per-origin predict, ~2 min)
# Alternatives: --origins sampled  |  --origins full
& $VENV_PY projects/ts-ml-experiments/h720/sub_experiments/spectral_omega_gate/rolling_arm_phase2.py --origins disjoint4 @args
