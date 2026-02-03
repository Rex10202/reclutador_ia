# Arquitectura del Proyecto (estado actual)

Este documento describe **lo que está en uso y funcional** hoy en el repo (Feb 2026). También lista módulos presentes pero **no conectados** o **parcialmente implementados**.

## Vista general

### Qué se considera “funcional” en este repo

- Subir CVs (PDF/DOCX/TXT) → extracción de texto → extracción de atributos → respuesta con `warnings`.
- Analizar CVs contra requisitos del puesto → ranking simple + `concerns` (y también `warnings`).
- Ver el archivo original subido (inline) y ver el “preview” del texto extraído.

## Estructura de directorios (en uso)

Árbol resumido de lo que participa en el flujo principal:

```
reclutador_ia/
  backend/
    run.py
    requirements.txt
    app/
      main.py
      config.py
      api/
        __init__.py
        documents/
          router.py
          __init__.py
        search/
          router.py            # existe, pero no está implementado (501)
          __init__.py
      core/
        security.py
        logger.py
        exceptions.py
        __init__.py
      models/
        schemas.py
        __init__.py
      services/                # wrappers que delegan a packages/
        cv_extractor.py
        pdf_processor.py
        document_normalizer.py
        section_detector.py
        matching_engine.py
        __init__.py
      utils/
        file_handler.py
        validators.py
        __init__.py

  frontend/
    package.json
    app/
      layout.tsx
      page.tsx
      globals.css
    components/
      DocumentUploader.tsx
      JobDescriptionInput.tsx
      InsightFilters.tsx
      TalentSummary.tsx
      CandidatesCard.tsx
      ProfilePanel.tsx
      SearchBar.tsx            # existe, pero no está conectado en page.tsx
    lib/
      api.ts
      types.ts
    public/
      CotecmarLogo.png

  packages/
    cv-extraction/
      cv_extraction/
        cv_extractor.py
        pdf_processor.py
        section_detector.py
        document_normalizer.py
        exceptions.py
        logging_utils.py
        __init__.py
    NLP/                       # opcional (no requerido para el flujo básico)
      config/
      src/
      data/
      tests/
      __init__.py
    ranking/                   # presente; no es parte del flujo principal actual
      src/
      data/
      tests/
```

## Flujos HTTP (contrato real)

### 1) Upload + extracción base

- **Frontend**: [frontend/app/page.tsx](frontend/app/page.tsx) → `DocumentUploader`
- **Backend**: [backend/app/api/documents/router.py](backend/app/api/documents/router.py)

Request:
- `POST /api/documents/upload` (multipart)

Response (por archivo):
- `document_id`, `extracted_attributes[]`, `raw_text_preview`, `warnings[]`.

Notas de confiabilidad:
- Si `role` o `location` vienen “detectados” pero **no se pueden verificar** dentro del texto del CV, se eliminan de `extracted_attributes` y se agrega `warnings`.

### 2) Analyze (ranking vs perfil)

- **Frontend**: [frontend/app/page.tsx](frontend/app/page.tsx) (`handleAnalyze`)
- **Backend**: [backend/app/api/documents/router.py](backend/app/api/documents/router.py)

Request:
- `POST /api/documents/analyze` con `documentIds[]`, `jobRequirements`, `filters`.

Response:
- `results[]` con:
  - `candidateName` (se intenta extraer del texto del CV, no del filename)
  - `attributes` (rol/ubicación/skills/idiomas/experiencia)
  - `overallScore`, `matchBreakdown`, `highlights`, `concerns`, `warnings`

Notas de confiabilidad:
- Si **no se detecta** experiencia, se envía `yearsExperience: null` (no “0”).
- `concerns` y `warnings` explican campos faltantes / no verificables.

### 3) Ver CV original

- `GET /api/documents/{document_id}/file` devuelve el archivo original con `Content-Disposition: inline` para poder mostrarse en iframe/modal.

## Presente pero NO conectado / NO implementado

- **NL Search**:
  - Backend: [backend/app/api/search/router.py](backend/app/api/search/router.py) responde `501` (pendiente integrar pipeline).
  - Frontend: [frontend/components/SearchBar.tsx](frontend/components/SearchBar.tsx) existe, pero no se usa en la página principal.

- **Ranking avanzado / embeddings**:
  - `packages/ranking/` está presente, pero el scoring principal actual vive en el endpoint de analyze (lógica simple).

## Puntos de extensión recomendados

- Centralizar un “motor de scoring” real en `packages/ranking/` y hacerlo la única fuente del score.
- Persistencia (DB) para documentos, resultados y estado de análisis (hoy se usa almacenamiento temporal por `document_id`).
