DROP TABLE IF EXISTS cliente;

CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,    
    celular TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);

DROP TABLE IF EXISTS farmacia;

CREATE TABLE farmacia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,    
    cnpj TEXT NOT NULL,
    email TEXT NOT NULL,
    senha TEXT NOT NULL
);