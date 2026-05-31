"""Dependency Mapper — parses import statements and builds a dependency graph."""

from __future__ import annotations

import itertools
import logging
import os
import re
from pathlib import Path

from .language_detector import IGNORE_DIRS

try:
    MAX_FILE_SIZE = int(os.environ.get("CODEDNA_MAX_FILE_SIZE", 5 * 1024 * 1024))
except ValueError:
    logging.getLogger(__name__).warning("Invalid CODEDNA_MAX_FILE_SIZE value. Using default 5MB.")
    MAX_FILE_SIZE = 5 * 1024 * 1024
