@echo off
set TQDM_DISABLE=1
set HF_HUB_DISABLE_PROGRESS_BARS=1
"C:\Users\Mateusz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe" projects\ts-ml-experiments\h720\sub_experiments\spectral_omega_gate\rolling_arm_phase2.py --origins disjoint4 %*
