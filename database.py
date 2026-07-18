import sqlite3
from pathlib import Path
import hashlib
from datetime import datetime, date

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "vs_erp.db"


class Database:
    def __init__(self):
        self.criar_tabelas()
        self.criar_admin_padrao()

    def conectar(self):
        conexao = sqlite3.connect(DB_PATH)
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    quantidade REAL NOT NULL,
                    estoque_anterior REAL NOT NULL,
                    estoque_atual REAL NOT NULL,
                    observacao TEXT,
                    data_hora TEXT NOT NULL,
                    FOREIGN KEY (produto_id) REFERENCES produtos(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora TEXT NOT NULL,
                    total REAL NOT NULL DEFAULT 0,
                    forma_pagamento TEXT,
                    observacao TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS itens_venda (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venda_id INTEGER NOT NULL,
                    produto_id INTEGER NOT NULL,
                    quantidade REAL NOT NULL,
                    preco_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venda_id) REFERENCES vendas(id),
                    FOREIGN KEY (produto_id) REFERENCES produtos(id)
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

    def cadastrar_produto(
        self,
        codigo,
        nome,
        categoria,
        preco_compra,
        preco_venda,
        estoque,
        estoque_minimo
    ):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                INSERT INTO produtos (
                    codigo,
                    nome,
                    categoria,
                    preco_compra,
                    preco_venda,
                    estoque,
                    estoque_minimo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                codigo,
                nome,
                categoria,
                preco_compra,
                preco_venda,
                estoque,
                estoque_minimo
            ))

            conexao.commit()

    def listar_produtos(self, pesquisa=""):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            if pesquisa:
                termo = f"%{pesquisa}%"

                cursor.execute("""
                    SELECT
                        id,
                        codigo,
                        nome,
                        categoria,
                        preco_compra,
                        preco_venda,
                        estoque,
                        estoque_minimo
                    FROM produtos
                    WHERE codigo LIKE ?
                    OR nome LIKE ?
                    OR categoria LIKE ?
                    ORDER BY nome
                """, (termo, termo, termo))

            else:
                cursor.execute("""
                    SELECT
                        id,
                        codigo,
                        nome,
                        categoria,
                        preco_compra,
                        preco_venda,
                        estoque,
                        estoque_minimo
                    FROM produtos
                    ORDER BY nome
                """)

            return cursor.fetchall()

    def buscar_produto_por_id(self, produto_id):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    id,
                    codigo,
                    nome,
                    categoria,
                    preco_compra,
                    preco_venda,
                    estoque,
                    estoque_minimo
                FROM produtos
                WHERE id = ?
            """, (produto_id,))

            return cursor.fetchone()

    def atualizar_produto(
        self,
        produto_id,
        codigo,
        nome,
        categoria,
        preco_compra,
        preco_venda,
        estoque,
        estoque_minimo
    ):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                UPDATE produtos
                SET
                    codigo = ?,
                    nome = ?,
                    categoria = ?,
                    preco_compra = ?,
                    preco_venda = ?,
                    estoque = ?,
                    estoque_minimo = ?
                WHERE id = ?
            """, (
                codigo,
                nome,
                categoria,
                preco_compra,
                preco_venda,
                estoque,
                estoque_minimo,
                produto_id
            ))

            conexao.commit()

    def excluir_produto(self, produto_id):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute(
                "DELETE FROM produtos WHERE id = ?",
                (produto_id,)
            )

            conexao.commit()

    def registrar_entrada(self, produto_id, quantidade, observacao=""):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT estoque FROM produtos WHERE id = ?",
                (produto_id,)
            )

            resultado = cursor.fetchone()

            if resultado is None:
                raise ValueError("Produto não encontrado.")

            estoque_anterior = float(resultado[0] or 0)
            estoque_atual = estoque_anterior + quantidade

            cursor.execute("""
                UPDATE produtos
                SET estoque = ?
                WHERE id = ?
            """, (
                estoque_atual,
                produto_id
            ))

            cursor.execute("""
                INSERT INTO movimentacoes_estoque (
                    produto_id,
                    tipo,
                    quantidade,
                    estoque_anterior,
                    estoque_atual,
                    observacao,
                    data_hora
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                produto_id,
                "ENTRADA",
                quantidade,
                estoque_anterior,
                estoque_atual,
                observacao,
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ))

            conexao.commit()

    def registrar_saida(self, produto_id, quantidade, observacao=""):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT estoque FROM produtos WHERE id = ?",
                (produto_id,)
            )

            resultado = cursor.fetchone()

            if resultado is None:
                raise ValueError("Produto não encontrado.")

            estoque_anterior = float(resultado[0] or 0)

            if quantidade > estoque_anterior:
                raise ValueError(
                    "Estoque insuficiente para realizar a saída."
                )

            estoque_atual = estoque_anterior - quantidade

            cursor.execute("""
                UPDATE produtos
                SET estoque = ?
                WHERE id = ?
            """, (
                estoque_atual,
                produto_id
            ))

            cursor.execute("""
                INSERT INTO movimentacoes_estoque (
                    produto_id,
                    tipo,
                    quantidade,
                    estoque_anterior,
                    estoque_atual,
                    observacao,
                    data_hora
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                produto_id,
                "SAÍDA",
                quantidade,
                estoque_anterior,
                estoque_atual,
                observacao,
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ))

            conexao.commit()

    def listar_movimentacoes(self):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    m.id,
                    p.codigo,
                    p.nome,
                    m.tipo,
                    m.quantidade,
                    m.estoque_anterior,
                    m.estoque_atual,
                    m.observacao,
                    m.data_hora
                FROM movimentacoes_estoque m
                INNER JOIN produtos p
                    ON p.id = m.produto_id
                ORDER BY m.id DESC
            """)

            return cursor.fetchall()

    def listar_produtos_estoque_baixo(self):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    id,
                    codigo,
                    nome,
                    categoria,
                    estoque,
                    estoque_minimo
                FROM produtos
                WHERE estoque <= estoque_minimo
                ORDER BY estoque ASC, nome ASC
            """)

            return cursor.fetchall()

    def finalizar_venda(
        self,
        itens,
        forma_pagamento="Dinheiro",
        observacao=""
    ):
        if not itens:
            raise ValueError("A venda não possui itens.")

        with self.conectar() as conexao:
            cursor = conexao.cursor()

            total_venda = 0

            # Validação de estoque antes de registrar qualquer coisa
            for item in itens:
                produto_id = item["produto_id"]
                quantidade = float(item["quantidade"])

                if quantidade <= 0:
                    raise ValueError(
                        "A quantidade dos itens deve ser maior que zero."
                    )

                cursor.execute("""
                    SELECT nome, estoque, preco_venda
                    FROM produtos
                    WHERE id = ?
                """, (produto_id,))

                produto = cursor.fetchone()

                if produto is None:
                    raise ValueError("Produto não encontrado.")

                nome = produto[0]
                estoque = float(produto[1] or 0)

                if quantidade > estoque:
                    raise ValueError(
                        f"Estoque insuficiente para o produto: {nome}"
                    )

            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            cursor.execute("""
                INSERT INTO vendas (
                    data_hora,
                    total,
                    forma_pagamento,
                    observacao
                )
                VALUES (?, ?, ?, ?)
            """, (
                data_hora,
                0,
                forma_pagamento,
                observacao
            ))

            venda_id = cursor.lastrowid

            for item in itens:
                produto_id = item["produto_id"]
                quantidade = float(item["quantidade"])

                cursor.execute("""
                    SELECT
                        nome,
                        estoque,
                        preco_venda
                    FROM produtos
                    WHERE id = ?
                """, (produto_id,))

                produto = cursor.fetchone()

                nome = produto[0]
                estoque_anterior = float(produto[1] or 0)
                preco_unitario = float(produto[2] or 0)

                subtotal = quantidade * preco_unitario
                estoque_atual = estoque_anterior - quantidade

                total_venda += subtotal

                cursor.execute("""
                    INSERT INTO itens_venda (
                        venda_id,
                        produto_id,
                        quantidade,
                        preco_unitario,
                        subtotal
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    venda_id,
                    produto_id,
                    quantidade,
                    preco_unitario,
                    subtotal
                ))

                cursor.execute("""
                    UPDATE produtos
                    SET estoque = ?
                    WHERE id = ?
                """, (
                    estoque_atual,
                    produto_id
                ))

                cursor.execute("""
                    INSERT INTO movimentacoes_estoque (
                        produto_id,
                        tipo,
                        quantidade,
                        estoque_anterior,
                        estoque_atual,
                        observacao,
                        data_hora
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    produto_id,
                    "VENDA",
                    quantidade,
                    estoque_anterior,
                    estoque_atual,
                    f"Venda #{venda_id} - {nome}",
                    data_hora
                ))

            cursor.execute("""
                UPDATE vendas
                SET total = ?
                WHERE id = ?
            """, (
                total_venda,
                venda_id
            ))

            conexao.commit()

            return venda_id, total_venda

    def listar_vendas(self):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    id,
                    data_hora,
                    total,
                    forma_pagamento,
                    observacao
                FROM vendas
                ORDER BY id DESC
            """)

            return cursor.fetchall()

    def listar_itens_venda(self, venda_id):
        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT
                    p.codigo,
                    p.nome,
                    i.quantidade,
                    i.preco_unitario,
                    i.subtotal
                FROM itens_venda i
                INNER JOIN produtos p
                    ON p.id = i.produto_id
                WHERE i.venda_id = ?
                ORDER BY i.id
            """, (venda_id,))

            return cursor.fetchall()

    def total_vendas_hoje(self):
        hoje = date.today().strftime("%d/%m/%Y")

        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT COALESCE(SUM(total), 0)
                FROM vendas
                WHERE data_hora LIKE ?
            """, (
                f"{hoje}%",
            ))

            return float(cursor.fetchone()[0] or 0)

    def quantidade_vendas_hoje(self):
        hoje = date.today().strftime("%d/%m/%Y")

        with self.conectar() as conexao:
            cursor = conexao.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM vendas
                WHERE data_hora LIKE ?
            """, (
                f"{hoje}%",
            ))

            return int(cursor.fetchone()[0] or 0)