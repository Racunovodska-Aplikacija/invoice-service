import sys
from pathlib import Path


# Ensure repo root is importable so `import main` / `import service...` works reliably
# across different runners/tools (e.g. uv on Windows).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

