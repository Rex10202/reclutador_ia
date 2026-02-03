"""Detect and extract CV sections for structured processing."""

from dataclasses import dataclass
from typing import Dict, Optional

from .logging_utils import get_logger

logger = get_logger(__name__)


@dataclass
class CVSection:
    name: str
    content: str
    start_line: int
    end_line: int


class CVSectionDetector:
    """Detects standard CV sections regardless of format."""

    SECTION_KEYWORDS = {
        "experiencia": ["experiencia", "experiencia laboral", "historial laboral", "trabajo"],
        "skills": ["skills", "competencias", "habilidades", "destrezas", "técnicas"],
        "educación": ["educación", "formación", "estudios", "pregrado", "postgrado"],
        "certificaciones": ["certificaciones", "certificados", "cursos"],
        "idiomas": ["idiomas", "languages", "lenguajes"],
        "referencias": ["referencias", "recomendaciones"],
    }

    @staticmethod
    def detect_sections(text: str) -> Dict[str, CVSection]:
        lines = text.split("\n")
        sections: Dict[str, CVSection] = {}
        current_section: Optional[str] = None
        section_start = 0

        for idx, line in enumerate(lines):
            detected_section = CVSectionDetector._detect_line_is_header(line)

            if detected_section:
                if current_section:
                    sections[current_section] = CVSection(
                        name=current_section,
                        content="\n".join(lines[section_start:idx]),
                        start_line=section_start,
                        end_line=idx,
                    )

                current_section = detected_section
                section_start = idx + 1

        if current_section:
            sections[current_section] = CVSection(
                name=current_section,
                content="\n".join(lines[section_start:]),
                start_line=section_start,
                end_line=len(lines),
            )

        return sections

    @staticmethod
    def _detect_line_is_header(line: str) -> Optional[str]:
        line_lower = line.lower().strip()

        if len(line_lower) < 3:
            return None

        for section_name, keywords in CVSectionDetector.SECTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in line_lower:
                    if len(line_lower) < len(keyword) + 10:
                        return section_name

        return None
