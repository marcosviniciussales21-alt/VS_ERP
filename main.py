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
# DIÁLOGO DE PRODUTO
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
# DIÁLOGO DE CLIENTE
# ============================================================

class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Cadastrar Cliente" if cliente is None else "Editar Cliente"
        )
        self.resize(450, 300)

        layout = QFormLayout(self)

        self.nome = QLineEdit()
        self.cpf_cnpj = QLineEdit()
        self.telefone = QLineEdit()
        self.email = QLineEdit()

        layout.addRow("Nome:", self.nome)
        layout.addRow("CPF/CNPJ:", self.cpf_cnpj)
        layout.addRow("Telefone:", self.telefone)
        layout.addRow("E-mail:", self.email)

        botoes = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)

        layout.addRow(botoes)

        if cliente:
            self.nome.setText(cliente[1] or "")
            self.cpf_cnpj.setText(cliente[2] or "")
            self.telefone.setText(cliente[3] or "")
            self.email.setText(cliente[4] or "")

    def obter_dados(self):
        return {
            "nome": self.nome.text().strip(),
            "cpf_cnpj": self.cpf_cnpj.text().strip(),
            "telefone": self.telefone.text().strip(),
            "email": self.email.text().strip(),
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

        info = QLabel(
            "Primeiro acesso:\n"
            "Usuário: admin\n"
            "Senha: 1234"
        )
        info.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addSpacing(30)
        layout.addWidget(self.campo_usuario)
        layout.addWidget(self.campo_senha)
        layout.addWidget(botao)
        layout.addWidget(info)
        layout.addStretch()

    def entrar(self):
        usuario = self.campo_usuario.text().strip()
        senha = self.campo_senha.text()

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
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        self.cards_layout = QHBoxLayout()

        self.label_vendas = self.criar_card("Vendas Hoje", "R$ 0,00")
        self.label_qtd_vendas = self.criar_card("Qtd. Vendas", "0")
        self.label_produtos = self.criar_card("Produtos", "0")
        self.label_clientes = self.criar_card("Clientes", "0")
        self.label_estoque_baixo = self.criar_card("Estoque Baixo", "0")

        layout.addLayout(self.cards_layout)
        layout.addStretch()

        self.atualizar()

    def criar_card(self, titulo, valor):
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: white; border-radius: 8px; }"
        )

        card_layout = QVBoxLayout(card)

        label_titulo = QLabel(titulo)
        label_valor = QLabel(valor)

        label_valor.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        card_layout.addWidget(label_titulo)
        card_layout.addWidget(label_valor)

        self.cards_layout.addWidget(card)

        return label_valor

    def atualizar(self):
        self.label_produtos.setText(
            str(self.database.contar_produtos())
        )

        self.label_clientes.setText(
            str(self.database.contar_clientes())
        )

        self.label_vendas.setText(
            f"R$ {self.database.total_vendas_hoje():.2f}"
        )

        self.label_qtd_vendas.setText(
            str(self.database.quantidade_vendas_hoje())
        )

        estoque_baixo = self.database.listar_produtos_estoque_baixo()

        self.label_estoque_baixo.setText(
            str(len(estoque_baixo))
        )


# ============================================================
# PRODUTOS
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

        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText("Pesquisar produto...")
        self.pesquisa.textChanged.connect(self.carregar)

        novo = QPushButton("Novo Produto")
        novo.clicked.connect(self.novo_produto)

        topo.addWidget(self.pesquisa)
        topo.addWidget(novo)

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

        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)

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

        self.carregar()

    def carregar(self):
        produtos = self.database.listar_produtos(
            self.pesquisa.text().strip()
        )

        self.tabela.setRowCount(len(produtos))

        for linha, produto in enumerate(produtos):
            valores = [
                produto[0],
                produto[1] or "",
                produto[2],
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

    def id_selecionado(self):
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

            self.carregar()
            self.atualizar_callback()

        except sqlite3.IntegrityError:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Código de produto já cadastrado."
            )

    def editar_produto(self):
        produto_id = self.id_selecionado()

        if produto_id is None:
            return

        produto = self.database.buscar_produto_por_id(produto_id)

        dialog = ProdutoDialog(self, produto)

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

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

        self.carregar()
        self.atualizar_callback()

    def excluir_produto(self):
        produto_id = self.id_selecionado()

        if produto_id is None:
            return

        self.database.excluir_produto(produto_id)

        self.carregar()
        self.atualizar_callback()


# ============================================================
# CLIENTES
# ============================================================

