"""
Scraper principal que integra: NLP -> URL -> Katana -> Parser
"""

import random
from typing import List
from scraper.katana_wrapper import KatanaWrapper, KatanaConfig
from scraper.profile_parser import CandidatoPerfil, LinkedInParser, GoogleResultParser
from scraper.nlp_extractor import NLPKeywordExtractor, SearchParams
from scraper.query_builder import URLBuilder


class LinkedInScraper:
    """
    Scraper de LinkedIn usando Katana.
    
    Flujo:
    1. Recibe texto en lenguaje natural
    2. NLP extrae keywords (rol, ubicación, skills)
    3. Construye URL de búsqueda
    4. Katana hace crawling
    5. Parser extrae datos estructurados
    """
    
    def __init__(self, use_katana: bool = True):
        self.use_katana = use_katana
        self.nlp = NLPKeywordExtractor()
        self.parser = LinkedInParser()
        self.google_parser = GoogleResultParser()
        
        if use_katana:
            try:
                self.katana = KatanaWrapper()
            except FileNotFoundError as e:
                print(f"[WARN] {e}")
                self.katana = None
                self.use_katana = False
        else:
            self.katana = None

    def search_from_text(self, query: str, max_candidates: int = 5) -> List[CandidatoPerfil]:
        """
        Flujo completo: Texto Natural -> Candidatos
        
        Args:
            query: Consulta en lenguaje natural
            max_candidates: Cantidad máxima de candidatos
            
        Returns:
            Lista de CandidatoPerfil
        """
        print("\n" + "="*60)
        print("[1. NLP] Analizando consulta...")
        print("="*60)
        
        # 1. EXTRAER KEYWORDS
        params = self.nlp.extract(query)
        print(f"   Rol detectado:  {params.role}")
        print(f"   Ubicación:      {params.location}")
        print(f"   Skills:         {params.skills}")
        print(f"   Experiencia:    {params.experience_years} años")
        print(f"   Idiomas:        {params.languages}")

        # 2. CONSTRUIR URL
        print("\n" + "="*60)
        print("[2. URL BUILDER] Generando URL de búsqueda...")
        print("="*60)
        
        target_url = URLBuilder.build_google_dork_url(params)
        print(f"   URL generada: {target_url}")

        candidatos = []

        # 3. EJECUTAR KATANA
        if self.use_katana and self.katana:
            print("\n" + "="*60)
            print("[3. KATANA] Iniciando crawling...")
            print("="*60)
            
            config = KatanaConfig(depth=2, headless=True, timeout=90)
            
            try:
                raw_data = self.katana.crawl_and_capture(target_url, config)
                
                # 4. PARSEAR RESULTADOS
                print("\n" + "="*60)
                print(f"[4. PARSER] Procesando {len(raw_data)} respuestas...")
                print("="*60)
                
                linkedin_urls_found = set()
                
                for item in raw_data:
                    if len(candidatos) >= max_candidates:
                        break
                    
                    body = item.get("response", {}).get("body", "")
                    url = item.get("request", {}).get("endpoint", "") or item.get("url", "")
                    
                    # Si es resultado de Google, extraer URLs de LinkedIn
                    if "google.com" in url:
                        found_urls = self.google_parser.extract_linkedin_urls(body)
                        linkedin_urls_found.update(found_urls)
                    
                    # Si ya es un perfil de LinkedIn
                    elif "linkedin.com/in/" in url:
                        perfil = self.parser.parse(body, url)
                        if perfil and perfil.nombre:
                            candidatos.append(perfil)
                            print(f"   [+] Extraído: {perfil.nombre}")
                
                # Crear candidatos desde URLs encontradas en Google
                for linkedin_url in list(linkedin_urls_found)[:max_candidates - len(candidatos)]:
                    # Extraer nombre del URL
                    if "/in/" in linkedin_url:
                        slug = linkedin_url.split("/in/")[-1].strip("/")
                        nombre = slug.replace("-", " ").title()
                        
                        candidatos.append(CandidatoPerfil(
                            nombre=nombre,
                            cargo=params.role.title() if params.role else "Profesional",
                            habilidades=params.skills,
                            experiencia_anios=params.experience_years,
                            idiomas=params.languages,
                            ubicacion=params.location,
                            fuente="LinkedIn (via Google)",
                            url_perfil=linkedin_url
                        ))
                        print(f"   [+] Perfil encontrado: {nombre}")
                        
            except Exception as e:
                print(f"[ERROR] Falló Katana: {e}")

        # 5. FALLBACK: Datos sintéticos si no hay resultados
        if not candidatos:
            print("\n" + "="*60)
            print("[5. FALLBACK] Generando datos sintéticos...")
            print("="*60)
            print("   (Katana no extrajo perfiles. Usando simulación para demo)")
            candidatos = self._generate_mock_candidates(params, max_candidates)

        return candidatos

    def _generate_mock_candidates(self, params: SearchParams, count: int) -> List[CandidatoPerfil]:
        """Genera candidatos simulados basados en los parámetros del NLP."""
        nombres = [
            "Carlos Méndez", "María García", "Juan Rodríguez",
            "Ana López", "Pedro Martínez", "Laura Sánchez",
            "Diego Hernández", "Sofia Castro", "Andrés Moreno",
            "Valentina Ruiz", "Felipe Torres", "Camila Vargas"
        ]
        
        random.shuffle(nombres)
        
        candidatos = []
        for i in range(min(count, len(nombres))):
            exp = params.experience_years if params.experience_years > 0 else random.randint(2, 8)
            
            candidatos.append(CandidatoPerfil(
                nombre=nombres[i],
                cargo=params.role.title() if params.role else "Profesional",
                habilidades=params.skills if params.skills else "Habilidades Generales",
                experiencia_anios=exp + random.randint(-1, 2),
                idiomas=params.languages if params.languages else "Español",
                ubicacion=params.location if params.location else "Colombia",
                modalidad=random.choice(["Presencial", "Remoto", "Híbrido"]),
                disponibilidad=random.choice(["Inmediata", "2 semanas", "1 mes"]),
                fuente="Simulación (Demo)",
                url_perfil=f"https://linkedin.com/in/{nombres[i].lower().replace(' ', '-')}"
            ))
        
        return candidatos