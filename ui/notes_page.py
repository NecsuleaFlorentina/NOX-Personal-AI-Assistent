from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QScrollArea,
    QFrame, QDialog, QComboBox, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from modules.notes import (
    adauga_notita, editeaza_notita, sterge_notita,
    lista_notite, CULORI
)


class NotitaDialog(QDialog):
    def __init__(self, parent=None, notita: dict = None):
        super().__init__(parent)
        self.notita = notita
        self.setWindowTitle("Notita noua" if not notita else "Editeaza notita")
        self.setMinimumSize(420, 340)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel { background-color: transparent; color: #cdd6f4; }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Titlu
        layout.addWidget(QLabel("Titlu:"))
        self.input_titlu = QLineEdit()
        self.input_titlu.setPlaceholderText("Titlul notiței...")
        self.input_titlu.setFixedHeight(38)
        self.input_titlu.setStyleSheet("""
            QLineEdit {
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 0 12px;
                background-color: #11111b;
                color: #cdd6f4;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: #cba6f7; }
        """)
        if self.notita:
            self.input_titlu.setText(self.notita["titlu"])
        layout.addWidget(self.input_titlu)

        # Continut
        layout.addWidget(QLabel("Continut:"))
        self.input_continut = QTextEdit()
        self.input_continut.setPlaceholderText("Scrie notita aici...")
        self.input_continut.setStyleSheet("""
            QTextEdit {
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 8px;
                background-color: #11111b;
                color: #cdd6f4;
                font-size: 12px;
            }
            QTextEdit:focus { border-color: #cba6f7; }
        """)
        if self.notita:
            self.input_continut.setText(self.notita["continut"])
        layout.addWidget(self.input_continut)

        # Culoare
        culoare_layout = QHBoxLayout()
        culoare_layout.addWidget(QLabel("Culoare:"))

        self.combo_culoare = QComboBox()
        self.combo_culoare.addItems(list(CULORI.keys()))
        self.combo_culoare.setFixedHeight(36)
        self.combo_culoare.setStyleSheet("""
            QComboBox {
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 0 10px;
                background-color: #11111b;
                color: #cdd6f4;
                font-size: 12px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #1e1e2e;
                color: #cdd6f4;
                selection-background-color: #313244;
                border: 1px solid #313244;
            }
        """)
        if self.notita:
            idx = self.combo_culoare.findText(self.notita.get("culoare", "violet"))
            if idx >= 0:
                self.combo_culoare.setCurrentIndex(idx)

        culoare_layout.addWidget(self.combo_culoare)
        culoare_layout.addStretch()
        layout.addLayout(culoare_layout)

        # Butoane
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        anuleaza_btn = QPushButton("Anuleaza")
        anuleaza_btn.setFixedHeight(38)
        anuleaza_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #313244;
                border-radius: 8px;
                color: #a6adc8;
                font-size: 12px;
                padding: 0 16px;
            }
            QPushButton:hover { border-color: #cba6f7; color: #cba6f7; }
        """)
        anuleaza_btn.clicked.connect(self.reject)

        salveaza_btn = QPushButton("Salveaza")
        salveaza_btn.setFixedHeight(38)
        salveaza_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: #b48eed; }
        """)
        salveaza_btn.clicked.connect(self.accept)

        btn_layout.addWidget(anuleaza_btn)
        btn_layout.addWidget(salveaza_btn)
        layout.addLayout(btn_layout)

    def get_date(self) -> tuple:
        return (
            self.input_titlu.text().strip(),
            self.input_continut.toPlainText().strip(),
            self.combo_culoare.currentText()
        )


