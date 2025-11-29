DROP TABLE IF EXISTS candidatos;

CREATE TABLE candidatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL,
    habilidades TEXT NOT NULL,        -- lista separada por comas
    experiencia_anios INTEGER NOT NULL,
    idiomas TEXT,                      -- lista separada por comas
    nivel_idioma TEXT,                 -- ej: B1, B2, C1...
    ubicacion TEXT,
    modalidad TEXT,                    -- remoto, presencial, hibrido
    disponibilidad TEXT,               -- inmediata, 30 días, etc.
    descripcion TEXT                   -- texto libre del perfil
);
