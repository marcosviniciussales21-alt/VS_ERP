import sys

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
)

from database import Database


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
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(15)

        titulo = QLabel("VS ERP")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(
            "font-size: 36px;"
            "font-weight: bold;"
            "color: #2563eb;"
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

        botao.setStyleSheet("""
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
        """)

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
        layout.addSpacing(20)
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


class Dashboard(QWidget):
    def __init__(self, database):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        titulo = QLabel("Dashboard")
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        cards_layout = QHBoxLayout()

        dados = [
            ("Vendas Hoje", "R$ 0,00"),
            ("Lucro Hoje", "R$ 0,00"),
            ("Produtos", str(database.contar_produtos())),
            ("Clientes", str(database.contar_clientes())),
        ]

        for nome, valor in dados:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 8px;
                }
            """)

            card_layout = QVBoxLayout(card)

            nome_label = QLabel(nome)
            valor_label = QLabel(valor)

            nome_label.setStyleSheet(
                "color: #64748b; font-size: 14px;"
            )

            valor_label.setStyleSheet(
                "font-size: 24px; font-weight: bold;"
            )

            card_layout.addWidget(nome_label)
            card_layout.addWidget(valor_label)

            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        mensagem = QLabel(
            "Bem-vindo ao VS ERP!\n\n"
            "Versão 1.0 instalada com sucesso."
        )

        mensagem.setAlignment(Qt.AlignCenter)
        mensagem.setStyleSheet(
            "font-size: 20px; color: #64748b;"
        )

        layout.addWidget(mensagem)
        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self, database, usuario):
        super().__init__()

        self.database = database
        self.usuario = usuario

        self.setWindowTitle(
            "VS ERP - Sistema de Gestão Comercial"
        )

        self.resize(1200, 750)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        menu = QFrame()
        menu.setFixedWidth(230)

        menu.setStyleSheet("""
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
        """)

        menu_layout = QVBoxLayout(menu)

        logo = QLabel("VS ERP")
        logo.setStyleSheet(
            "font-size: 25px;"
            "font-weight: bold;"
            "padding: 20px;"
        )

        menu_layout.addWidget(logo)

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
            botao = QPushButton(opcao)

            if opcao != "Dashboard":
                botao.clicked.connect(
                    lambda checked=False, nome=opcao:
                    self.modulo_futuro(nome)
                )

            menu_layout.addWidget(botao)

        menu_layout.addStretch()

        usuario_label = QLabel(
            f"{usuario[2]}\n{usuario[3]}"
        )

        menu_layout.addWidget(usuario_label)

        self.paginas = QStackedWidget()
        self.paginas.addWidget(Dashboard(database))

        layout.addWidget(menu)
        layout.addWidget(self.paginas)

    def modulo_futuro(self, nome):
        QMessageBox.information(
            self,
            "VS ERP",
            f"O módulo '{nome}' será adicionado "
            "nas próximas versões."
        )


class Sistema:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.app.setStyleSheet("""
            QWidget {
                font-family: Segoe UI;
                background-color: #f1f5f9;
            }

            QLineEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
        """)

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