class NotitaCard(QFrame):
    def __init__(self, notita: dict, on_editeaza, on_sterge):
        super().__init__()
        self.notita = notita
        culoare_hex = CULORI.get(notita.get("culoare", "violet"), "#cba6f7")
        self.setFixedHeight(180)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #181825;
                border: 1px solid #313244;
                border-top: 3px solid {culoare_hex};
                border-radius: 10px;
            }}
            QLabel {{ background-color: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(6)

        # Titlu
        titlu_lbl = QLabel(notita["titlu"] or "Fara titlu")
        titlu_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        titlu_lbl.setStyleSheet(f"color: {culoare_hex};")
        titlu_lbl.setWordWrap(True)
        layout.addWidget(titlu_lbl)

        # Continut
        continut_lbl = QLabel(notita["continut"])
        continut_lbl.setFont(QFont("Segoe UI", 11))
        continut_lbl.setStyleSheet("color: #a6adc8;")
        continut_lbl.setWordWrap(True)
        continut_lbl.setMaximumHeight(70)
        layout.addWidget(continut_lbl)

        layout.addStretch()

        # Footer
        footer = QHBoxLayout()

        data_lbl = QLabel(f"✏️ {notita.get('modificat_la', '')}")
        data_lbl.setStyleSheet("color: #45475a; font-size: 10px;")

        edit_btn = QPushButton("Editeaza")
        edit_btn.setFixedHeight(26)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #313244;
                border-radius: 5px;
                color: #a6adc8;
                font-size: 10px;
                padding: 0 8px;
            }
            QPushButton:hover { border-color: #cba6f7; color: #cba6f7; }
        """)
        edit_btn.clicked.connect(lambda: on_editeaza(notita))

        sterge_btn = QPushButton("Sterge")
        sterge_btn.setFixedHeight(26)
        sterge_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #313244;
                border-radius: 5px;
                color: #f38ba8;
                font-size: 10px;
                padding: 0 8px;
            }
            QPushButton:hover { background-color: #f38ba8; color: #1e1e2e; }
        """)
        sterge_btn.clicked.connect(lambda: on_sterge(notita["id"]))

        footer.addWidget(data_lbl)
        footer.addStretch()
        footer.addWidget(edit_btn)
        footer.addWidget(sterge_btn)
        layout.addLayout(footer)


class NotesPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()

        titlu = QLabel("Notite")
        titlu.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titlu.setStyleSheet("color: #cba6f7; background-color: transparent;")

        adauga_btn = QPushButton("+ Notita noua")
        adauga_btn.setFixedHeight(38)
        adauga_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover { background-color: #b48eed; }
        """)
        adauga_btn.clicked.connect(self._adauga)

        header.addWidget(titlu)
        header.addStretch()
        header.addWidget(adauga_btn)
        layout.addLayout(header)

        # Search
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Cauta in notite...")
        self.input_search.setFixedHeight(38)
        self.input_search.setStyleSheet("""
            QLineEdit {
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 0 12px;
                background-color: #181825;
                color: #cdd6f4;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: #cba6f7; }
        """)
        self.input_search.textChanged.connect(self._refresh)
        layout.addWidget(self.input_search)

        # Grid scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

    def _refresh(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        termen = self.input_search.text().lower().strip()
        notite = lista_notite()

        if termen:
            notite = [n for n in notite if
                      termen in n["titlu"].lower() or
                      termen in n["continut"].lower()]

        if not notite:
            gol = QLabel("Nu ai nicio notita. Apasa '+ Notita noua' pentru a incepe.")
            gol.setStyleSheet("color: #6c7086; font-size: 12px; background-color: transparent;")
            gol.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_layout.addWidget(gol, 0, 0, 1, 3)
            return

        col = 3
        for i, notita in enumerate(notite):
            card = NotitaCard(notita, self._editeaza, self._sterge)
            self.grid_layout.addWidget(card, i // col, i % col)

    def _adauga(self):
        dialog = NotitaDialog(self)
        if dialog.exec():
            titlu, continut, culoare = dialog.get_date()
            if titlu or continut:
                adauga_notita(titlu, continut, culoare)
                self._refresh()

    def _editeaza(self, notita: dict):
        dialog = NotitaDialog(self, notita)
        if dialog.exec():
            titlu, continut, culoare = dialog.get_date()
            editeaza_notita(notita["id"], titlu, continut, culoare)
            self._refresh()

    def _sterge(self, nid: str):
        sterge_notita(nid)
        self._refresh()