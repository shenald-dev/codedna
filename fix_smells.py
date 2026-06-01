with open("codedna/analyzers/code_smell_detector.py", "r") as f:
    content = f.read()

import re

# Fix indentation and missing imports
new_content = """\"\"\"Code Smell Detector — identifies structural design problems in codebases.\"\"\"

from __future__ import annotations

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
""" + "\n".join(content.split("\n")[7:])

with open("codedna/analyzers/code_smell_detector.py", "w") as f:
    f.write(new_content)
