from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QCheckBox,
    QMessageBox,
    QGroupBox,
)

from impressora import listar_impressoras, imprimir_teste
from config_impressora import (
    carregar_configuracao,
    salvar_configuracao,
)


class ConfiguracoesImpressoraPage(QWidget):
    def __init__(self):
        super().__init__()

        self.config = carregar_configuracao()

        self.criar_interface()
        self.carregar_dados()

    def criar_interface(self):
        layout = QVBoxLayout(self)

        titulo = QLabel("Configurações da Impressora")
        titulo.setStyleSheet(
            "font-size: 28px;"
            "font-weight: bold;"
        )

        layout.addWidget(titulo)

        grupo = QGroupBox("Impressora Térmica")

        grupo_layout = QVBoxLayout(grupo)

        linha_impressora = QHBoxLayout()

        linha_impressora.addWidget(
            QLabel("Impressora:")
        )

        self.combo_impressora = QComboBox()

        linha_impressora.addWidget(
            self.combo_impressora
        )

        atualizar = QPushButton(
            "Atualizar Lista"
        )

        atualizar.clicked.connect(
            self.carregar_impressoras
        )

        linha_impressora.addWidget(
            atualizar
        )

        grupo_layout.addLayout(
            linha_impressora
        )

        linha_papel = QHBoxLayout()

        linha_papel.addWidget(
            QLabel("Tamanho do papel:")
        )

        self.combo_papel = QComboBox()

        self.combo_papel.addItems([
            "58mm",
            "80mm",
        ])

        linha_papel.addWidget(
            self.combo_papel
        )

        linha_papel.addStretch()

        grupo_layout.addLayout(
            linha_papel
        )

        self.check_automatica = QCheckBox(
            "Imprimir automaticamente ao finalizar a venda"
        )

        grupo_layout.addWidget(
            self.check_automatica
        )

        botoes = QHBoxLayout()

        salvar = QPushButton(
            "Salvar Configuração"
        )

        teste = QPushButton(
            "Imprimir Teste"
        )

        salvar.clicked.connect(
            self.salvar
        )

        teste.clicked.connect(
            self.testar_impressao
        )

        botoes.addWidget(
            salvar
        )

        botoes.addWidget(
            teste
        )

        botoes.addStretch()

        grupo_layout.addLayout(
            botoes
        )

        layout.addWidget(
            grupo
        )

        layout.addStretch()

    def carregar_dados(self):
        self.carregar_impressoras()

        impressora_salva = self.config.get(
            "impressora",
            ""
        )

        indice = self.combo_impressora.findText(
            impressora_salva
        )

        if indice >= 0:
            self.combo_impressora.setCurrentIndex(
                indice
            )

        papel = self.config.get(
            "papel",
            "80mm"
        )

        indice_papel = self.combo_papel.findText(
            papel
        )

        if indice_papel >= 0:
            self.combo_papel.setCurrentIndex(
                indice_papel
            )

        self.check_automatica.setChecked(
            self.config.get(
                "impressao_automatica",
                False
            )
        )

    def carregar_impressoras(self):
        atual = self.combo_impressora.currentText()

        self.combo_impressora.clear()

        try:
            impressoras = listar_impressoras()

            self.combo_impressora.addItems(
                impressoras
            )

            indice = self.combo_impressora.findText(
                atual
            )

            if indice >= 0:
                self.combo_impressora.setCurrentIndex(
                    indice
                )

        except Exception as erro:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Não foi possível listar as impressoras.\n\n"
                f"{erro}"
            )

    def salvar(self):
        config = {
            "impressora":
                self.combo_impressora.currentText(),

            "papel":
                self.combo_papel.currentText(),

            "impressao_automatica":
                self.check_automatica.isChecked(),
        }

        salvar_configuracao(
            config
        )

        self.config = config

        QMessageBox.information(
            self,
            "VS ERP",
            "Configuração da impressora salva com sucesso."
        )

    def testar_impressao(self):
        nome_impressora = (
            self.combo_impressora.currentText()
        )

        if not nome_impressora:
            QMessageBox.warning(
                self,
                "VS ERP",
                "Selecione uma impressora."
            )

            return

        try:
            imprimir_teste(
                nome_impressora
            )

            QMessageBox.information(
                self,
                "VS ERP",
                "Teste de impressão enviado."
            )

        except Exception as erro:
            QMessageBox.critical(
                self,
                "VS ERP",
                "Não foi possível imprimir.\n\n"
                f"{erro}"
            )