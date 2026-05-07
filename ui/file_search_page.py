from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QFileDialog, QFrame, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from modules.file_search import cauta_fisiere, deschide_fisier, deschide_folder


class SearchWorker(QThread):
    rezultate_gata = pyqtSignal(list)

    def __init__(self, termen, folder):
        super().__init__()
        self.termen = termen
        self.folder = folder

    def run(self):
        rezultate = cauta_fisiere(self.termen, self.folder)
        self.rezultate_gata.emit(rezultate)


class FileSearchPage(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_selectat = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titlu = QLabel("Cautare fisiere")
        titlu.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titlu.setStyleSheet("color: #cba6f7;")
        layout.addWidget(titlu)

        # Bara de cautare
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 12px;
            }
        """)
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(16, 16, 16, 16)
        search_layout.setSpacing(10)

        # Input cautare
        input_layout = QHBoxLayout()

        self.input_cautare = QLineEdit()
        self.input_cautare.setPlaceholderText("Numele fisierului (ex: raport, .pdf, .py)...")
        self.input_cautare.setFixedHeight(42)
        self.input_cautare.setFont(QFont("Segoe UI", 12))
        self.input_cautare.setStyleSheet("""
            QLineEdit {
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 0 12px;
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: #cba6f7; }
        """)
        self.input_cautare.returnPressed.connect(self._cauta)

        cauta_btn = QPushButton("Cauta")
        cauta_btn.setFixedHeight(42)
        cauta_btn.setFixedWidth(90)
        cauta_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #b48eed; }
            QPushButton:disabled { background-color: #45475a; color: #888; }
        """)
        cauta_btn.clicked.connect(self._cauta)
        self.cauta_btn = cauta_btn

        input_layout.addWidget(self.input_cautare)
        input_layout.addWidget(cauta_btn)
        search_layout.addLayout(input_layout)

        # Selectie folder
        folder_layout = QHBoxLayout()

        self.folder_label = QLabel("Cauta in: Locatii implicite (Desktop, Documente, Descarcari...)")
        self.folder_label.setStyleSheet("color: #6c7086; font-size: 11px; border: none;")
        self.folder_label.setWordWrap(True)

        folder_btn = QPushButton("Alege folder")
        folder_btn.setFixedHeight(32)
        folder_btn.setFixedWidth(110)
        folder_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #313244;
                border-radius: 6px;
                color: #a6adc8;
                font-size: 11px;
            }
            QPushButton:hover { border-color: #cba6f7; color: #cba6f7; }
        """)
        folder_btn.clicked.connect(self._alege_folder)

        reset_btn = QPushButton("Reset")
        reset_btn.setFixedHeight(32)
        reset_btn.setFixedWidth(60)
        reset_btn.setStyleSheet(folder_btn.styleSheet())
        reset_btn.clicked.connect(self._reset_folder)

        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(folder_btn)
        folder_layout.addWidget(reset_btn)
        search_layout.addLayout(folder_layout)

        layout.addWidget(search_frame)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #6c7086; font-size: 12px;")
        layout.addWidget(self.status_label)

        # Lista rezultate
        self.lista = QListWidget()
        self.lista.setFont(QFont("Segoe UI", 11))
        self.lista.setStyleSheet("""
            QListWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 10px;
                padding: 8px;
                color: #cdd6f4;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                border: none;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
            QListWidget::item:selected {
                background-color: #45475a;
                color: #cba6f7;
            }
        """)
        self.lista.itemDoubleClicked.connect(self._deschide_fisier)
        self.lista.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lista.customContextMenuRequested.connect(self._context_menu)

        layout.addWidget(self.lista)

        hint = QLabel("Dublu click pentru a deschide fisierul  |  Click dreapta pentru optiuni")
        hint.setStyleSheet("color: #45475a; font-size: 11px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

    def _cauta(self):
        termen = self.input_cautare.text().strip()
        if not termen:
            return

        self.lista.clear()
        self.status_label.setText("Se cauta...")
        self.cauta_btn.setEnabled(False)

        self.worker = SearchWorker(termen, self.folder_selectat)
        self.worker.rezultate_gata.connect(self._afiseaza_rezultate)
        self.worker.start()

    def _afiseaza_rezultate(self, rezultate: list):
        self.lista.clear()
        self.cauta_btn.setEnabled(True)

        if not rezultate:
            self.status_label.setText("Niciun fisier gasit.")
            return

        self.status_label.setText(f"{len(rezultate)} fisiere gasite:")
        for cale in rezultate:
            item = QListWidgetItem(cale)
            item.setToolTip(cale)
            self.lista.addItem(item)

    def _deschide_fisier(self, item: QListWidgetItem):
        try:
            deschide_fisier(item.text())
        except Exception as e:
            self.status_label.setText(f"Eroare: {e}")

    def _context_menu(self, pos):
        item = self.lista.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 8px;
                color: #cdd6f4;
                font-size: 12px;
            }
            QMenu::item { padding: 6px 20px; }
            QMenu::item:selected { background-color: #313244; color: #cba6f7; }
        """)

        act_deschide = menu.addAction("Deschide fisier")
        act_folder = menu.addAction("Deschide folderul parinte")
        act_copie = menu.addAction("Copiaza calea")

        actiune = menu.exec(QCursor.pos())

        if actiune == act_deschide:
            deschide_fisier(item.text())
        elif actiune == act_folder:
            deschide_folder(item.text())
        elif actiune == act_copie:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(item.text())
            self.status_label.setText("Calea a fost copiata!")

    def _alege_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Alege folder")
        if folder:
            self.folder_selectat = folder
            self.folder_label.setText(f"Cauta in: {folder}")

    def _reset_folder(self):
        self.folder_selectat = None
        self.folder_label.setText("Cauta in: Locatii implicite (Desktop, Documente, Descarcari...)")