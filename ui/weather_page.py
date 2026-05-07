from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from modules.weather import get_meteo, get_curs_valutar


class MeteoWorker(QThread):
    gata = pyqtSignal(dict)

    def __init__(self, oras):
        super().__init__()
        self.oras = oras

    def run(self):
        self.gata.emit(get_meteo(self.oras))


class ValutarWorker(QThread):
    gata = pyqtSignal(dict)

    def __init__(self, baza, tinta):
        super().__init__()
        self.baza = baza
        self.tinta = tinta

    def run(self):
        self.gata.emit(get_curs_valutar(self.baza, self.tinta))


class WeatherPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self._refresh_meteo()
        self._refresh_valutar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titlu = QLabel("Meteo & Valutar")
        titlu.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titlu.setStyleSheet("color: #cba6f7;")
        layout.addWidget(titlu)

        # --- METEO ---
        meteo_frame = QFrame()
        meteo_frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 12px;
            }
        """)
        meteo_layout = QVBoxLayout(meteo_frame)
        meteo_layout.setContentsMargins(16, 16, 16, 16)
        meteo_layout.setSpacing(10)

        meteo_header = QHBoxLayout()
        meteo_titlu = QLabel("Meteo")
        meteo_titlu.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        meteo_titlu.setStyleSheet("color: #cdd6f4; border: none;")

        self.input_oras = QLineEdit()
        self.input_oras.setPlaceholderText("Oras...")
        self.input_oras.setText("Craiova")
        self.input_oras.setFixedHeight(34)
        self.input_oras.setFixedWidth(150)
        self.input_oras.setStyleSheet("""
            QLineEdit {
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 0 10px;
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: #cba6f7; }
        """)
        self.input_oras.returnPressed.connect(self._refresh_meteo)

        meteo_btn = QPushButton("Actualizeaza")
        meteo_btn.setFixedHeight(34)
        meteo_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 12px;
            }
            QPushButton:hover { background-color: #b48eed; }
        """)
        meteo_btn.clicked.connect(self._refresh_meteo)

        meteo_header.addWidget(meteo_titlu)
        meteo_header.addStretch()
        meteo_header.addWidget(self.input_oras)
        meteo_header.addWidget(meteo_btn)
        meteo_layout.addLayout(meteo_header)

        # Cards meteo
        self.meteo_status = QLabel("Se incarca...")
        self.meteo_status.setStyleSheet("color: #6c7086; font-size: 12px; border: none;")
        meteo_layout.addWidget(self.meteo_status)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        self.card_acum = self._meteo_card("Acum", "--°C", "--")
        self.card_azi = self._meteo_card("Astazi", "--°C / --°C", "Max / Min")
        self.card_maine = self._meteo_card("Maine", "--°C / --°C", "Max / Min")

        cards_layout.addWidget(self.card_acum)
        cards_layout.addWidget(self.card_azi)
        cards_layout.addWidget(self.card_maine)
        meteo_layout.addLayout(cards_layout)

        # Extra info
        self.meteo_extra = QLabel("")
        self.meteo_extra.setStyleSheet("color: #6c7086; font-size: 11px; border: none;")
        meteo_layout.addWidget(self.meteo_extra)

        layout.addWidget(meteo_frame)

        # --- VALUTAR ---
        valutar_frame = QFrame()
        valutar_frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 12px;
            }
        """)
        valutar_layout = QVBoxLayout(valutar_frame)
        valutar_layout.setContentsMargins(16, 16, 16, 16)
        valutar_layout.setSpacing(10)

        valutar_titlu = QLabel("Curs valutar")
        valutar_titlu.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        valutar_titlu.setStyleSheet("color: #cdd6f4; border: none;")
        valutar_layout.addWidget(valutar_titlu)

        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(8)

        self.combo_baza = QComboBox()
        self.combo_baza.addItems(["EUR", "USD", "GBP", "CHF", "JPY"])
        self.combo_baza.setFixedHeight(36)
        self.combo_baza.setStyleSheet("""
            QComboBox {
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 0 10px;
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-size: 12px;
            }
            QComboBox:focus { border-color: #cba6f7; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #1e1e2e;
                color: #cdd6f4;
                selection-background-color: #313244;
                border: 1px solid #313244;
            }
        """)

        sageata = QLabel("→")
        sageata.setStyleSheet("color: #cba6f7; font-size: 16px; border: none;")
        sageata.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.combo_tinta = QComboBox()
        self.combo_tinta.addItems(["RON", "USD", "EUR", "GBP", "CHF"])
        self.combo_tinta.setFixedHeight(36)
        self.combo_tinta.setStyleSheet(self.combo_baza.styleSheet())

        valutar_btn = QPushButton("Converteste")
        valutar_btn.setFixedHeight(36)
        valutar_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 14px;
            }
            QPushButton:hover { background-color: #b48eed; }
        """)
        valutar_btn.clicked.connect(self._refresh_valutar)

        selector_layout.addWidget(self.combo_baza)
        selector_layout.addWidget(sageata)
        selector_layout.addWidget(self.combo_tinta)
        selector_layout.addWidget(valutar_btn)
        selector_layout.addStretch()
        valutar_layout.addLayout(selector_layout)

        self.valutar_result = QLabel("Se incarca...")
        self.valutar_result.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.valutar_result.setStyleSheet("color: #a6e3a1; border: none;")
        valutar_layout.addWidget(self.valutar_result)

        self.valutar_data = QLabel("")
        self.valutar_data.setStyleSheet("color: #6c7086; font-size: 11px; border: none;")
        valutar_layout.addWidget(self.valutar_data)

        layout.addWidget(valutar_frame)
        layout.addStretch()

    def _meteo_card(self, titlu, valoare, sub) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 10px;
            }
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.setSpacing(4)

        t = QLabel(titlu)
        t.setStyleSheet("color: #6c7086; font-size: 11px; border: none;")
        t.setObjectName("card_titlu")

        v = QLabel(valoare)
        v.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        v.setStyleSheet("color: #cdd6f4; border: none;")
        v.setObjectName("card_valoare")

        s = QLabel(sub)
        s.setStyleSheet("color: #6c7086; font-size: 11px; border: none;")
        s.setObjectName("card_sub")

        cl.addWidget(t)
        cl.addWidget(v)
        cl.addWidget(s)
        return card

    def _update_card(self, card: QFrame, titlu: str, valoare: str, sub: str):
        card.findChild(QLabel, "card_titlu").setText(titlu)
        card.findChild(QLabel, "card_valoare").setText(valoare)
        card.findChild(QLabel, "card_sub").setText(sub)

    def _refresh_meteo(self):
        oras = self.input_oras.text().strip() or "Craiova"
        self.meteo_status.setText("Se incarca...")
        self.worker_meteo = MeteoWorker(oras)
        self.worker_meteo.gata.connect(self._afiseaza_meteo)
        self.worker_meteo.start()

    def _afiseaza_meteo(self, data: dict):
        if not data["success"]:
            self.meteo_status.setText(f"Eroare: {data['eroare']}")
            return

        self.meteo_status.setText(f"📍 {data['oras']}")
        self._update_card(
            self.card_acum,
            "Acum",
            f"{data['temp']}°C",
            data["descriere"]
        )
        self._update_card(
            self.card_azi,
            "Astazi",
            f"{data['max_azi']}° / {data['min_azi']}°",
            f"Umiditate: {data['umiditate']}%"
        )
        self._update_card(
            self.card_maine,
            "Maine",
            f"{data['max_maine']}° / {data['min_maine']}°",
            f"Vant: {data['vant']} km/h"
        )
        self.meteo_extra.setText(
            f"Se simte ca: {data['feels_like']}°C  |  "
            f"Vant: {data['vant']} km/h  |  "
            f"Umiditate: {data['umiditate']}%"
        )

    def _refresh_valutar(self):
        baza = self.combo_baza.currentText()
        tinta = self.combo_tinta.currentText()
        self.valutar_result.setText("Se incarca...")
        self.worker_valutar = ValutarWorker(baza, tinta)
        self.worker_valutar.gata.connect(self._afiseaza_valutar)
        self.worker_valutar.start()

    def _afiseaza_valutar(self, data: dict):
        if not data["success"]:
            self.valutar_result.setText(f"Eroare: {data['eroare']}")
            return

        self.valutar_result.setText(
            f"1 {data['baza']} = {data['curs']} {data['tinta']}"
        )
        self.valutar_data.setText(f"Actualizat: {data['data']}")