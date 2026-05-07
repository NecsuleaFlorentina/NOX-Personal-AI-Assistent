from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QScreen
from PyQt6.QtWidgets import QApplication


class NotificarePopup(QWidget):
    def __init__(self, titlu: str, mesaj: str):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(320, 100)
        self._pozitioneaza()
        self._build_ui(titlu, mesaj)

        # Inchide automat dupa 6 secunde
        QTimer.singleShot(6000, self.close)

    def _pozitioneaza(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() - self.width() - 24,
            screen.height() - self.height() - 60
        )

    def _build_ui(self, titlu: str, mesaj: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #1e1e2e;
                border: 1px solid #cba6f7;
                border-radius: 12px;
            }
        """)

        inner = QVBoxLayout(container)
        inner.setContentsMargins(16, 12, 16, 12)
        inner.setSpacing(4)

        # Header
        header = QHBoxLayout()

        icon = QLabel("⏰")
        icon.setFont(QFont("Segoe UI", 14))

        titlu_lbl = QLabel(titlu)
        titlu_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        titlu_lbl.setStyleSheet("color: #cba6f7;")

        inchide_btn = QPushButton("✕")
        inchide_btn.setFixedSize(20, 20)
        inchide_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #6c7086;
                font-size: 12px;
            }
            QPushButton:hover { color: #f38ba8; }
        """)
        inchide_btn.clicked.connect(self.close)

        header.addWidget(icon)
        header.addWidget(titlu_lbl)
        header.addStretch()
        header.addWidget(inchide_btn)

        # Mesaj
        mesaj_lbl = QLabel(mesaj if mesaj else "Reminder!")
        mesaj_lbl.setFont(QFont("Segoe UI", 11))
        mesaj_lbl.setStyleSheet("color: #a6adc8;")
        mesaj_lbl.setWordWrap(True)

        inner.addLayout(header)
        inner.addWidget(mesaj_lbl)

        layout.addWidget(container)