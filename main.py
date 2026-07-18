import sys
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QDialogButtonBox,
    QComboBox,
)

from database import Database


# ============================================================
# PRODUTOS
# ============================================================

class ProdutoDialog(QDialog):
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Cadastrar Produto" if produto is None else "Editar Produto"
        )
        self.resize(450, 430)

        layout = QFormLayout(self)

        self.codigo = QLineEdit()
        self.nome = QLineEdit()
        self.categoria = QLineEdit()

        self.preco_compra = QDoubleSpinBox()
        self.preco_compra.setMaximum(999999999)
        self.preco_compra.setDecimals(2)
        self.preco_compra.setPrefix("R$ ")

        self.preco_venda = QDoubleSpinBox()
        self.preco_venda.setMaximum(999999999)
        self.preco_venda.setDecimals(2)
        self.preco_venda.setPrefix("R$ ")

        self.estoque = QDoubleSpinBox()
        self.estoque.setMaximum(999999999)
        self.estoque.setDecimals(2)

        self.estoque_minimo = QDoubleSpinBox()
        self.estoque_minimo.setMaximum(999999999)
        self.estoque_minimo.setDecimals(2)

        layout.addRow("Código:", self.codigo)
        layout.addRow("Nome:", self.nome)
        layout.addRow("Categoria:", self.categoria)
        layout.addRow("Preço de compra:", self.preco_compra)
        layout.addRow("Preço de venda:", self.preco_venda)
        layout.addRow("Estoque:", self.estoque)
        layout.addRow("Estoque mínimo:", self.estoque_minimo)

        botoes = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)

        layout.addRow(botoes)

        if produto:
            self.codigo.setText(produto[1] or "")
            self.nome.setText(produto[2] or "")
            self.categoria.setText(produto[3] or "")
            self.preco_compra.setValue(float(produto[4] or 0))
            self.preco_venda.setValue(float(produto[5] or 0))
            self.estoque.setValue(float(produto[6] or 0))
            self.estoque_minimo.setValue(float(produto[7] or 0))

    def obter_dados(self):
        return {
            "codigo": self.codigo.text().strip(),
            "nome": self.nome.text().strip(),
            "categoria": self.categoria.text().strip(),
            "preco_compra": self.preco_compra.value(),
            "preco_venda": self.preco_venda.value(),
            "estoque": self.estoque.value(),
            "estoque_minimo": self.estoque_minimo.value(),
        }


# ============================================================
# MOVIMENTAÇÃO DE ESTOQUE
# ============================================================

class MovimentacaoDialog(QDialog):
    def __init__(self, database, tipo, parent=None):
        super().__init__(parent)

        self.database = database
        self.tipo = tipo

        self.setWindowTitle(
            "Entrada de Mercadoria"
            if tipo == "ENTRADA"
            else "Saída de Mercadoria"
        )

        self.resize(500, 300)

        layout = QFormLayout(self)

        self.produto = QComboBox()

        for item in self.database.listar_produtos():
            texto = (
                f"{item[1] or 'SEM CÓDIGO'} - "
                f"{item[2]} | Estoque: {item[6]}"
            )

            self.produto.addItem(texto, item[0])

        self.quantidade = QDoubleSpinBox()
        self.quantidade.setMinimum(0.01)
        self.quantidade.setMaximum(999999999)
        self.quantidade.setDecimals(2)

        self.observacao = QLineEdit()
        self.observacao.setPlaceholderText("Observação opcional")

        layout.addRow("Produto:", self.produto)
        layout.addRow("Quantidade:", self.quantidade)
        layout.addRow("Observação:", self.observacao)

        botoes = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )

        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)

        layout.addRow(botoes)

    def obter_dados(self):
        return {
            "produto_id": self.produto.currentData(),
            "quantidade": self.quantidade.value(),
            "observacao": self.observacao.text().strip(),
        }


# ============================================================
# LOGIN
# ============================================================

