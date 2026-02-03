# Reclutador IA

App para subir hojas de vida, extraer atributos y comparar candidatos contra un perfil de puesto.

- Backend: FastAPI en `backend/`
- Frontend: Next.js en `frontend/`
- Extracción real: `packages/cv-extraction` (cargada por el backend)

## Ejecutar (sin Docker)

### 1) Backend (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python -m spacy download es_core_news_md
python backend/run.py
```

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

Nota: en la primera ejecución, `transformers` puede descargar BETO (`dccuchile/bert-base-spanish-wwm-cased`).

### 2) Frontend
```bash
cd frontend
npm install
npm run dev
```

- UI: http://localhost:3000

## Endpoints principales

- `POST /api/documents/upload`
- `POST /api/documents/analyze`
- `GET /api/documents/{id}`
- `GET /api/documents/{id}/file`