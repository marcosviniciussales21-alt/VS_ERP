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
)

from database import Database


class ProdutoDialog(QDialog):
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Cadastrar Produto"
            if produto is None
            else "Editar Produto"
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
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)

        layout.addRow(botoes)

        if produto:
            self.codigo.setText(
                produto[1] if produto[1] else ""
            )

            self.nome.setText(
                produto[2] if produto[2] else ""
            )

            self.categoria.setText(
                produto[3] if produto[3] else ""
            )

            self.preco_compra.setValue(
                float(produto[4] or 0)
            )

            self.preco_venda.setValue(
                float(produto[5] or 0)
            )

            self.estoque.setValue(
                float(produto[6] or 0)
            )

            self.estoque_minimo.setValue(
                float(produto[7] or 0)
            )

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


class LoginWindow(QWidget):
    def __init__(self, database, login_sucesso):
        super().__init__()

        self.database = database
        self.login_sucesso = login_sucesso

        self.setWindowTitle("VS ERP - Login")
        self.resize(450, 500)

        self.criar_interface()

    def criar_interface(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            60,
            60,
            60,
            60
        )

        layout.setSpacing(15)

        titulo = QLabel("VS ERP")

        titulo.setAlignment(
            Qt.AlignCenter
        )

        titulo.setStyleSheet(
            """
            font-size: 36px;
            font-weight: bold;
            color: #2563eb;
            """
        )

        subtitulo = QLabel(
            "Sistema de Gestão Comercial"
        )

        subtitulo.setAlignment(
            Qt.AlignCenter
        )

        subtitulo.setStyleSheet(
            """
            font-size: 16px;
            color: #334155;
            """
        )

        self.campo_usuario = QLineEdit()

        self.campo_usuario.setPlaceholderText(
            "Usuário"
        )

        self.campo_usuario.setMinimumHeight(
            45
        )

        self.campo_senha = QLineEdit()

        self.campo_senha.setPlaceholderText(
            "Senha"
        )

        self.campo_senha.setEchoMode(
            QLineEdit.Password
        )

        self.campo_senha.setMinimumHeight(
            45
        )

        self.campo_senha.returnPressed.connect(
            self.entrar
        )

        botao = QPushButton(
            "ENTRAR"
        )

        botao.setMinimumHeight(
            45
        )

        botao.clicked.connect(
            self.entrar
        )

        botao.setStyleSheet(
            """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 15px;
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

        info.setAlignment(
            Qt.AlignCenter
        )

        info.setStyleSheet(
            "color: #475569;"
        )

        layout.addStretch()
        layout.addWidget(
            titulo
        )

        layout.addWidget(
            subtitulo
        )

        layout.addSpacing(
            30
        )

        layout.addWidget(
            self.campo_usuario
        )

        layout.addWidget(
            self.campo_senha
        )

        layout.addWidget(
            botao
        )

        layout.addSpacing(
            20
        )

        layout.addWidget(
            info
        )

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

        dados = self.database.verificar_login(
            usuario,
            senha
        )

        if dados:
            self.login_sucesso(
                dados
            )

        else:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Usuário ou senha inválidos."
            )


class Dashboard(QWidget):
    def __init__(self, database):
        super().__init__()

        self.database = database

        self.layout_principal = QVBoxLayout(
            self
        )

        self.layout_principal.setContentsMargins(
            30,
            30,
            30,
            30
        )

        titulo = QLabel(
            "Dashboard"
        )

        titulo.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        self.layout_principal.addWidget(
            titulo
        )

        self.cards_layout = QHBoxLayout()

        self.label_produtos = QLabel()
        self.label_clientes = QLabel()

        self.criar_cards()

        self.layout_principal.addLayout(
            self.cards_layout
        )

        mensagem = QLabel(
            "Bem-vindo ao VS ERP!\n\n"
            "Versão 1.1 - Cadastro de Produtos"
        )

        mensagem.setAlignment(
            Qt.AlignCenter
        )

        mensagem.setStyleSheet(
            """
            font-size: 20px;
            color: #475569;
            """
        )

        self.layout_principal.addWidget(
            mensagem
        )

        self.layout_principal.addStretch()

    def criar_card(
        self,
        titulo,
        valor
    ):
        card = QFrame()

        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 8px;
            }
            """
        )

        layout = QVBoxLayout(
            card
        )

        label_titulo = QLabel(
            titulo
        )

        label_titulo.setStyleSheet(
            """
            color: #64748b;
            font-size: 14px;
            """
        )

        label_valor = QLabel(
            valor
        )

        label_valor.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        layout.addWidget(
            label_titulo
        )

        layout.addWidget(
            label_valor
        )

        self.cards_layout.addWidget(
            card
        )

        return label_valor

    def criar_cards(self):
        self.criar_card(
            "Vendas Hoje",
            "R$ 0,00"
        )

        self.criar_card(
            "Lucro Hoje",
            "R$ 0,00"
        )

        self.label_produtos = self.criar_card(
            "Produtos",
            str(
                self.database.contar_produtos()
            )
        )

        self.label_clientes = self.criar_card(
            "Clientes",
            str(
                self.database.contar_clientes()
            )
        )

    def atualizar(self):
        self.label_produtos.setText(
            str(
                self.database.contar_produtos()
            )
        )

        self.label_clientes.setText(
            str(
                self.database.contar_clientes()
            )
        )