class LoginWindow(QWidget):
    def __init__(self, database, login_sucesso):
        super().__init__()

        self.database = database
        self.login_sucesso = login_sucesso

        self.setWindowTitle("VS ERP - Login")
        self.resize(450, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(15)

        titulo = QLabel("VS ERP")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #2563eb;"
        )

        subtitulo = QLabel("Sistema de Gestão Comercial")
        subtitulo.setAlignment(Qt.AlignCenter)
        subtitulo.setStyleSheet("font-size: 16px; color: #334155;")

        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Usuário")
        self.campo_usuario.setMinimumHeight(45)

        self.campo_senha = QLineEdit()
        self.campo_senha.setPlaceholderText("Senha")
        self.campo_senha.setEchoMode(QLineEdit.Password)
        self.campo_senha.setMinimumHeight(45)
        self.campo_senha.returnPressed.connect(self.entrar)

        botao = QPushButton("ENTRAR")
        botao.setMinimumHeight(45)
        botao.clicked.connect(self.entrar)
        botao.setStyleSheet(
            """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
            """
        )

        info = QLabel(
            "Primeiro acesso:\n"
            "Usuário: admin\n"
            "Senha: 1234"
        )
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("color: #475569;")

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(30)
        layout.addWidget(self.campo_usuario)
        layout.addWidget(self.campo_senha)
        layout.addWidget(botao)
        layout.addSpacing(20)
        layout.addWidget(info)
        layout.addStretch()

    def entrar(self):
        usuario = self.campo_usuario.text().strip()
        senha = self.campo_senha.text()

        if not usuario or not senha:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Informe o usuário e a senha."
            )
            return

        dados = self.database.verificar_login(usuario, senha)

        if dados:
            self.login_sucesso(dados)
        else:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Usuário ou senha inválidos."
            )


# ============================================================
# DASHBOARD
# ============================================================

