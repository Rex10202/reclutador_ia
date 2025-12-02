"""
Parsers para extraer datos estructurados de perfiles HTML.
"""

import re
from dataclasses import dataclass, field
from typing import Optional, Tuple
from bs4 import BeautifulSoup


@dataclass
class CandidatoPerfil:
    """Estructura de datos de un candidato."""
    nombre: str = ""
    cargo: str = ""
    habilidades: str = ""
    experiencia_anios: int = 0
    idiomas: str = "Español"
    ubicacion: str = ""
    modalidad: str = "Presencial"
    disponibilidad: str = "Consultar"
    fuente: str = "LinkedIn"
    url_perfil: str = ""
    
    def to_dict(self):
        return {
            "nombre": self.nombre,
            "cargo": self.cargo,
            "habilidades": self.habilidades,
            "experiencia_anios": self.experiencia_anios,
            "idiomas": self.idiomas,
            "ubicacion": self.ubicacion,
            "modalidad": self.modalidad,
            "disponibilidad": self.disponibilidad,
            "fuente": self.fuente,
            "url_perfil": self.url_perfil
        }
    
    def to_db_tuple(self) -> Tuple:
        """Retorna tupla para insertar en SQLite."""
        return (
            self.nombre,
            self.cargo,
            self.habilidades,
            self.experiencia_anios,
            self.idiomas,
            self.ubicacion,
            self.modalidad,
            self.disponibilidad
        )


class LinkedInParser:
    """
    Parser para extraer datos de perfiles de LinkedIn.
    NOTA: LinkedIn cambia su HTML frecuentemente. Este parser es aproximado.
    """
    
    def parse(self, html: str, url: str = "") -> Optional[CandidatoPerfil]:
        """
        Intenta extraer datos de un HTML de LinkedIn.
        """
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraer nombre
        nombre = self._extract_name(soup, url)
        if not nombre:
            return None
        
        # Extraer otros campos
        cargo = self._extract_title(soup)
        ubicacion = self._extract_location(soup)
        
        return CandidatoPerfil(
            nombre=nombre,
            cargo=cargo,
            habilidades="",  # Requiere parsing más profundo
            experiencia_anios=0,
            idiomas="Español",
            ubicacion=ubicacion,
            fuente="LinkedIn (Katana)",
            url_perfil=url
        )
    
    def _extract_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extrae el nombre del perfil."""
        # Intentar desde H1
        h1 = soup.find("h1")
        if h1 and h1.text.strip():
            return h1.text.strip()
        
        # Intentar desde título de página
        title = soup.find("title")
        if title:
            # LinkedIn titles: "Nombre Apellido | LinkedIn"
            text = title.text.split("|")[0].strip()
            text = text.split("-")[0].strip()
            if text and "LinkedIn" not in text:
                return text
        
        # Fallback: extraer del URL
        if "/in/" in url:
            slug = url.split("/in/")[-1].strip("/").split("?")[0]
            # Convertir "juan-perez-123abc" -> "Juan Perez"
            name = "-".join(slug.split("-")[:-1]) if slug[-1].isdigit() else slug
            return name.replace("-", " ").title()
        
        return ""
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extrae el cargo/título."""
        # Buscar en meta description
        meta = soup.find("meta", {"name": "description"})
        if meta:
            content = meta.get("content", "")
            # Típico: "Nombre - Cargo en Empresa"
            if " - " in content:
                return content.split(" - ")[1].split(" en ")[0].strip()
        
        return "Profesional"
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extrae la ubicación."""
        # Buscar en meta o texto
        meta = soup.find("meta", {"name": "geo.placename"})
        if meta:
            return meta.get("content", "")
        
        return "No especificado"


class GoogleResultParser:
    """
    Parser para extraer URLs de LinkedIn desde resultados de Google.
    """
    
    def extract_linkedin_urls(self, html: str) -> list:
        """Extrae URLs de perfiles de LinkedIn desde resultados de Google."""
        urls = []
        
        # Buscar todos los links
        pattern = r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9\-]+'
        matches = re.findall(pattern, html)
        
        for url in matches:
            if url not in urls:
                urls.append(url)
        
        return urls