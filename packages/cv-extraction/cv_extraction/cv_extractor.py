"""CV attribute extraction service.

This module wraps the NLP package when available, and falls back to
simple heuristics when it's not.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .logging_utils import get_logger

logger = get_logger(__name__)


class CVExtractor:
    """Extracts attributes from CV text using NLP when available."""

    @staticmethod
    def extract_attributes(cv_text: str, document_id: str) -> List[Dict]:
        # Lazy import NLP so that missing heavy deps don't break backend startup.
        nlp = CVExtractor._try_load_nlp()
        if nlp is None:
            logger.warning("Using fallback extraction (NLP not available)")
            return CVExtractor._fallback_extraction(cv_text)

        get_doc, detect_role, detect_skills, extract_experience, extract_languages, extract_location, config_dir = nlp

        try:
            doc = get_doc(cv_text)
            noun_chunks = [chunk.text for chunk in getattr(doc, "noun_chunks", [])]

            cities = CVExtractor._load_json_list(config_dir / "cities_co.json")
            languages_catalog = CVExtractor._load_json_list(config_dir / "languages.json")

            extracted = {
                "role": detect_role(cv_text, noun_chunks),
                "skills": detect_skills(cv_text, noun_chunks),
                "years_experience": extract_experience(cv_text),
                "languages": extract_languages(cv_text, languages_catalog),
                "location": extract_location(doc, cities),
                "document_id": document_id,
            }

            attributes: List[Dict] = []

            if extracted["role"]:
                attributes.append(
                    {
                        "attribute_type": "role",
                        "value": str(extracted["role"]),
                        "confidence": 0.85,
                        "source_text": None,
                    }
                )

            if extracted["skills"]:
                skills_str = (
                    "; ".join(extracted["skills"])
                    if isinstance(extracted["skills"], list)
                    else str(extracted["skills"])
                )
                attributes.append(
                    {
                        "attribute_type": "skills",
                        "value": skills_str,
                        "confidence": 0.8,
                        "source_text": None,
                    }
                )

            if extracted["years_experience"] is not None:
                attributes.append(
                    {
                        "attribute_type": "years_experience",
                        "value": str(extracted["years_experience"]),
                        "confidence": 0.9,
                        "source_text": None,
                    }
                )

            if extracted["languages"]:
                langs_str = (
                    "; ".join(extracted["languages"])
                    if isinstance(extracted["languages"], list)
                    else str(extracted["languages"])
                )
                attributes.append(
                    {
                        "attribute_type": "languages",
                        "value": langs_str,
                        "confidence": 0.75,
                        "source_text": None,
                    }
                )

            if extracted["location"]:
                attributes.append(
                    {
                        "attribute_type": "location",
                        "value": str(extracted["location"]),
                        "confidence": 0.8,
                        "source_text": None,
                    }
                )

            logger.info(f"Extracted {len(attributes)} attributes for document {document_id}")
            return attributes

        except Exception as e:
            logger.error(f"Error extracting attributes with NLP: {str(e)}")
            return CVExtractor._fallback_extraction(cv_text)

    @staticmethod
    def _try_load_nlp():
        try:
            from NLP.src.spacy_utils import get_doc
            from NLP.src.parser import _detect_role, _detect_skills
            from NLP.src.extract_rules import (
                extract_experience,
                extract_languages,
                extract_location,
            )
            import NLP  # type: ignore

            config_dir = Path(NLP.__file__).resolve().parent / "config"
            return (
                get_doc,
                _detect_role,
                _detect_skills,
                extract_experience,
                extract_languages,
                extract_location,
                config_dir,
            )
        except Exception as e:
            logger.warning(f"NLP module not available: {e}.")
            return None

    @staticmethod
    def _load_json_list(path: Path) -> List[str]:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    @staticmethod
    def _fallback_extraction(cv_text: str) -> List[Dict]:
        import re

        attributes: List[Dict] = []

        exp_match = re.search(r"(\d+)\s*\+?\s*(?:años|years)", cv_text.lower())
        if exp_match:
            attributes.append(
                {
                    "attribute_type": "years_experience",
                    "value": exp_match.group(1),
                    "confidence": 0.6,
                    "source_text": None,
                }
            )

        cities = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Bogota"]
        for city in cities:
            if city.lower() in cv_text.lower():
                attributes.append(
                    {
                        "attribute_type": "location",
                        "value": city,
                        "confidence": 0.6,
                        "source_text": None,
                    }
                )
                break

        languages = ["Spanish", "English", "Español", "Inglés"]
        found_langs = [lang for lang in languages if lang.lower() in cv_text.lower()]
        if found_langs:
            attributes.append(
                {
                    "attribute_type": "languages",
                    "value": "; ".join(found_langs),
                    "confidence": 0.5,
                    "source_text": None,
                }
            )

        logger.info(f"Fallback extraction: {len(attributes)} attributes found")
        return attributes