class Dashboard(QWidget):
    def __init__(self, database):
        super().__init__()

        self.database = database

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Dashboard")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #0f172a;"
        )

        layout.addWidget(titulo)

        self.cards_layout = QHBoxLayout()

        self.label_vendas = self.criar_card(
            "Vendas Hoje",
            "R$ 0,00"
        )

        self.label_qtd_vendas = self.criar_card(
            "Qtd. Vendas",
            "0"
        )

        self.label_produtos = self.criar_card(
            "Produtos",
            "0"
        )

        self.label_estoque_baixo = self.criar_card(
            "Estoque Baixo",
            "0"
        )

        layout.addLayout(self.cards_layout)

        mensagem = QLabel(
            "VS ERP V1.3\n\n"
            "Caixa / PDV e vendas integradas ao estoque."
        )

        mensagem.setAlignment(Qt.AlignCenter)
        mensagem.setStyleSheet(
            "font-size: 20px; color: #475569;"
        )

        layout.addWidget(mensagem)
        layout.addStretch()

        self.atualizar()

    def criar_card(self, titulo, valor):
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
            """
        )

        card_layout = QVBoxLayout(card)

        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("color: #64748b;")

        valor_label = QLabel(valor)
        valor_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #0f172a;"
        )

        card_layout.addWidget(titulo_label)
        card_layout.addWidget(valor_label)

        self.cards_layout.addWidget(card)

        return valor_label

    def atualizar(self):
        self.label_produtos.setText(
            str(self.database.contar_produtos())
        )

        estoque_baixo = self.database.listar_produtos_estoque_baixo()

        self.label_estoque_baixo.setText(
            str(len(estoque_baixo))
        )

        self.label_vendas.setText(
            f"R$ {self.database.total_vendas_hoje():.2f}"
        )

        self.label_qtd_vendas.setText(
            str(self.database.quantidade_vendas_hoje())
        )


# ============================================================
# PRODUTOS PAGE
# ============================================================

class ProdutosPage(QWidget):
    def __init__(self, database, atualizar_callback):
        super().__init__()

        self.database = database
        self.atualizar_callback = atualizar_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Produtos")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        topo = QHBoxLayout()

        self.campo_pesquisa = QLineEdit()
        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar por código, nome ou categoria..."
        )
        self.campo_pesquisa.textChanged.connect(
            self.carregar_produtos
        )

        botao_novo = QPushButton("Novo Produto")
        botao_novo.clicked.connect(self.novo_produto)

        topo.addWidget(self.campo_pesquisa)
        topo.addWidget(botao_novo)

        layout.addLayout(topo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Código",
                "Nome",
                "Categoria",
                "Preço Compra",
                "Preço Venda",
                "Estoque",
                "Estoque Mínimo",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabela.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout.addWidget(self.tabela)

        botoes = QHBoxLayout()

        editar = QPushButton("Editar")
        excluir = QPushButton("Excluir")

        editar.clicked.connect(self.editar_produto)
        excluir.clicked.connect(self.excluir_produto)

        botoes.addStretch()
        botoes.addWidget(editar)
        botoes.addWidget(excluir)

        layout.addLayout(botoes)

        self.carregar_produtos()

    def carregar_produtos(self):
        produtos = self.database.listar_produtos(
            self.campo_pesquisa.text().strip()
        )

        self.tabela.setRowCount(len(produtos))

        for linha, produto in enumerate(produtos):
            valores = [
                produto[0],
                produto[1] or "",
                produto[2] or "",
                produto[3] or "",
                f"R$ {produto[4]:.2f}",
                f"R$ {produto[5]:.2f}",
                produto[6],
                produto[7],
            ]

            for coluna, valor in enumerate(valores):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(valor))
                )

    def produto_selecionado_id(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Selecione um produto."
            )
            return None

        return int(self.tabela.item(linha, 0).text())

    def novo_produto(self):
        dialog = ProdutoDialog(self)

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        if not dados["nome"]:
            QMessageBox.warning(
                self,
                "VS ERP",
                "O nome do produto é obrigatório."
            )
            return

        try:
            self.database.cadastrar_produto(
                dados["codigo"],
                dados["nome"],
                dados["categoria"],
                dados["preco_compra"],
                dados["preco_venda"],
                dados["estoque"],
                dados["estoque_minimo"],
            )

            self.carregar_produtos()
            self.atualizar_callback()

            QMessageBox.information(
                self,
                "VS ERP",
                "Produto cadastrado com sucesso."
            )

        except sqlite3.IntegrityError:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Já existe um produto com esse código."
            )

    def editar_produto(self):
        produto_id = self.produto_selecionado_id()

        if produto_id is None:
            return

        produto = self.database.buscar_produto_por_id(
            produto_id
        )

        dialog = ProdutoDialog(self, produto)

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.database.atualizar_produto(
                produto_id,
                dados["codigo"],
                dados["nome"],
                dados["categoria"],
                dados["preco_compra"],
                dados["preco_venda"],
                dados["estoque"],
                dados["estoque_minimo"],
            )

            self.carregar_produtos()
            self.atualizar_callback()

            QMessageBox.information(
                self,
                "VS ERP",
                "Produto atualizado."
            )

        except sqlite3.IntegrityError:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Código de produto duplicado."
            )

    def excluir_produto(self):
        produto_id = self.produto_selecionado_id()

        if produto_id is None:
            return

        resposta = QMessageBox.question(
            self,
            "VS ERP",
            "Deseja realmente excluir este produto?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta != QMessageBox.Yes:
            return

        try:
            self.database.excluir_produto(produto_id)

            self.carregar_produtos()
            self.atualizar_callback()

        except sqlite3.IntegrityError:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Este produto possui movimentações ou vendas "
                "e não pode ser excluído."
            )


# ============================================================
# ESTOQUE PAGE
# ============================================================

class EstoquePage(QWidget):
    def __init__(self, database):
        super().__init__()

        self.database = database

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Controle de Estoque")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)

        self.tabela.setHorizontalHeaderLabels(
            [
                "Código",
                "Produto",
                "Categoria",
                "Estoque Atual",
                "Estoque Mínimo",
                "Situação",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout.addWidget(self.tabela)

        self.carregar()

    def carregar(self):
        produtos = self.database.listar_produtos()

        self.tabela.setRowCount(len(produtos))

        for linha, produto in enumerate(produtos):
            estoque = float(produto[6] or 0)
            minimo = float(produto[7] or 0)

            situacao = (
                "ESTOQUE BAIXO"
                if estoque <= minimo
                else "NORMAL"
            )

            valores = [
                produto[1] or "",
                produto[2],
                produto[3] or "",
                estoque,
                minimo,
                situacao,
            ]

            for coluna, valor in enumerate(valores):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(valor))
                )


# ============================================================
# MOVIMENTAÇÕES PAGE
# ============================================================

class MovimentacoesPage(QWidget):
    def __init__(self, database):
        super().__init__()

        self.database = database

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Histórico de Movimentações")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Código",
                "Produto",
                "Tipo",
                "Quantidade",
                "Estoque Anterior",
                "Estoque Atual",
                "Observação",
                "Data/Hora",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout.addWidget(self.tabela)

        self.carregar()

    def carregar(self):
        dados = self.database.listar_movimentacoes()

        self.tabela.setRowCount(len(dados))

        for linha, movimentacao in enumerate(dados):
            for coluna, valor in enumerate(movimentacao):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(valor or ""))
                )


# ============================================================
# CAIXA / PDV
# ============================================================

class CaixaPage(QWidget):
    def __init__(self, database, atualizar_callback):
        super().__init__()

        self.database = database
        self.atualizar_callback = atualizar_callback

        self.itens_carrinho = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Caixa / PDV")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        topo = QHBoxLayout()

        self.produto_combo = QComboBox()

        self.quantidade = QDoubleSpinBox()
        self.quantidade.setMinimum(0.01)
        self.quantidade.setMaximum(999999)
        self.quantidade.setDecimals(2)
        self.quantidade.setValue(1)

        adicionar = QPushButton("Adicionar Produto")
        adicionar.clicked.connect(
            self.adicionar_produto
        )

        topo.addWidget(QLabel("Produto:"))
        topo.addWidget(self.produto_combo, 1)
        topo.addWidget(QLabel("Quantidade:"))
        topo.addWidget(self.quantidade)
        topo.addWidget(adicionar)

        layout.addLayout(topo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Produto",
                "Quantidade",
                "Preço Unit.",
                "Subtotal",
                "Estoque",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabela.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout.addWidget(self.tabela)

        botoes = QHBoxLayout()

        remover = QPushButton("Remover Item")
        remover.clicked.connect(
            self.remover_item
        )

        limpar = QPushButton("Limpar Venda")
        limpar.clicked.connect(
            self.limpar_venda
        )

        botoes.addWidget(remover)
        botoes.addWidget(limpar)
        botoes.addStretch()

        self.total_label = QLabel("TOTAL: R$ 0,00")
        self.total_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #16a34a;"
        )

        botoes.addWidget(self.total_label)

        layout.addLayout(botoes)

        rodape = QHBoxLayout()

        self.forma_pagamento = QComboBox()
        self.forma_pagamento.addItems(
            [
                "Dinheiro",
                "PIX",
                "Cartão de Débito",
                "Cartão de Crédito",
            ]
        )

        self.observacao = QLineEdit()
        self.observacao.setPlaceholderText(
            "Observação da venda"
        )

        finalizar = QPushButton("FINALIZAR VENDA")
        finalizar.setMinimumHeight(45)
        finalizar.clicked.connect(
            self.finalizar_venda
        )
        finalizar.setStyleSheet(
            """
            QPushButton {
                background-color: #16a34a;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #15803d;
            }
            """
        )

        rodape.addWidget(QLabel("Pagamento:"))
        rodape.addWidget(self.forma_pagamento)
        rodape.addWidget(self.observacao, 1)
        rodape.addWidget(finalizar)

        layout.addLayout(rodape)

        self.carregar_produtos()

    def carregar_produtos(self):
        produto_atual = self.produto_combo.currentData()

        self.produto_combo.clear()

        produtos = self.database.listar_produtos()

        for produto in produtos:
            texto = (
                f"{produto[1] or 'SEM CÓDIGO'} - "
                f"{produto[2]} | "
                f"R$ {produto[5]:.2f} | "
                f"Estoque: {produto[6]}"
            )

            self.produto_combo.addItem(
                texto,
                produto[0]
            )

        if produto_atual is not None:
            indice = self.produto_combo.findData(
                produto_atual
            )

            if indice >= 0:
                self.produto_combo.setCurrentIndex(
                    indice
                )

    def adicionar_produto(self):
        produto_id = self.produto_combo.currentData()

        if produto_id is None:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Nenhum produto disponível."
            )
            return

        produto = self.database.buscar_produto_por_id(
            produto_id
        )

        quantidade = self.quantidade.value()
        estoque = float(produto[6] or 0)

        quantidade_ja_carrinho = 0

        for item in self.itens_carrinho:
            if item["produto_id"] == produto_id:
                quantidade_ja_carrinho += item["quantidade"]

        if quantidade + quantidade_ja_carrinho > estoque:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Quantidade maior que o estoque disponível."
            )
            return

        for item in self.itens_carrinho:
            if item["produto_id"] == produto_id:
                item["quantidade"] += quantidade
                self.atualizar_carrinho()
                return

        self.itens_carrinho.append(
            {
                "produto_id": produto_id,
                "nome": produto[2],
                "quantidade": quantidade,
                "preco": float(produto[5] or 0),
                "estoque": estoque,
            }
        )

        self.atualizar_carrinho()

    def atualizar_carrinho(self):
        self.tabela.setRowCount(
            len(self.itens_carrinho)
        )

        total = 0

        for linha, item in enumerate(
            self.itens_carrinho
        ):
            subtotal = (
                item["quantidade"]
                * item["preco"]
            )

            total += subtotal

            valores = [
                item["produto_id"],
                item["nome"],
                item["quantidade"],
                f"R$ {item['preco']:.2f}",
                f"R$ {subtotal:.2f}",
                item["estoque"],
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(valor))
                )

        self.total_label.setText(
            f"TOTAL: R$ {total:.2f}"
        )

    def remover_item(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Selecione um item."
            )
            return

        self.itens_carrinho.pop(linha)

        self.atualizar_carrinho()

    def limpar_venda(self):
        self.itens_carrinho.clear()
        self.observacao.clear()
        self.atualizar_carrinho()

    def finalizar_venda(self):
        if not self.itens_carrinho:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Adicione produtos à venda."
            )
            return

        itens = [
            {
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
            }
            for item in self.itens_carrinho
        ]

        try:
            venda_id, total = self.database.finalizar_venda(
                itens,
                self.forma_pagamento.currentText(),
                self.observacao.text().strip()
            )

            QMessageBox.information(
                self,
                "VS ERP",
                f"Venda #{venda_id} finalizada com sucesso.\n\n"
                f"Total: R$ {total:.2f}"
            )

            self.limpar_venda()
            self.carregar_produtos()
            self.atualizar_callback()

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "VS ERP",
                str(erro)
            )


# ============================================================
# HISTÓRICO DE VENDAS
# ============================================================

class VendasPage(QWidget):
    def __init__(self, database):
        super().__init__()

        self.database = database

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Histórico de Vendas")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)

        self.tabela.setHorizontalHeaderLabels(
            [
                "Venda",
                "Data/Hora",
                "Total",
                "Pagamento",
                "Observação",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.tabela.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        layout.addWidget(self.tabela)

        atualizar = QPushButton("Atualizar")
        atualizar.clicked.connect(
            self.carregar
        )

        layout.addWidget(atualizar)

        self.carregar()

    def carregar(self):
        vendas = self.database.listar_vendas()

        self.tabela.setRowCount(
            len(vendas)
        )

        for linha, venda in enumerate(vendas):
            valores = [
                venda[0],
                venda[1],
                f"R$ {venda[2]:.2f}",
                venda[3] or "",
                venda[4] or "",
            ]

            for coluna, valor in enumerate(
                valores
            ):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(valor))
                )


# ============================================================
# JANELA PRINCIPAL
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self, database, usuario):
        super().__init__()

        self.database = database
        self.usuario = usuario

        self.setWindowTitle(
            "VS ERP - Sistema de Gestão Comercial"
        )

        self.resize(1300, 800)

        self.criar_interface()

    def criar_interface(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        menu = QFrame()
        menu.setFixedWidth(230)

        menu.setStyleSheet(
            """
            QFrame {
                background-color: #0f172a;
            }

            QLabel {
                color: white;
            }

            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 12px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #1e293b;
            }
            """
        )

        menu_layout = QVBoxLayout(menu)

        logo = QLabel("VS ERP")
        logo.setStyleSheet(
            "font-size: 25px; font-weight: bold; padding: 20px;"
        )

        menu_layout.addWidget(logo)

        self.paginas = QStackedWidget()

        self.dashboard = Dashboard(
            self.database
        )

        self.produtos_page = ProdutosPage(
            self.database,
            self.atualizar_telas
        )

        self.estoque_page = EstoquePage(
            self.database
        )

        self.movimentacoes_page = MovimentacoesPage(
            self.database
        )

        self.caixa_page = CaixaPage(
            self.database,
            self.atualizar_telas
        )

        self.vendas_page = VendasPage(
            self.database
        )

        paginas = [
            self.dashboard,
            self.caixa_page,
            self.produtos_page,
            self.estoque_page,
            self.movimentacoes_page,
            self.vendas_page,
        ]

        for pagina in paginas:
            self.paginas.addWidget(pagina)

        botoes = [
            ("Dashboard", self.abrir_dashboard),
            ("Caixa / PDV", self.abrir_caixa),
            ("Produtos", self.abrir_produtos),
            ("Estoque", self.abrir_estoque),
            ("Entradas", self.registrar_entrada),
            ("Saídas", self.registrar_saida),
            ("Movimentações", self.abrir_movimentacoes),
            ("Vendas", self.abrir_vendas),
        ]

        for texto, funcao in botoes:
            botao = QPushButton(texto)
            botao.clicked.connect(funcao)
            menu_layout.addWidget(botao)

        outros = [
            "Clientes",
            "Fornecedores",
            "Fluxo de Caixa",
            "Relatórios",
            "Configurações",
        ]

        for nome in outros:
            botao = QPushButton(nome)

            botao.clicked.connect(
                lambda checked=False, n=nome:
                self.modulo_futuro(n)
            )

            menu_layout.addWidget(botao)

        menu_layout.addStretch()

        usuario_label = QLabel(
            f"{self.usuario[2]}\n"
            f"{self.usuario[3]}"
        )

        usuario_label.setStyleSheet(
            "padding: 15px; color: #94a3b8;"
        )

        menu_layout.addWidget(usuario_label)

        layout.addWidget(menu)
        layout.addWidget(self.paginas)

    def atualizar_telas(self):
        self.dashboard.atualizar()
        self.produtos_page.carregar_produtos()
        self.estoque_page.carregar()
        self.movimentacoes_page.carregar()
        self.caixa_page.carregar_produtos()
        self.vendas_page.carregar()

    def abrir_dashboard(self):
        self.atualizar_telas()
        self.paginas.setCurrentWidget(
            self.dashboard
        )

    def abrir_caixa(self):
        self.caixa_page.carregar_produtos()
        self.paginas.setCurrentWidget(
            self.caixa_page
        )

    def abrir_produtos(self):
        self.produtos_page.carregar_produtos()
        self.paginas.setCurrentWidget(
            self.produtos_page
        )

    def abrir_estoque(self):
        self.estoque_page.carregar()
        self.paginas.setCurrentWidget(
            self.estoque_page
        )

    def abrir_movimentacoes(self):
        self.movimentacoes_page.carregar()
        self.paginas.setCurrentWidget(
            self.movimentacoes_page
        )

    def abrir_vendas(self):
        self.vendas_page.carregar()
        self.paginas.setCurrentWidget(
            self.vendas_page
        )

    def registrar_entrada(self):
        if self.database.contar_produtos() == 0:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Cadastre um produto primeiro."
            )
            return

        dialog = MovimentacaoDialog(
            self.database,
            "ENTRADA",
            self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.database.registrar_entrada(
                dados["produto_id"],
                dados["quantidade"],
                dados["observacao"]
            )

            self.atualizar_telas()

            QMessageBox.information(
                self,
                "VS ERP",
                "Entrada registrada com sucesso."
            )

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "VS ERP",
                str(erro)
            )

    def registrar_saida(self):
        if self.database.contar_produtos() == 0:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Cadastre um produto primeiro."
            )
            return

        dialog = MovimentacaoDialog(
            self.database,
            "SAÍDA",
            self
        )

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        try:
            self.database.registrar_saida(
                dados["produto_id"],
                dados["quantidade"],
                dados["observacao"]
            )

            self.atualizar_telas()

            QMessageBox.information(
                self,
                "VS ERP",
                "Saída registrada com sucesso."
            )

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "VS ERP",
                str(erro)
            )

    def modulo_futuro(self, nome):
        QMessageBox.information(
            self,
            "VS ERP",
            f"O módulo '{nome}' será implementado "
            "nas próximas versões."
        )


# ============================================================
# SISTEMA
# ============================================================

class Sistema:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.app.setStyleSheet(
            """
            QWidget {
                font-family: Segoe UI;
                background-color: #f1f5f9;
                color: #0f172a;
            }

            QLineEdit,
            QComboBox,
            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 7px;
            }

            QPushButton {
                padding: 8px 14px;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #cbd5e1;
            }

            QHeaderView::section {
                background-color: #e2e8f0;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            """
        )

        self.database = Database()

        self.login = LoginWindow(
            self.database,
            self.abrir_sistema
        )

        self.login.show()

    def abrir_sistema(self, usuario):
        self.janela = MainWindow(
            self.database,
            usuario
        )

        self.janela.show()
        self.login.close()

    def executar(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    sistema = Sistema()
    sistema.executar()