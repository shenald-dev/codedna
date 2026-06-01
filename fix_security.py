with open("codedna/analyzers/security_detector.py", "r") as f:
    content = f.read()

import re

new_content = """\"\"\"Security & Vulnerability Scanner — detects hardcoded secrets and risky patterns.\"\"\"

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from .language_detector import IGNORE_DIRS

try:
    MAX_FILE_SIZE = int(os.environ.get("CODEDNA_MAX_FILE_SIZE", 5 * 1024 * 1024))
except ValueError:
    logging.warning("Invalid CODEDNA_MAX_FILE_SIZE value. Using default 5MB.")
    MAX_FILE_SIZE = 5 * 1024 * 1024
""" + "\n".join(content.split("\n")[8:])

with open("codedna/analyzers/security_detector.py", "w") as f:
    f.write(new_content)
