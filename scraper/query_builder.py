"""
Constructor de URLs de búsqueda a partir de parámetros extraídos.
"""

from urllib.parse import quote_plus
from scraper.nlp_extractor import SearchParams


class URLBuilder:
    """
    Construye URLs de búsqueda para diferentes plataformas.
    """
    
    @staticmethod
    def build_linkedin_url(params: SearchParams) -> str:
        """
        Construye URL de búsqueda directa de LinkedIn.
        NOTA: LinkedIn bloquea frecuentemente. Usar con precaución.
        """
        query_parts = []
        
        if params.role:
            query_parts.append(params.role)
        if params.skills:
            query_parts.append(params.skills)
        if params.location:
            query_parts.append(params.location)
        
        full_query = " ".join(query_parts)
        encoded = quote_plus(full_query)
        
        return f"https://www.linkedin.com/search/results/people/?keywords={encoded}"

    @staticmethod
    def build_google_dork_url(params: SearchParams) -> str:
        """
        Construye URL usando Google Dorking para buscar perfiles de LinkedIn.
        RECOMENDADO: Google es más permisivo que LinkedIn directo.
        
        Ejemplo resultado:
        https://www.google.com/search?q=site:linkedin.com/in/+"ingeniero"+"cartagena"
        """
        query_parts = ['site:linkedin.com/in/']
        
        if params.role:
            query_parts.append(f'"{params.role}"')
        if params.location:
            query_parts.append(f'"{params.location}"')
        if params.skills:
            # Agregar skills principales
            for skill in params.skills.split(",")[:2]:
                skill = skill.strip()
                if skill:
                    query_parts.append(f'"{skill}"')
        
        full_query = " ".join(query_parts)
        return f"https://www.google.com/search?q={quote_plus(full_query)}"

    @staticmethod
    def build_url(params: SearchParams, strategy: str = "google") -> str:
        """
        Construye URL según la estrategia elegida.
        
        Args:
            params: Parámetros de búsqueda
            strategy: "google" (recomendado) o "linkedin" (riesgo de bloqueo)
        """
        if strategy == "linkedin":
            return URLBuilder.build_linkedin_url(params)
        else:
            return URLBuilder.build_google_dork_url(params)