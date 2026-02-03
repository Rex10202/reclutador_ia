# Backend API - COTECMAR Reclutador IA

API FastAPI para subir CVs, extraer atributos y comparar contra un perfil de puesto.

El extractor real vive en `packages/cv-extraction` y el backend lo carga automáticamente (vía `sys.path`).

## 📁 Estructura (relevante)

```
backend/
├── app/
│   ├── main.py                    # Crea FastAPI + agrega rutas /api/*
│   ├── api/
│   │   ├── __init__.py            # APIRouter(prefix="/api")
│   │   ├── documents/router.py    # /api/documents/* (flujo principal)
│   │   └── search/router.py       # /api/search/* (stub)
│   ├── services/                  # wrappers hacia packages/cv-extraction
│   └── models/schemas.py          # esquemas
├── requirements.txt
└── run.py                         # entrypoint uvicorn

packages/
└── cv-extraction/cv_extraction/   # extracción real (PDFProcessor + CVExtractor)
```

## 🚀 Instalación y ejecución (sin Docker)

Recomendado: crear el virtualenv en la raíz del repo (para backend + packages).

### 1) Crear y activar entorno (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Instalar dependencias
```bash
pip install -r backend/requirements.txt
```

### 3) Instalar modelo de spaCy (recomendado)
El extractor usa `es_core_news_md` para mejorar detección de rol/ubicación.
```bash
python -m spacy download es_core_news_md
```

### 4) Ejecutar el backend
```bash
python backend/run.py
```

El servidor estará disponible en:
- **API**: http://127.0.0.1:8000
- **Swagger Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

Primera ejecución (NLP): `transformers` descargará el modelo BETO `dccuchile/bert-base-spanish-wwm-cased`.
Esto puede tardar y requiere internet. Se cachea en la carpeta de Hugging Face del usuario.

Windows: por defecto `UPLOAD_TEMP_DIR` es `/tmp/uploads` y normalmente termina como `C:\\tmp\\uploads`.
Si prefieres que quede dentro del repo, define `UPLOAD_TEMP_DIR=./tmp/uploads` en `backend/.env`.

## 📚 API Endpoints

### Module 1: CV Analysis (Módulo Principal)

#### `POST /api/documents/upload`
Subir y analizar múltiples CVs.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/documents/upload" \
  -H "accept: application/json" \
  -F "files=@resume1.pdf" \
  -F "files=@resume2.pdf"
```

**Response:**
```json
[
  {
    "document_id": "uuid-here",
    "filename": "resume1.pdf",
    "status": "success",
    "extracted_attributes": [
      {
        "attribute_type": "role",
        "value": "Software Engineer",
        "confidence": 0.95,
        "source_text": "Software Engineer with 5 years..."
      }
    ],
    "raw_text_preview": "John Doe\nSoftware Engineer\n...",
    "processing_time_ms": 245.3
  }
]
```

**Validaciones:**
- Mínimo 2 archivos, máximo 10
- Formatos soportados: PDF, DOCX, DOC, TXT
- Tamaño máximo: 50MB por archivo

---

#### `GET /api/documents/{document_id}`
Recuperar análisis previo de un documento.

**Response:**
```json
{
  "document_id": "uuid-here",
  "filename": "resume1.pdf",
  "status": "success",
  "extracted_attributes": [...],
  "raw_text_preview": "..."
}
```

---

#### `DELETE /api/documents/{document_id}`
Eliminar un documento y su análisis.

**Response:** `204 No Content`

---

#### `GET /api/documents/{document_id}/file`
Devuelve el archivo original (PDF) para visualizarlo (iframe / nueva pestaña).

### Search (placeholder)

#### `POST /api/search`
Actualmente es un stub (no usado por el frontend).

**Request:**
```json
{
  "text": "Ingeniero de software con 5 años en Python y React, ubicado en Bogotá"
}
```

**Response:**
```json
{
  "candidates": [
    {
      "id": "123",
      "role": "Software Engineer",
      "score": 0.92,
      "location": "Bogotá",
      "years_experience": 5,
      "languages": "Spanish;English",
      "skills": "Python;React;PostgreSQL"
    }
  ],
  "parsed_query": {
    "role": "Software Engineer",
    "skills": ["Python", "React"],
    "experience_years": 5,
    "location": "Bogotá",
    "languages": ["Spanish", "English"]
  },
  "total_results": 15
}
```

---

### Health Checks

#### `GET /health`
Estado general del servicio.

**Response:**
```json
{
  "status": "ok",
  "service": "reclutador_ia_backend"
}
```

---

#### `GET /health/ready`
Verificación de preparación para recibir requests.

**Response:**
```json
{
  "ready": true,
  "timestamp": "2025-12-11T10:30:45.123Z"
}
```

---

## 🔧 Configuración

Todas las variables de configuración están en `backend/.env`:

```env
# API
HOST=127.0.0.1
PORT=8000
DEBUG=True
RELOAD=True

# CORS (Frontend)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000

# File Upload
MAX_FILE_SIZE_MB=50
MAX_UPLOAD_FILES=10
UPLOAD_TEMP_DIR=/tmp/uploads

# NLP & Models
MODELS_PATH=./models
NLP_PARSER_MODEL=beto
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# Logging
LOG_LEVEL=INFO
```

## 🏗️ Arquitectura de Capas

### 1. **API Layer** (`api/`)
- Rutas HTTP
- Validación de requests (Pydantic)
- Manejo de errores
- Documentación automática (Swagger)

### 2. **Service Layer** (`services/`)
- `PDFProcessor`: Extracción de texto de documentos
- `CVExtractor`: Análisis NLP de atributos
- `MatchingEngine`: Scoring y ranking

### 3. **Core Layer** (`core/`)
- `exceptions.py`: Excepciones personalizadas
- `logger.py`: Sistema de logging centralizado
- `security.py`: Validaciones de archivos

### 4. **Models Layer** (`models/`)
- Pydantic schemas (DTOs)
- Validación de datos centralizada
- Documentación automática de tipos

### 5. **Utils Layer** (`utils/`)
- Funciones utilitarias
- Validadores personalizados
- Manejo de archivos

## ✨ Características

✅ **Modularidad**: Fácil de escalar y mantener
✅ **Type Hints**: Python 3.9+ con tipos completos
✅ **Validación**: Pydantic + custom validators
✅ **Documentación**: Swagger automático + docstrings
✅ **Error Handling**: Excepciones consistentes
✅ **Logging**: Sistema centralizado
✅ **CORS**: Configuración flexible para frontend
✅ **Async**: Operaciones asincrónicas para mejor performance

## 🔌 Integración con Módulos Existentes

### NLP Module
El `CVExtractor` integrará con `NLP/src/parser.py` para:
- Detección de roles (BETO embeddings)
- Extracción de skills
- Cálculo de años de experiencia
- Detección de ubicación e idiomas

### Ranking Model
El `MatchingEngine` integrará con `ranking_model/` para:
- Cálculo de embeddings semánticos
- Scoring de candidatos
- Aplicación de filtros (lexical + semantic)

## 📝 Próximos Pasos

- [ ] Integración completa con NLP module
- [ ] Integración con ranking_model
- [ ] Implementar persistencia de documentos (DB)
- [ ] Caché de embeddings
- [ ] Tests unitarios y E2E
- [ ] Docker containerization
- [ ] CI/CD pipeline

## 📧 Contacto

Equipo COTECMAR
