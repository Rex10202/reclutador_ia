"""
Extractor de keywords desde consultas en lenguaje natural.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchParams:
    """Parámetros de búsqueda extraídos del texto."""
    role: str = ""
    location: str = ""
    skills: str = ""
    experience_years: int = 0
    languages: str = ""
    
    def to_dict(self):
        return {
            "role": self.role,
            "location": self.location,
            "skills": self.skills,
            "experience_years": self.experience_years,
            "languages": self.languages
        }


class NLPKeywordExtractor:
    """
    Extrae keywords estructurados desde una consulta en lenguaje natural.
    
    Ejemplo:
        Input: "Busco ingeniero de mantenimiento con SAP PM en Cartagena"
        Output: SearchParams(role="ingeniero de mantenimiento", location="Cartagena", skills="SAP PM")
    """
    
    # Ciudades conocidas de Colombia
    KNOWN_CITIES = [
        "cartagena", "bogota", "bogotá", "medellin", "medellín",
        "cali", "barranquilla", "bucaramanga", "pereira", "manizales",
        "santa marta", "ibague", "ibagué", "cucuta", "cúcuta",
        "villavicencio", "pasto", "monteria", "montería", "neiva"
    ]
    
    # Skills/tecnologías comunes
    KNOWN_SKILLS = [
        "sap", "sap pm", "sap mm", "sap fi", "python", "java", "sql",
        "excel", "power bi", "tableau", "aws", "azure", "git",
        "mantenimiento preventivo", "mantenimiento correctivo",
        "lean", "six sigma", "scrum", "jira", "autocad", "solidworks"
    ]

    def extract(self, query: str) -> SearchParams:
        """
        Extrae parámetros de búsqueda desde texto natural.
        """
        query_lower = query.lower()
        
        role = self._extract_role(query_lower)
        location = self._extract_location(query_lower)
        skills = self._extract_skills(query_lower)
        experience = self._extract_experience(query_lower)
        languages = self._extract_languages(query_lower)
        
        return SearchParams(
            role=role,
            location=location,
            skills=skills,
            experience_years=experience,
            languages=languages
        )

    def _extract_role(self, query: str) -> str:
        """Extrae el rol/cargo buscado."""
        patterns = [
            r"(?:busco|necesito|requiero)\s+(?:un|una)?\s*([a-záéíóúñ\s]+?)(?:\s+con|\s+en|\s+que|,|$)",
            r"(?:perfil de|cargo de)\s+([a-záéíóúñ\s]+?)(?:\s+con|\s+en|,|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                role = match.group(1).strip()
                # Limpiar palabras innecesarias
                role = re.sub(r'\b(un|una|el|la|los|las)\b', '', role).strip()
                if len(role) > 3:
                    return role
        
        return "profesional"

    def _extract_location(self, query: str) -> str:
        """Extrae la ubicación."""
        # Buscar ciudades conocidas
        for city in self.KNOWN_CITIES:
            if city in query:
                return city.title()
        
        # Patrón general: "en [ciudad]"
        match = re.search(r"\ben\s+([a-záéíóúñ]+)(?:\s|,|$)", query)
        if match:
            return match.group(1).title()
        
        return "Colombia"

    def _extract_skills(self, query: str) -> str:
        """Extrae habilidades/tecnologías."""
        found_skills = []
        
        # Buscar skills conocidos
        for skill in self.KNOWN_SKILLS:
            if skill in query:
                found_skills.append(skill.upper() if len(skill) <= 4 else skill.title())
        
        # Patrón: "con [skill]" o "sepa [skill]"
        match = re.search(r"(?:con|sepa|maneje|experiencia en)\s+([a-záéíóúñ0-9\s,]+?)(?:\s+en|\s+que|,|$)", query)
        if match:
            extra = match.group(1).strip()
            if extra and extra not in [s.lower() for s in found_skills]:
                found_skills.append(extra)
        
        return ", ".join(found_skills) if found_skills else ""

    def _extract_experience(self, query: str) -> int:
        """Extrae años de experiencia."""
        patterns = [
            r"(\d+)\s*(?:años|años de experiencia)",
            r"(?:mínimo|minimo|al menos)\s*(\d+)\s*años",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))
        
        return 0

    def _extract_languages(self, query: str) -> str:
        """Extrae idiomas requeridos."""
        languages = []
        
        if "inglés" in query or "ingles" in query:
            languages.append("Inglés")
        if "francés" in query or "frances" in query:
            languages.append("Francés")
        if "portugués" in query or "portugues" in query:
            languages.append("Portugués")
        
        return ", ".join(languages) if languages else "Español"