class ClientesPage(QWidget):
    def __init__(self, database, atualizar_callback):
        super().__init__()

        self.database = database
        self.atualizar_callback = atualizar_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Clientes")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        topo = QHBoxLayout()

        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText(
            "Pesquisar cliente..."
        )
        self.pesquisa.textChanged.connect(self.carregar)

        novo = QPushButton("Novo Cliente")
        novo.clicked.connect(self.novo_cliente)

        topo.addWidget(self.pesquisa)
        topo.addWidget(novo)

        layout.addLayout(topo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)

        self.tabela.setHorizontalHeaderLabels(
            [
                "ID",
                "Nome",
                "CPF/CNPJ",
                "Telefone",
                "E-mail",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.tabela)

        botoes = QHBoxLayout()

        editar = QPushButton("Editar")
        excluir = QPushButton("Excluir")

        editar.clicked.connect(self.editar_cliente)
        excluir.clicked.connect(self.excluir_cliente)

        botoes.addStretch()
        botoes.addWidget(editar)
        botoes.addWidget(excluir)

        layout.addLayout(botoes)

        self.carregar()

    def carregar(self):
        clientes = self.database.listar_clientes(
            self.pesquisa.text().strip()
        )

        self.tabela.setRowCount(len(clientes))

        for linha, cliente in enumerate(clientes):
            for coluna, valor in enumerate(cliente):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(valor or ""))
                )

    def id_selecionado(self):
        linha = self.tabela.currentRow()

        if linha < 0:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Selecione um cliente."
            )
            return None

        return int(self.tabela.item(linha, 0).text())

    def novo_cliente(self):
        dialog = ClienteDialog(self)

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        if not dados["nome"]:
            QMessageBox.warning(
                self,
                "VS ERP",
                "O nome do cliente é obrigatório."
            )
            return

        self.database.cadastrar_cliente(
            dados["nome"],
            dados["cpf_cnpj"],
            dados["telefone"],
            dados["email"],
        )

        self.carregar()
        self.atualizar_callback()

    def editar_cliente(self):
        cliente_id = self.id_selecionado()

        if cliente_id is None:
            return

        cliente = self.database.buscar_cliente_por_id(
            cliente_id
        )

        dialog = ClienteDialog(self, cliente)

        if dialog.exec() != QDialog.Accepted:
            return

        dados = dialog.obter_dados()

        self.database.atualizar_cliente(
            cliente_id,
            dados["nome"],
            dados["cpf_cnpj"],
            dados["telefone"],
            dados["email"],
        )

        self.carregar()
        self.atualizar_callback()

    def excluir_cliente(self):
        cliente_id = self.id_selecionado()

        if cliente_id is None:
            return

        self.database.excluir_cliente(cliente_id)

        self.carregar()
        self.atualizar_callback()


# ============================================================
# ESTOQUE
# ============================================================

class EstoquePage(QWidget):
    def __init__(self, database):
        super().__init__()

        self.database = database

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Estoque")
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
                "Estoque",
                "Mínimo",
                "Situação",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
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
# CAIXA
# ============================================================

class CaixaPage(QWidget):
    def __init__(self, database, atualizar_callback):
        super().__init__()

        self.database = database
        self.atualizar_callback = atualizar_callback
        self.itens = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Caixa / PDV")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        topo = QHBoxLayout()

        self.produto = QComboBox()

        self.quantidade = QDoubleSpinBox()
        self.quantidade.setMinimum(0.01)
        self.quantidade.setMaximum(999999)
        self.quantidade.setValue(1)

        adicionar = QPushButton("Adicionar")
        adicionar.clicked.connect(self.adicionar)

        topo.addWidget(self.produto)
        topo.addWidget(self.quantidade)
        topo.addWidget(adicionar)

        layout.addLayout(topo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)

        self.tabela.setHorizontalHeaderLabels(
            [
                "Produto",
                "Quantidade",
                "Preço",
                "Subtotal",
            ]
        )

        self.tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.tabela)

        self.total = QLabel("TOTAL: R$ 0,00")
        self.total.setStyleSheet(
            "font-size: 26px; font-weight: bold;"
        )

        layout.addWidget(self.total)

        self.pagamento = QComboBox()
        self.pagamento.addItems(
            [
                "Dinheiro",
                "PIX",
                "Cartão de Débito",
                "Cartão de Crédito",
            ]
        )

        finalizar = QPushButton("FINALIZAR VENDA")
        finalizar.clicked.connect(self.finalizar)

        layout.addWidget(self.pagamento)
        layout.addWidget(finalizar)

        self.carregar_produtos()

    def carregar_produtos(self):
        self.produto.clear()

        for produto in self.database.listar_produtos():
            self.produto.addItem(
                f"{produto[2]} - Estoque: {produto[6]}",
                produto[0]
            )

    def adicionar(self):
        produto_id = self.produto.currentData()

        if produto_id is None:
            return

        produto = self.database.buscar_produto_por_id(produto_id)

        quantidade = self.quantidade.value()

        self.itens.append(
            {
                "produto_id": produto_id,
                "nome": produto[2],
                "quantidade": quantidade,
                "preco": float(produto[5] or 0),
            }
        )

        self.atualizar_carrinho()

    def atualizar_carrinho(self):
        self.tabela.setRowCount(len(self.itens))

        total = 0

        for linha, item in enumerate(self.itens):
            subtotal = item["quantidade"] * item["preco"]

            total += subtotal

            valores = [
                item["nome"],
                item["quantidade"],
                f"R$ {item['preco']:.2f}",
                f"R$ {subtotal:.2f}",
            ]

            for coluna, valor in enumerate(valores):
                self.tabela.setItem(
                    linha,
                    coluna,
                    QTableWidgetItem(str(valor))
                )

        self.total.setText(f"TOTAL: R$ {total:.2f}")

    def finalizar(self):
        if not self.itens:
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
            for item in self.itens
        ]

        try:
            venda_id, total = self.database.finalizar_venda(
                itens,
                self.pagamento.currentText()
            )

            QMessageBox.information(
                self,
                "VS ERP",
                f"Venda #{venda_id} finalizada.\n"
                f"Total: R$ {total:.2f}"
            )

            self.itens.clear()
            self.atualizar_carrinho()
            self.carregar_produtos()
            self.atualizar_callback()

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "VS ERP",
                str(erro)
            )


