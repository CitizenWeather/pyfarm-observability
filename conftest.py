"""Pytest configuration for pyfarm-observability."""

import sys
from pathlib import Path

# Add src directories to path for imports
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "src"))

# Add pyfarm-core to path
core_path = repo_root.parent / "pyfarm-core" / "src"
if core_path.exists():
    sys.path.insert(0, str(core_path))
