"""
CLI principal del módulo de scraping.
Uso: python -m scraper.main --query "Busco ingeniero en Cartagena"
"""

import argparse
import sys
import json
from pathlib import Path

# Asegurar imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.linkedin_scraper import LinkedInScraper
from app.db import get_connection


def guardar_en_db(candidatos) -> int:
    """Guarda candidatos en la base de datos SQLite."""
    if not candidatos:
        return 0
    
    conn = get_connection()
    cursor = conn.cursor()
    count = 0
    
    for c in candidatos:
        try:
            cursor.execute("""
                INSERT INTO candidatos 
                (nombre, cargo, habilidades, experiencia_anios, idiomas, ubicacion, modalidad, disponibilidad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, c.to_db_tuple())
            count += 1
        except Exception as e:
            print(f"   [!] Error guardando {c.nombre}: {e}")
    
    conn.commit()
    conn.close()
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Reclutador IA - Módulo de Scraping con Katana",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python -m scraper.main --query "Busco ingeniero de mantenimiento con SAP en Cartagena"
  python -m scraper.main --query "Necesito desarrollador Python en Bogotá" --cantidad 10
  python -m scraper.main --query "Analista de datos" --guardar-db --output resultados.json
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        required=True,
        help="Consulta en lenguaje natural"
    )
    parser.add_argument(
        "--cantidad", "-n",
        type=int,
        default=5,
        help="Cantidad máxima de candidatos (default: 5)"
    )
    parser.add_argument(
        "--guardar-db", "-g",
        action="store_true",
        help="Guardar resultados en la base de datos"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Exportar resultados a archivo JSON"
    )
    parser.add_argument(
        "--no-katana",
        action="store_true",
        help="Desactivar Katana (solo usar mock)"
    )
    
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  RECLUTADOR IA - MÓDULO DE SCRAPING")
    print("  Pipeline: Query -> NLP -> URL -> Katana -> BD")
    print("="*60)
    print(f"\n[INPUT] Consulta: '{args.query}'")
    print(f"[CONFIG] Cantidad: {args.cantidad} | Guardar BD: {args.guardar_db}")

    # Crear scraper
    scraper = LinkedInScraper(use_katana=not args.no_katana)
    
    # Ejecutar búsqueda
    candidatos = scraper.search_from_text(args.query, max_candidates=args.cantidad)

    # Mostrar resultados
    print("\n" + "="*60)
    print(f"[RESULTADOS] {len(candidatos)} candidatos encontrados")
    print("="*60)
    
    for i, c in enumerate(candidatos, 1):
        print(f"\n  {i}. {c.nombre}")
        print(f"     Cargo: {c.cargo}")
        print(f"     Skills: {c.habilidades}")
        print(f"     Experiencia: {c.experiencia_anios} años")
        print(f"     Ubicación: {c.ubicacion}")
        print(f"     Idiomas: {c.idiomas}")
        print(f"     URL: {c.url_perfil}")
        print(f"     Fuente: {c.fuente}")

    # Guardar en BD
    if args.guardar_db and candidatos:
        print("\n" + "="*60)
        print("[BD] Guardando candidatos...")
        print("="*60)
        n = guardar_en_db(candidatos)
        print(f"   {n} candidatos guardados exitosamente.")

    # Exportar JSON
    if args.output and candidatos:
        output_data = {
            "query": args.query,
            "total": len(candidatos),
            "candidatos": [c.to_dict() for c in candidatos]
        }
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"\n[OUTPUT] Resultados exportados a: {args.output}")

    print("\n" + "="*60)
    print("  PROCESO COMPLETADO")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()