class ProdutosPage(QWidget):
    def __init__(self, database, dashboard):
        super().__init__()

        self.database = database
        self.dashboard = dashboard

        self.criar_interface()

        self.carregar_produtos()

    def criar_interface(self):
        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        titulo = QLabel(
            "Produtos"
        )

        titulo.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            color: #0f172a;
            """
        )

        layout.addWidget(
            titulo
        )

        topo = QHBoxLayout()

        self.campo_pesquisa = QLineEdit()

        self.campo_pesquisa.setPlaceholderText(
            "Pesquisar por código, nome ou categoria..."
        )

        self.campo_pesquisa.textChanged.connect(
            self.carregar_produtos
        )

        botao_novo = QPushButton(
            "Novo Produto"
        )

        botao_novo.clicked.connect(
            self.novo_produto
        )

        botao_novo.setStyleSheet(
            """
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
            """
        )

        topo.addWidget(
            self.campo_pesquisa
        )

        topo.addWidget(
            botao_novo
        )

        layout.addLayout(
            topo
        )

        self.tabela = QTableWidget()

        self.tabela.setColumnCount(
            8
        )

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

        layout.addWidget(
            self.tabela
        )

        botoes = QHBoxLayout()

        botao_editar = QPushButton(
            "Editar"
        )

        botao_excluir = QPushButton(
            "Excluir"
        )

        botao_editar.clicked.connect(
            self.editar_produto
        )

        botao_excluir.clicked.connect(
            self.excluir_produto
        )

        botoes.addStretch()

        botoes.addWidget(
            botao_editar
        )

        botoes.addWidget(
            botao_excluir
        )

        layout.addLayout(
            botoes
        )

    def carregar_produtos(self):
        pesquisa = self.campo_pesquisa.text().strip()

        produtos = self.database.listar_produtos(
            pesquisa
        )

        self.tabela.setRowCount(
            len(produtos)
        )

        for linha, produto in enumerate(
            produtos
        ):
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

            for coluna, valor in enumerate(
                valores
            ):
                item = QTableWidgetItem(
                    str(valor)
                )

                self.tabela.setItem(
                    linha,
                    coluna,
                    item
                )

    def novo_produto(self):
        dialog = ProdutoDialog(
            self
        )

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

            QMessageBox.information(
                self,
                "VS ERP",
                "Produto cadastrado com sucesso."
            )

            self.carregar_produtos()

            self.dashboard.atualizar()

        except sqlite3.IntegrityError:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Já existe um produto com esse código."
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

        item = self.tabela.item(
            linha,
            0
        )

        if not item:
            return None

        return int(
            item.text()
        )

    def editar_produto(self):
        produto_id = self.produto_selecionado_id()

        if produto_id is None:
            return

        produto = self.database.buscar_produto_por_id(
            produto_id
        )

        if not produto:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Produto não encontrado."
            )

            return

        dialog = ProdutoDialog(
            self,
            produto
        )

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

            QMessageBox.information(
                self,
                "VS ERP",
                "Produto atualizado com sucesso."
            )

            self.carregar_produtos()

            self.dashboard.atualizar()

        except sqlite3.IntegrityError:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Já existe outro produto com esse código."
            )

    def excluir_produto(self):
        produto_id = self.produto_selecionado_id()

        if produto_id is None:
            return

        resposta = QMessageBox.question(
            self,
            "VS ERP",
            "Deseja realmente excluir o produto selecionado?",
            QMessageBox.Yes
            | QMessageBox.No
        )

        if resposta != QMessageBox.Yes:
            return

        self.database.excluir_produto(
            produto_id
        )

        QMessageBox.information(
            self,
            "VS ERP",
            "Produto excluído com sucesso."
        )

        self.carregar_produtos()

        self.dashboard.atualizar()


class MainWindow(QMainWindow):
    def __init__(
        self,
        database,
        usuario
    ):
        super().__init__()

        self.database = database
        self.usuario = usuario

        self.setWindowTitle(
            "VS ERP - Sistema de Gestão Comercial"
        )

        self.resize(
            1200,
            750
        )

        self.criar_interface()

    def criar_interface(self):
        central = QWidget()

        self.setCentralWidget(
            central
        )

        layout = QHBoxLayout(
            central
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            0
        )

        menu = QFrame()

        menu.setFixedWidth(
            230
        )

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

        menu_layout = QVBoxLayout(
            menu
        )

        logo = QLabel(
            "VS ERP"
        )

        logo.setStyleSheet(
            """
            font-size: 25px;
            font-weight: bold;
            padding: 20px;
            """
        )

        menu_layout.addWidget(
            logo
        )

        self.paginas = QStackedWidget()

        self.dashboard = Dashboard(
            self.database
        )

        self.produtos_page = ProdutosPage(
            self.database,
            self.dashboard
        )

        self.paginas.addWidget(
            self.dashboard
        )

        self.paginas.addWidget(
            self.produtos_page
        )

        opcoes = [
            "Dashboard",
            "Caixa",
            "Produtos",
            "Estoque",
            "Entradas",
            "Saídas",
            "Clientes",
            "Fornecedores",
            "Fluxo de Caixa",
            "Relatórios",
            "Configurações",
        ]

        for opcao in opcoes:
            botao = QPushButton(
                opcao
            )

            if opcao == "Dashboard":
                botao.clicked.connect(
                    lambda:
                    self.abrir_dashboard()
                )

            elif opcao == "Produtos":
                botao.clicked.connect(
                    lambda:
                    self.abrir_produtos()
                )

            else:
                botao.clicked.connect(
                    lambda checked=False, nome=opcao:
                    self.modulo_futuro(
                        nome
                    )
                )

            menu_layout.addWidget(
                botao
            )

        menu_layout.addStretch()

        usuario_label = QLabel(
            f"{self.usuario[2]}\n"
            f"{self.usuario[3]}"
        )

        usuario_label.setStyleSheet(
            """
            padding: 15px;
            color: #94a3b8;
            """
        )

        menu_layout.addWidget(
            usuario_label
        )

        layout.addWidget(
            menu
        )

        layout.addWidget(
            self.paginas
        )

    def abrir_dashboard(self):
        self.dashboard.atualizar()

        self.paginas.setCurrentWidget(
            self.dashboard
        )

    def abrir_produtos(self):
        self.produtos_page.carregar_produtos()

        self.paginas.setCurrentWidget(
            self.produtos_page
        )

    def modulo_futuro(
        self,
        nome
    ):
        QMessageBox.information(
            self,
            "VS ERP",
            f"O módulo '{nome}' será adicionado "
            "nas próximas versões."
        )


class Sistema:
    def __init__(self):
        self.app = QApplication(
            sys.argv
        )

        self.app.setStyleSheet(
            """
            QWidget {
                font-family: Segoe UI;
                background-color: #f1f5f9;
                color: #0f172a;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #2563eb;
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

            QDoubleSpinBox {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px;
            }
            """
        )

        self.database = Database()

        self.login = LoginWindow(
            self.database,
            self.abrir_sistema
        )

        self.login.show()

    def abrir_sistema(
        self,
        usuario
    ):
        self.janela = MainWindow(
            self.database,
            usuario
        )

        self.janela.show()

        self.login.close()

    def executar(self):
        sys.exit(
            self.app.exec()
        )


if __name__ == "__main__":
    sistema = Sistema()
    sistema.executar()