from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from modules.chat import ChatModule
from modules.notes import adauga_notita
from modules.voice import VoiceRecorder
from datetime import datetime
import re
import json


class WorkerThread(QThread):
    raspuns_primit = pyqtSignal(str)
    eroare = pyqtSignal(str)

    def __init__(self, chat_module, mesaj):
        super().__init__()
        self.chat_module = chat_module
        self.mesaj = mesaj

    def run(self):
        try:
            raspuns = self.chat_module.trimite_mesaj(self.mesaj)
            self.raspuns_primit.emit(raspuns)
        except Exception as e:
            self.eroare.emit(str(e))


class CitatWorker(QThread):
    citat_primit = pyqtSignal(str)

    def __init__(self, chat_module):
        super().__init__()
        self.chat_module = chat_module

    def run(self):
        try:
            citat = self.chat_module.genereaza_citat()
            self.citat_primit.emit(citat)
        except Exception:
            self.citat_primit.emit("")


def _parse_actiune(raspuns: str):
    match = re.search(r'<actiune>(.*?)</actiune>', raspuns, re.DOTALL)
    if not match:
        return raspuns, None
    try:
        actiune = json.loads(match.group(1).strip())
        text_curat = raspuns[:match.start()].strip()
        return text_curat, actiune
    except Exception:
        return raspuns, None


