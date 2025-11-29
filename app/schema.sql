DROP TABLE IF EXISTS candidatos;

CREATE TABLE candidatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cargo TEXT NOT NULL,
    habilidades TEXT NOT NULL,        
    experiencia_anios INTEGER NOT NULL,
    idiomas TEXT,                      
    nivel_idioma TEXT,                 
    ubicacion TEXT,
    modalidad TEXT,                    
    disponibilidad TEXT,               
    descripcion TEXT                   
);
