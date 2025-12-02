"""
Wrapper para ejecutar Katana desde Python.
Katana debe estar instalado: go install github.com/projectdiscovery/katana/cmd/katana@latest
"""

import subprocess
import json
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class KatanaConfig:
    """Configuración para Katana."""
    depth: int = 2
    headless: bool = True
    js_crawl: bool = True
    timeout: int = 60
    rate_limit: int = 1
    concurrency: int = 2


class KatanaWrapper:
    """
    Wrapper para ejecutar Katana como subprocess.
    """
    
    def __init__(self):
        self.katana_path = self._find_katana()
        
    def _find_katana(self) -> str:
        """Encuentra la ruta de Katana en el sistema."""
        # 1. Buscar en PATH global
        katana_global = shutil.which("katana")
        if katana_global:
            return katana_global
        
        # 2. Buscar en carpeta de Go (Windows)
        go_bin = Path.home() / "go" / "bin" / "katana.exe"
        if go_bin.exists():
            return str(go_bin)
        
        # 3. Buscar en carpeta local del proyecto
        local_exe = Path(__file__).parent / "katana.exe"
        if local_exe.exists():
            return str(local_exe)
        
        raise FileNotFoundError(
            "Katana no encontrado. Instálalo con:\n"
            "go install github.com/projectdiscovery/katana/cmd/katana@latest"
        )

    def crawl_and_capture(self, url: str, config: KatanaConfig = None) -> List[Dict[str, Any]]:
        """
        Ejecuta Katana y captura las respuestas en formato JSON.
        
        Args:
            url: URL objetivo
            config: Configuración de Katana
            
        Returns:
            Lista de respuestas JSON con URL, headers, body, etc.
        """
        if config is None:
            config = KatanaConfig()

        # Construir comando
        cmd = [
            self.katana_path,
            "-u", url,
            "-d", str(config.depth),
            "-jc",                          # Javascript Crawling
            "-headless",                    # Navegador oculto
            "-json",                        # Salida JSON
            "-silent",                      # Sin banner
            "-c", str(config.concurrency),  # Concurrencia
            "-rl", str(config.rate_limit),  # Rate limit
            "-timeout", str(config.timeout)
        ]

        print(f"[KATANA] Ejecutando crawling...")
        print(f"[KATANA] Target: {url}")
        
        results = []
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Leer salida línea por línea
            for line in process.stdout:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        results.append(data)
                        
                        # Mostrar progreso
                        found_url = data.get("request", {}).get("endpoint", "") or data.get("url", "")
                        if found_url:
                            print(f"[KATANA] Encontrado: {found_url[:80]}...")
                            
                    except json.JSONDecodeError:
                        continue
            
            process.wait()
            
        except FileNotFoundError:
            print(f"[ERROR] No se puede ejecutar Katana desde: {self.katana_path}")
        except Exception as e:
            print(f"[ERROR] Error ejecutando Katana: {e}")

        print(f"[KATANA] Total respuestas capturadas: {len(results)}")
        return results

    def is_installed(self) -> bool:
        """Verifica si Katana está instalado."""
        try:
            result = subprocess.run(
                [self.katana_path, "-version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False