class ChatPage(QWidget):
    reminder_adaugat = pyqtSignal()
    notita_adaugata = pyqtSignal()
    # Semnale voice (thread-safe)
    voice_result_signal = pyqtSignal(str)
    voice_error_signal = pyqtSignal(str)
    voice_status_signal = pyqtSignal(str)

    def __init__(self, api_key: str, reminder_manager=None):
        super().__init__()
        self.chat = ChatModule(api_key)
        self.reminder_manager = reminder_manager
        self.worker = None
        self._inject_system_prompt()
        self._voice = VoiceRecorder(
            on_result=lambda t: self.voice_result_signal.emit(t),
            on_error=lambda e: self.voice_error_signal.emit(e),
            on_status=lambda s: self.voice_status_signal.emit(s),
        )
        self.voice_result_signal.connect(self._on_voice_result)
        self.voice_error_signal.connect(self._on_voice_error)
        self.voice_status_signal.connect(self._on_voice_status)

        self._build_ui()
        self._incarca_citat()

    def _inject_system_prompt(self):
        original = self.chat._get_system_prompt

        def system_prompt_extins():
            base = original()
            return base + """

--- COMENZI SPECIALE ---
Daca utilizatorul iti cere sa seteze un reminder, sa adauge o notita sau sa salveze ceva,
raspunde normal in romana SI adauga la SFARSITUL raspunsului un bloc JSON astfel:

Pentru reminder:
<actiune>{"tip": "reminder", "titlu": "Titlul scurt", "mesaj": "Detalii", "datetime": "YYYY-MM-DD HH:MM"}</actiune>

Pentru notita:
<actiune>{"tip": "notita", "titlu": "Titlul notitei", "continut": "Continutul complet"}</actiune>

IMPORTANT:
- Foloseste intotdeauna formatul YYYY-MM-DD HH:MM pentru datetime
- Extrage titlul si ora EXACT din ce spune utilizatorul
- Adauga blocul <actiune> doar cand utilizatorul confirma explicit ca vrea sa salveze/adauge
- Nu afisa blocul JSON in textul normal al raspunsului
"""
        self.chat._get_system_prompt = system_prompt_extins

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        self.citat_label = QLabel("Se incarca citatul zilei...")
        self.citat_label.setObjectName("citat_label")
        self.citat_label.setWordWrap(True)
        self.citat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.citat_label.setFont(QFont("Segoe UI", 10))
        self.citat_label.setStyleSheet("color: #888; font-style: italic; padding: 8px 16px; border-radius: 8px;")
        layout.addWidget(self.citat_label)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Segoe UI", 12))
        self.chat_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #313244;
                border-radius: 10px;
                padding: 12px;
                background-color: #181825;
            }
        """)
        layout.addWidget(self.chat_area)

        hint = QLabel("💡 Comenzi rapide: <i>\"amintește-mi să... la 15:00\"</i>  |  <i>\"salvează notița: titlu...\"</i>")
        hint.setStyleSheet("color: #45475a; font-size: 11px; padding: 0 4px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        reset_btn = QPushButton("🔄 Conversatie noua")
        reset_btn.setFixedHeight(32)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid #313244;
                border-radius: 6px; color: #888; font-size: 12px; padding: 0 12px;
            }
            QPushButton:hover { border-color: #cba6f7; color: #cba6f7; }
        """)
        reset_btn.clicked.connect(self._reseteaza)
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_layout.addWidget(reset_btn)
        layout.addLayout(reset_layout)

        # ── Input + microfon + trimitere ──────────────────────────────
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Scrie un mesaj sau apasă 🎙 pentru voce...")
        self.input_field.setFixedHeight(44)
        self.input_field.setFont(QFont("Segoe UI", 12))
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #313244; border-radius: 10px;
                padding: 0 16px; background-color: #181825; color: #cdd6f4;
            }
            QLineEdit:focus { border-color: #cba6f7; }
        """)
        self.input_field.returnPressed.connect(self._trimite)

        # Buton microfon
        self.btn_mic = QPushButton("🎙")
        self.btn_mic.setFixedSize(44, 44)
        self.btn_mic.setFont(QFont("Segoe UI", 16))
        self.btn_mic.setToolTip("Apasă pentru a începe/opri înregistrarea")
        self.btn_mic.setStyleSheet("""
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.btn_mic.clicked.connect(self._toggle_voice)
        self._mic_active = False

        self.send_btn = QPushButton("Trimite")
        self.send_btn.setFixedHeight(44)
        self.send_btn.setFixedWidth(90)
        self.send_btn.setFont(QFont("Segoe UI", 12))
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7; color: #1e1e2e;
                border: none; border-radius: 10px; font-weight: bold;
            }
            QPushButton:hover { background-color: #b48eed; }
            QPushButton:disabled { background-color: #45475a; color: #888; }
        """)
        self.send_btn.clicked.connect(self._trimite)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_mic)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

    # ── Voice ─────────────────────────────────────────────────────────────

    def _toggle_voice(self):
        if not self._mic_active:
            self._mic_active = True
            self._voice.start()
        else:
            self._mic_active = False
            self._voice.stop()

    def _on_voice_status(self, status: str):
        if status == "recording":
            self.btn_mic.setStyleSheet("""
                QPushButton {
                    background-color: #f38ba8;
                    color: #1e1e2e;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
                QPushButton:hover { background-color: #e06c88; }
            """)
            self.btn_mic.setToolTip("Înregistrare activă — apasă din nou pentru a opri")
            self.input_field.setPlaceholderText("🔴 Se înregistrează... apasă 🎙 pentru a opri")
        elif status == "transcribing":
            self.btn_mic.setStyleSheet("""
                QPushButton {
                    background-color: #fab387;
                    color: #1e1e2e;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
            """)
            self.input_field.setPlaceholderText("⏳ Se transcrie...")
        else:  # idle
            self.btn_mic.setStyleSheet("""
                QPushButton {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                }
                QPushButton:hover { background-color: #45475a; }
            """)
            self.input_field.setPlaceholderText("Scrie un mesaj sau apasă 🎙 pentru voce...")

    def _on_voice_result(self, text: str):
        """Textul transcris — il punem in input si trimitem automat."""
        self.input_field.setText(text)
        self._trimite()

    def _on_voice_error(self, err: str):
        self._adauga_sistem(f"🎙 Eroare voce: {err}")

    # ── Chat ──────────────────────────────────────────────────────────────

    def _incarca_citat(self):
        self.citat_worker = CitatWorker(self.chat)
        self.citat_worker.citat_primit.connect(self._afiseaza_citat)
        self.citat_worker.start()

    def _afiseaza_citat(self, citat: str):
        if citat:
            self.citat_label.setText(f"✨ {citat}")

    def _trimite(self):
        mesaj = self.input_field.text().strip()
        if not mesaj or self.worker is not None:
            return

        self.input_field.clear()
        self.send_btn.setEnabled(False)
        self._adauga_mesaj("Tu", mesaj, este_user=True)
        self._adauga_mesaj("NOX", "Se gândește...", este_user=False)

        self.worker = WorkerThread(self.chat, mesaj)
        self.worker.raspuns_primit.connect(self._primeste_raspuns)
        self.worker.eroare.connect(self._primeste_eroare)
        self.worker.start()

    def _primeste_raspuns(self, raspuns: str):
        self._sterge_ultimul_mesaj()
        text_curat, actiune = _parse_actiune(raspuns)
        self._adauga_mesaj("NOX", text_curat, este_user=False)
        if actiune:
            self._executa_actiune(actiune)
        self.send_btn.setEnabled(True)
        self.worker = None

    def _executa_actiune(self, actiune: dict):
        tip = actiune.get("tip")
        if tip == "reminder":
            if not self.reminder_manager:
                self._adauga_sistem("⚠️ ReminderManager nu este conectat.")
                return
            try:
                titlu = actiune.get("titlu", "Reminder")
                mesaj = actiune.get("mesaj", titlu)
                dt_str = actiune.get("datetime", "")
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                self.reminder_manager.adauga(titlu=titlu, mesaj=mesaj, dt=dt)
                ora_fmt = dt.strftime("%d.%m.%Y la %H:%M")
                self._adauga_sistem(f"⏰ Reminder setat: <b>{titlu}</b> — {ora_fmt}")
                self.reminder_adaugat.emit()
            except Exception as e:
                self._adauga_sistem(f"❌ Eroare reminder: {e}")
        elif tip == "notita":
            try:
                titlu = actiune.get("titlu", "Notiță")
                continut = actiune.get("continut", "")
                adauga_notita(titlu=titlu, continut=continut)
                self._adauga_sistem(f"📝 Notiță salvată: <b>{titlu}</b>")
                self.notita_adaugata.emit()
            except Exception as e:
                self._adauga_sistem(f"❌ Eroare notiță: {e}")

    def _primeste_eroare(self, eroare: str):
        self._sterge_ultimul_mesaj()
        self._adauga_mesaj("NOX", f"Eroare: {eroare}", este_user=False)
        self.send_btn.setEnabled(True)
        self.worker = None

    def _adauga_mesaj(self, expeditor: str, text: str, este_user: bool):
        culoare = "#cba6f7" if este_user else "#89dceb"
        self.chat_area.append(
            f'<p><span style="color:{culoare}; font-weight:bold;">{expeditor}:</span> '
            f'<span style="color:#cdd6f4;">{text}</span></p>'
        )

    def _adauga_sistem(self, text: str):
        self.chat_area.append(
            f'<p><span style="color:#a6e3a1;">● {text}</span></p>'
        )

    def _sterge_ultimul_mesaj(self):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

    def _reseteaza(self):
        self.chat.reseteaza_conversatia()
        self.chat_area.clear()