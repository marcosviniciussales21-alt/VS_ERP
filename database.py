import sqlite3
from pathlib import Path
import hashlib

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "vs_erp.db"


class Database:
    def __init__(self):
        self.criar_tabelas()
        self.criar_admin_padrao()

    def conectar(self):
        return sqlite3.connect(DB_PATH)

    @staticmethod
    def hash_senha(senha):
        return hashlib.sha256(senha.encode("utf-8")).hexdigest()

    def criar_tabelas(self):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    perfil TEXT NOT NULL DEFAULT 'Administrador',
                    ativo INTEGER NOT NULL DEFAULT 1
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE,
                    nome TEXT NOT NULL,
                    categoria TEXT,
                    preco_compra REAL DEFAULT 0,
                    preco_venda REAL DEFAULT 0,
                    estoque REAL DEFAULT 0,
                    estoque_minimo REAL DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf_cnpj TEXT,
                    telefone TEXT,
                    email TEXT
                )
            """)

            conexao.commit()

    def criar_admin_padrao(self):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT id FROM usuarios WHERE usuario = ?",
                ("admin",)
            )

            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO usuarios
                    (usuario, senha, nome, perfil)
                    VALUES (?, ?, ?, ?)
                """, (
                    "admin",
                    self.hash_senha("1234"),
                    "Administrador",
                    "Administrador"
                ))

                conexao.commit()

    def verificar_login(self, usuario, senha):
        senha_hash = self.hash_senha(senha)

        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT id, usuario, nome, perfil
                FROM usuarios
                WHERE usuario = ?
                AND senha = ?
                AND ativo = 1
            """, (usuario, senha_hash))

            return cursor.fetchone()

    def contar_produtos(self):
        with self.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM produtos")
            return cursor.fetchone()[0]

    def contar_clientes(self):
        with self.conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT COUNT(*) FROM clientes")
            return cursor.fetchone()[0]