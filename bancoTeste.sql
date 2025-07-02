DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS login;

CREATE TABLE produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL NOT NULL,
    imagem TEXT
);

CREATE TABLE login (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT,
    senha TEXT NOT NULL
);

-- os inserts já podem ter NULL ou string vazia na imagem
INSERT INTO produtos (nome, descricao, preco, imagem) VALUES
('Bolo de Chocolate', 'Bolo macio com cobertura de chocolate', 25.00, ''),
('Torta de Limão', 'Torta gelada com merengue', 20.00, ''),
('Cupcake de Baunilha', 'Cupcake com cobertura de chantilly', 8.50, '');

INSERT INTO login (nome, email, senha) VALUES
('Justin Bieber Brasileiro', 'justinbieber@gmail.com', '1234'),
('Cachorro Russo Putim', 'cachorro@gmail.com', '5678'),
('Lula da Silva', 'lula@gmail.com', '9876');
