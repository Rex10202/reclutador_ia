"""
Utilidades auxiliares para el módulo de scraping.
"""

def clean_text(text: str) -> str:
    """Limpia texto removiendo espacios extra."""
    if not text:
        return ""
    return " ".join(text.split())