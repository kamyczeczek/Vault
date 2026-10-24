@echo off
REM Open Interpreter -> OmniRoute (custom OpenAI-compatible endpoint)
REM
REM WHY THIS EXISTS INSTEAD OF ENV VARS:
REM   OPENAI_API_KEY is already set in the User environment by another tool
REM   (a different sk-... key, 35 chars). Overwriting it would break that tool,
REM   and setting OPENAI_API_BASE globally would make every bare `interpreter`
REM   call send that foreign key to OmniRoute -> 401. So nothing global is touched.
REM
REM The key is read from the existing OMNIROUTE_API_KEY (User env) and injected
REM into THIS process only. It is never written to disk by this script.
REM
REM Usage:
REM   agents\oi-omniroute.cmd                        interactive
REM   echo "prompt" ^| agents\oi-omniroute.cmd -s    one-shot, non-interactive
REM   echo "prompt" ^| agents\oi-omniroute.cmd -s -safe off -y   allow code exec

setlocal
set "OPENAI_API_BASE=http://localhost:20128/v1"

if not defined OMNIROUTE_API_KEY (
  echo [BLAD] Brak OMNIROUTE_API_KEY w zmiennych uzytkownika.
  echo        Ustaw:  setx OMNIROUTE_API_KEY "twoj-klucz"
  exit /b 1
)
set "OPENAI_API_KEY=%OMNIROUTE_API_KEY%"

REM --llm_supports_functions is NOT optional. Without it OI 0.4.3 auto-detects the
REM wrong LLM mode for this model, never executes the code, and the model then
REM FABRICATES plausible output (observed: 8, then 16, then 32 cores against a
REM real 12). Silent wrong answers are worse than a crash. With the flag, code
REM runs for real - verified against len(str(2**100))=31 and the real cwd.
REM -safe off -y = never ask before running code. -y alone is NOT enough:
REM default safe_mode=ask still blocks, and in -s/stdin mode nobody answers.
REM To get the confirmation back, pass them later on the command line (argparse
REM takes the last one), e.g. oi-omniroute.cmd -s -safe ask
REM WARNING: this runs generated code immediately under your account, with no
REM prompt. Fine for ad-hoc scripting on your own machine; do NOT use it where a
REM downloaded/remote model could suggest destructive code.
"%USERPROFILE%\.local\bin\interpreter.exe" -m openai/cx/gpt-5.6-luna-low --llm_supports_functions -cw 32000 -dt -safe off -y %*
