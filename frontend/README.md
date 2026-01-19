# Frontend - COTECMAR Reclutador IA

Interfaz moderna y responsiva para gestión de candidatos y análisis de perfiles.

## 📁 Estructura del Proyecto

```
frontend/
├── app/
│   ├── globals.css                # Estilos globales
│   ├── layout.tsx                 # Componente root layout
│   └── page.tsx                   # Página principal
├── components/                    # Componentes React reutilizables
│   ├── CandidatesCard.tsx        # Tarjeta de candidatos
│   ├── DocumentUploader.tsx       # Cargador de documentos (CVs)
│   ├── InsightFilters.tsx        # Filtros de análisis
│   ├── JobDescriptionInput.tsx   # Input de descripción de puesto
│   ├── ProfilePanel.tsx          # Panel de perfil
│   ├── SearchBar.tsx             # Barra de búsqueda
│   └── TalentSummary.tsx         # Resumen de talento
├── lib/
│   ├── api.ts                     # Integración con Backend API
│   └── types.ts                   # Definiciones de tipos TypeScript
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.local
```

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
cd frontend
npm install
```

### 2. Configurar variables de entorno
Crear `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_API_TIMEOUT=30000
```

### 3. Ejecutar servidor de desarrollo
```bash
npm run dev
```

La aplicación estará disponible en: **http://localhost:3000**

### 4. Build para producción
```bash
npm run build
npm run start
```

## 🎨 Tecnologías Principales

- **Framework**: Next.js 14+ con TypeScript
- **Styling**: Tailwind CSS + PostCSS
- **Componentes**: React functional components
- **HTTP Client**: Fetch API / axios (via `lib/api.ts`)
- **Type Safety**: TypeScript strict mode

## 🧩 Directrices de Componentes

Cada componente en `components/` debe:

✅ Ser auto-contenido y reutilizable
✅ Aceptar props tipadas desde `lib/types.ts`
✅ Realizar llamadas API a través de `lib/api.ts`
✅ Incluir documentación JSDoc
✅ Soportar estados de carga y error

## 📝 Flujo de Desarrollo

### Agregar Nueva Funcionalidad

1. **Definir tipos** en `lib/types.ts`
    ```typescript
    export interface CandidateProfile {
      id: string;
      name: string;
      // ...
    }
    ```

2. **Crear endpoint API** en `lib/api.ts`
    ```typescript
    export const getCandidates = async () => {
      return fetch(`${API_URL}/api/v1/candidates`);
    }
    ```

3. **Crear componente** en `components/`
    ```typescript
    export default function MyComponent(props: MyComponentProps) {
      // ...
    }
    ```

4. **Integrar en página** en `app/page.tsx`

## 🔌 Integración con Backend

El frontend se conecta con el Backend API en `http://127.0.0.1:8000`:

- **Upload de CVs**: `POST /api/v1/documents/upload`
- **Búsqueda Natural**: `POST /api/v1/search`
- **Recuperar Análisis**: `GET /api/v1/documents/{document_id}`
- **Health Checks**: `GET /health`

## 📦 Scripts Disponibles

```bash
npm run dev       # Servidor de desarrollo (hot reload)
npm run build     # Compilar para producción
npm run start     # Ejecutar build de producción
npm run lint      # Análisis de código
npm run type-check # Verificar tipos TypeScript
```

## ✨ Características

✅ **Responsive Design**: Funciona en desktop, tablet y móvil
✅ **Type Safety**: TypeScript strict + type hints completos
✅ **Performance**: Next.js optimizations (SSR, ISR, SSG)
✅ **Accesibilidad**: Componentes semánticos y ARIA
✅ **Error Handling**: Validación de usuario consistente
✅ **Documentación**: Comentarios JSDoc en componentes

## 📧 Contacto

Equipo COTECMAR
