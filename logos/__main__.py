"""
LogOS entry point.

Allows running via:
  python -m logos health
"""

import sys
from logos.cli import main

if __name__ == "__main__":
    sys.exit(main())
