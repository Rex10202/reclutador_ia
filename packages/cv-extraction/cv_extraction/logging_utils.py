"""Minimal logging utilities for the cv_extraction package."""

import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name or "cv_extraction")
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO)
    return logger
