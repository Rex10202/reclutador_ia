# Backend API - COTECMAR Reclutador IA

Arquitectura modular y escalable para análisis y matching de hojas de vida.

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application factory
│   ├── config.py                  # Configuration management
│   ├── core/
│   │   ├── exceptions.py          # Custom exceptions
│   │   ├── logger.py              # Logging setup
│   │   └── security.py            # File validation & security
│   ├── api/
│   │   └── v1/
│   │       ├── documents/         # Module 1: CV Analysis
│   │       │   └── router.py      # POST /api/v1/documents/upload
│   │       └── search/            # Module 2: NL Search (fallback)
│   │           └── router.py      # POST /api/v1/search
│   ├── services/
│   │   ├── pdf_processor.py       # PDF/DOCX text extraction
│   │   ├── cv_extractor.py        # Attribute extraction (NLP integration)
│   │   └── matching_engine.py     # Scoring & ranking
│   ├── models/
│   │   └── schemas.py             # Pydantic schemas (DTOs)
│   └── utils/
│       ├── file_handler.py        # File management utilities
│       └── validators.py          # Input validation
├── requirements.txt
├── .env
└── run.py                         # Entry point
```

## 🚀 Instalación y Ejecución

### 1. Crear virtualenv (si no existe)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# o: source venv/bin/activate  # Linux/Mac
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar servidor
```bash
python run.py
```

El servidor estará disponible en:
- **API**: http://127.0.0.1:8000
- **Swagger Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📚 API Endpoints

### Module 1: CV Analysis (Módulo Principal)

#### `POST /api/v1/documents/upload`
Subir y analizar múltiples CVs.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload" \
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

#### `GET /api/v1/documents/{document_id}`
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

#### `DELETE /api/v1/documents/{document_id}`
Eliminar un documento y su análisis.

**Response:** `204 No Content`

---

### Module 2: Natural Language Search (Fallback)

#### `POST /api/v1/search`
Búsqueda por lenguaje natural (cuando no se encuentren perfiles en CVs).

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

### 1. **API Layer** (`api/v1/`)
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
