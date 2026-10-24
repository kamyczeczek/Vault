# Gate note (if you touch `ALLOWED_ROOT`)

`scripts/check_workspace_integrity.py` holds `ALLOWED_ROOT`, a whitelist:
any unlisted name at the workspace root is a **FAIL**. This file is listed
there for that reason. Which check is which (hard vs advisory) and the
root-entry procedure: the gate's docstring is the single home; this note
and the other docs link, not restate.