# ============================================================
# VENDAS
# ============================================================

class VendasPage(QWidget):
    def __init__(self, database):
        super().__init__()

        self.database = database

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Vendas")
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

        layout.addWidget(self.tabela)

        self.carregar()

    def carregar(self):
        vendas = self.database.listar_vendas()

        self.tabela.setRowCount(len(vendas))

        for linha, venda in enumerate(vendas):
            valores = [
                venda[0],
                venda[1],
                f"R$ {venda[2]:.2f}",
                venda[3] or "",
                venda[4] or "",
            ]

            for coluna, valor in enumerate(valores):
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

        self.setWindowTitle("VS ERP - Sistema de Gestão Comercial")
        self.resize(1300, 800)

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

        self.dashboard = Dashboard(database)
        self.caixa = CaixaPage(database, self.atualizar_telas)
        self.produtos = ProdutosPage(database, self.atualizar_telas)
        self.estoque = EstoquePage(database)
        self.clientes = ClientesPage(database, self.atualizar_telas)
        self.vendas = VendasPage(database)

        for pagina in [
            self.dashboard,
            self.caixa,
            self.produtos,
            self.estoque,
            self.clientes,
            self.vendas,
        ]:
            self.paginas.addWidget(pagina)

        botoes = [
            ("Dashboard", self.abrir_dashboard),
            ("Caixa / PDV", self.abrir_caixa),
            ("Produtos", self.abrir_produtos),
            ("Estoque", self.abrir_estoque),
            ("Entradas", self.registrar_entrada),
            ("Saídas", self.registrar_saida),
            ("Clientes", self.abrir_clientes),
            ("Vendas", self.abrir_vendas),
        ]

        for texto, funcao in botoes:
            botao = QPushButton(texto)
            botao.clicked.connect(funcao)
            menu_layout.addWidget(botao)

        outros = [
            "Fornecedores",
            "Fluxo de Caixa",
            "Relatórios",
            "Configurações",
        ]

        for nome in outros:
            botao = QPushButton(nome)
            botao.clicked.connect(
                lambda checked=False, n=nome:
                QMessageBox.information(
                    self,
                    "VS ERP",
                    f"O módulo '{n}' será implementado depois."
                )
            )
            menu_layout.addWidget(botao)

        menu_layout.addStretch()

        layout.addWidget(menu)
        layout.addWidget(self.paginas)

    def atualizar_telas(self):
        self.dashboard.atualizar()
        self.produtos.carregar()
        self.estoque.carregar()
        self.clientes.carregar()
        self.vendas.carregar()
        self.caixa.carregar_produtos()

    def abrir_dashboard(self):
        self.atualizar_telas()
        self.paginas.setCurrentWidget(self.dashboard)

    def abrir_caixa(self):
        self.caixa.carregar_produtos()
        self.paginas.setCurrentWidget(self.caixa)

    def abrir_produtos(self):
        self.produtos.carregar()
        self.paginas.setCurrentWidget(self.produtos)

    def abrir_estoque(self):
        self.estoque.carregar()
        self.paginas.setCurrentWidget(self.estoque)

    def abrir_clientes(self):
        self.clientes.carregar()
        self.paginas.setCurrentWidget(self.clientes)

    def abrir_vendas(self):
        self.vendas.carregar()
        self.paginas.setCurrentWidget(self.vendas)

    def registrar_entrada(self):
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

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "VS ERP",
                str(erro)
            )

    def registrar_saida(self):
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

        except ValueError as erro:
            QMessageBox.warning(
                self,
                "VS ERP",
                str(erro)
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
            }

            QHeaderView::section {
                background-color: #e2e8f0;
                padding: 8px;
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