"""Detect and extract CV sections for structured processing."""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CVSection:
    """Represents a section of a CV."""
    name: str
    content: str
    start_line: int
    end_line: int


class CVSectionDetector:
    """Detects standard CV sections regardless of format."""

    # Palabras clave que indican secciones comunes
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
        """
        Detect major CV sections from raw text.
        
        Args:
            text: Cleaned CV text
            
        Returns:
            Dictionary mapping section names to CVSection objects
        """
        lines = text.split('\n')
        sections = {}
        current_section = None
        section_start = 0

        for idx, line in enumerate(lines):
            detected_section = CVSectionDetector._detect_line_is_header(line)
            
            if detected_section:
                # Save previous section
                if current_section:
                    sections[current_section] = CVSection(
                        name=current_section,
                        content='\n'.join(lines[section_start:idx]),
                        start_line=section_start,
                        end_line=idx
                    )
                
                # Start new section
                current_section = detected_section
                section_start = idx + 1

        # Save last section
        if current_section:
            sections[current_section] = CVSection(
                name=current_section,
                content='\n'.join(lines[section_start:]),
                start_line=section_start,
                end_line=len(lines)
            )

        return sections

    @staticmethod
    def _detect_line_is_header(line: str) -> Optional[str]:
        """Detect if line is a section header."""
        line_lower = line.lower().strip()
        
        # Avoid empty lines and very short lines
        if len(line_lower) < 3:
            return None
        
        # Check for common header patterns
        for section_name, keywords in CVSectionDetector.SECTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in line_lower:
                    # Must be mostly the keyword (not a sentence)
                    if len(line_lower) < len(keyword) + 10:
                        return section_name
        
        return None