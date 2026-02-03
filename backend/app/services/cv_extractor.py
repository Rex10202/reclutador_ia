"""Backend wrapper for CV extraction.

The implementation lives in packages/cv-extraction so it can be developed
independently. This module remains to preserve existing backend imports.
"""

from cv_extraction.cv_extractor import CVExtractor

__all__ = ["CVExtractor"]