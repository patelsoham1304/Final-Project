#!/usr/bin/env python
"""Quick launcher for the Streamlit education path generator."""

import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        cwd=".",
    )
    sys.exit(result.returncode)
