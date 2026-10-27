"""Shim to run only the G4 5-seed sweep of the AMR-24/168 final runner."""
import _workspace_paths  # noqa: F401  (bootstrap sys.path)
import run_amr_h720_final as r

if __name__ == "__main__":
    r.run_g4(r.load_selected_anchor())
