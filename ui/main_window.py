from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.chat_page import ChatPage
from ui.reminders_page import RemindersPage
from ui.file_search_page import FileSearchPage
from ui.weather_page import WeatherPage
from modules.reminders import ReminderManager
from PyQt6.QtGui import QPixmap
from ui.notes_page import NotesPage
from ui.music_page import MusicPage


DARK_STYLE = """
    QMainWindow, QWidget {
        background-color: #1e1e2e;
        color: #cdd6f4;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }
    QLabel {
        background-color: transparent;
    }
    #sidebar {
        background-color: #11111b;
        border-right: 1px solid #313244;
    }
    #app_title {
        color: #cba6f7;
        font-size: 16px;
        font-weight: bold;
        padding: 4px 0;
        background-color: transparent;
    }
    #app_subtitle {
        color: #6c7086;
        font-size: 10px;
        padding: 0;
        background-color: transparent;
    }
    #avatar_circle {
        background-color: #cba6f7;
        border-radius: 0px;
        color: #1e1e2e;
        font-size: 13px;
        font-weight: bold;
    }
    #user_name {
        color: #cdd6f4;
        font-size: 13px;
        font-weight: bold;
        background-color: transparent;
    }
    #user_role {
        color: #6c7086;
        font-size: 10px;
        background-color: transparent;
    }
    #nav_btn {
        background-color: transparent;
        color: #6c7086;
        border: none;
        border-radius: 10px;
        padding: 10px 14px;
        text-align: left;
        font-size: 13px;
    }
    #nav_btn:hover {
        background-color: #1e1e2e;
        color: #cdd6f4;
    }
    #nav_btn:checked {
        background-color: #313244;
        color: #cba6f7;
        font-weight: bold;
    }
    #toggle_btn {
        background-color: #313244;
        color: #a6adc8;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 11px;
        text-align: left;
    }
    #toggle_btn:hover {
        background-color: #45475a;
        color: #cdd6f4;
    }
    #divider {
        background-color: #313244;
        border: none;
        max-height: 1px;
    }
    #content_area {
        background-color: #1e1e2e;
    }
"""

LIGHT_STYLE = """
    QMainWindow, QWidget {
        background-color: #eff1f5;
        color: #4c4f69;
        font-family: 'Poppins', 'Segoe UI', sans-serif;
    }
    QLabel {
        background-color: transparent;
    }
    #sidebar {
        background-color: #e6e9ef;
        border-right: 1px solid #ccd0da;
    }
    #app_title {
        color: #8839ef;
        font-size: 16px;
        font-weight: bold;
        padding: 4px 0;
        background-color: transparent;
    }
    #app_subtitle {
        color: #9ca0b0;
        font-size: 10px;
        padding: 0;
        background-color: transparent;
    }
    #avatar_circle {
        background-color: #8839ef;
        border-radius: 0px;
        color: #eff1f5;
        font-size: 13px;
        font-weight: bold;
    }
    #user_name {
        color: #4c4f69;
        font-size: 13px;
        font-weight: bold;
        background-color: transparent;
    }
    #user_role {
        color: #9ca0b0;
        font-size: 10px;
        background-color: transparent;
    }
    #nav_btn {
        background-color: transparent;
        color: #6c6f85;
        border: none;
        border-radius: 10px;
        padding: 10px 14px;
        text-align: left;
        font-size: 13px;
    }
    #nav_btn:hover {
        background-color: #ccd0da;
        color: #4c4f69;
    }
    #nav_btn:checked {
        background-color: #ccd0da;
        color: #8839ef;
        font-weight: bold;
    }
    #toggle_btn {
        background-color: #ccd0da;
        color: #6c6f85;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 11px;
        text-align: left;
    }
    #toggle_btn:hover {
        background-color: #bcc0cc;
        color: #4c4f69;
    }
    #divider {
        background-color: #ccd0da;
        border: none;
        max-height: 1px;
    }
    #content_area {
        background-color: #eff1f5;
    }
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True
        self.setWindowTitle("NOX — Asistent AI Personal")
        self.setMinimumSize(960, 620)
        self.resize(1150, 700)
        self.reminder_manager = ReminderManager()
        self.reminder_manager.signals.declansat.connect(self._arata_notificare)
        self._build_ui()
        self._apply_theme()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- SIDEBAR ---
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 20, 16, 20)
        sidebar_layout.setSpacing(4)

        # Logo + titlu
        # Logo + titlu
        logo_layout = QHBoxLayout()  # <- adauga aceasta linie
        logo_layout.setSpacing(10)  # <- si aceasta
        logo_icon = QLabel()
        logo_icon.setFixedSize(36, 36)
        pixmap = QPixmap("logo.png").scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
        logo_icon.setPixmap(pixmap)
        logo_icon.setStyleSheet("background-color: transparent;")

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)

        app_title = QLabel("NOX")
        app_title.setObjectName("app_title")

        app_subtitle = QLabel("Asistent AI Personal")
        app_subtitle.setObjectName("app_subtitle")

        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)

        logo_layout.addWidget(logo_icon)
        logo_layout.addLayout(title_layout)
        logo_layout.addStretch()
        sidebar_layout.addLayout(logo_layout)

        sidebar_layout.addSpacing(20)

        # Divider
        div1 = QFrame()
        div1.setObjectName("divider")
        div1.setFixedHeight(1)
        sidebar_layout.addWidget(div1)

        sidebar_layout.addSpacing(12)

        # Label sectiune
        nav_label = QLabel("NAVIGARE")
        nav_label.setStyleSheet(
            "color: #45475a; font-size: 9px; font-weight: bold; "
            "letter-spacing: 1px; background-color: transparent;"
        )
        sidebar_layout.addWidget(nav_label)
        sidebar_layout.addSpacing(4)

        # Butoane navigare
        self.nav_buttons = []
        nav_items = [
            ("💬", "Chat", 0),
            ("⏰", "Remindere", 1),
            ("📝", "Notițe", 2),
            ("🔍", "Căutare fișiere", 3),
            ("🌦️", "Meteo & Valutar", 4),
            ("🎵", "Muzică", 5),  # <--- Adaugă această linie aici
        ]

        for icon, label, index in nav_items:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setObjectName("nav_btn")
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            btn.clicked.connect(lambda checked, i=index: self._navigate(i))
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Divider
        div2 = QFrame()
        div2.setObjectName("divider")
        div2.setFixedHeight(1)
        sidebar_layout.addWidget(div2)

        sidebar_layout.addSpacing(12)

        # Avatar utilizator
        avatar_layout = QHBoxLayout()
        avatar_layout.setSpacing(10)

        avatar = QLabel("FL")
        avatar.setObjectName("avatar_circle")
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        user_layout = QVBoxLayout()
        user_layout.setSpacing(0)

        user_name = QLabel("Flori")
        user_name.setObjectName("user_name")

        user_role = QLabel("Utilizator activ")
        user_role.setObjectName("user_role")

        user_layout.addWidget(user_name)
        user_layout.addWidget(user_role)

        avatar_layout.addWidget(avatar)
        avatar_layout.addLayout(user_layout)
        avatar_layout.addStretch()
        sidebar_layout.addLayout(avatar_layout)

        sidebar_layout.addSpacing(10)

        # Toggle dark/light
        self.toggle_btn = QPushButton("🌙   Dark mode activ")
        self.toggle_btn.setObjectName("toggle_btn")
        self.toggle_btn.setFixedHeight(38)
        self.toggle_btn.clicked.connect(self._toggle_theme)
        sidebar_layout.addWidget(self.toggle_btn)

        # --- CONTENT ---
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")

        self.chat_page = ChatPage(api_key="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", reminder_manager=self.reminder_manager)
        self.stack.addWidget(self.chat_page)
        self.reminders_page = RemindersPage(self.reminder_manager)
        self.notes_page = NotesPage()
        self.stack.addWidget(self.reminders_page)
        self.stack.addWidget(self.notes_page)
        self.stack.addWidget(FileSearchPage())
        self.stack.addWidget(WeatherPage())
        self.stack.addWidget(MusicPage(self.stack))

        self.chat_page.reminder_adaugat.connect(self.reminders_page._refresh_lista)
        self.chat_page.notita_adaugata.connect(self.notes_page._refresh)
        # <-- așa

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.stack)

        self._navigate(0)

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def _apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet(DARK_STYLE)
            self.toggle_btn.setText("🌙   Dark mode activ")
        else:
            self.setStyleSheet(LIGHT_STYLE)
            self.toggle_btn.setText("☀️   Light mode activ")

    def _arata_notificare(self, titlu: str, mesaj: str):
        from ui.notificare import NotificarePopup
        self._popup = NotificarePopup(titlu, mesaj)
        self._popup.show()

    def closeEvent(self, event):
        self.reminder_manager.opreste()
        event.accept()