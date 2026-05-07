from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QDateTimeEdit, QScrollArea,
    QFrame, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from datetime import datetime
from modules.reminders import ReminderManager


class ReminderCard(QFrame):
    def __init__(self, reminder: dict, on_sterge):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 10px;
                padding: 4px;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        dt = datetime.fromisoformat(reminder["datetime"])
        data_str = dt.strftime("%d.%m.%Y  %H:%M")

        info_layout = QVBoxLayout()

        titlu_lbl = QLabel(reminder["titlu"])
        titlu_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        titlu_lbl.setStyleSheet("color: #cba6f7; border: none;")

        mesaj_lbl = QLabel(reminder.get("mesaj", ""))
        mesaj_lbl.setFont(QFont("Segoe UI", 11))
        mesaj_lbl.setStyleSheet("color: #a6adc8; border: none;")

        recurent = reminder.get("recurent", False)
        zile = reminder.get("zile_saptamana", "")
        if recurent and zile:
            zile_display = zile.replace("mon", "Lun").replace("tue", "Mar").replace("wed", "Mie").replace("thu", "Joi").replace("fri", "Vin").replace("sat", "Sam").replace("sun", "Dum")
            data_lbl = QLabel(f"🔁  In fiecare: {zile_display}  la  {dt.strftime('%H:%M')}")
        else:
            data_lbl = QLabel(f"⏰  {data_str}")
        data_lbl.setFont(QFont("Segoe UI", 10))
        data_lbl.setStyleSheet("color: #6c7086; border: none;")

        info_layout.addWidget(titlu_lbl)
        info_layout.addWidget(mesaj_lbl)
        info_layout.addWidget(data_lbl)

        sterge_btn = QPushButton("Sterge")
        sterge_btn.setFixedSize(70, 32)
        sterge_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #f38ba8;
                border-radius: 6px;
                color: #f38ba8;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #f38ba8;
                color: #1e1e2e;
            }
        """)
        sterge_btn.clicked.connect(lambda: on_sterge(reminder["id"]))

        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(sterge_btn)


class RemindersPage(QWidget):
    def __init__(self, manager: ReminderManager):
        super().__init__()
        self.manager = manager
        self._build_ui()
        self._refresh_lista()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titlu = QLabel("Remindere")
        titlu.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titlu.setStyleSheet("color: #cba6f7;")
        layout.addWidget(titlu)

        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 12px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(10)

        form_titlu = QLabel("Reminder nou")
        form_titlu.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        form_titlu.setStyleSheet("color: #cdd6f4; border: none;")
        form_layout.addWidget(form_titlu)

        self.input_titlu = QLineEdit()
        self.input_titlu.setPlaceholderText("Titlu reminder...")
        self.input_titlu.setFixedHeight(38)
        self.input_titlu.setStyleSheet("""
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
        form_layout.addWidget(self.input_titlu)

        self.input_mesaj = QLineEdit()
        self.input_mesaj.setPlaceholderText("Mesaj (optional)...")
        self.input_mesaj.setFixedHeight(38)
        self.input_mesaj.setStyleSheet(self.input_titlu.styleSheet())
        form_layout.addWidget(self.input_mesaj)

        self.check_recurent = QCheckBox("Reminder recurent (se repeta saptamanal)")
        self.check_recurent.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 12px;
                border: none;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #313244;
                border-radius: 4px;
                background: #1e1e2e;
            }
            QCheckBox::indicator:checked {
                background: #cba6f7;
                border-color: #cba6f7;
            }
        """)
        self.check_recurent.toggled.connect(self._toggle_zile)
        form_layout.addWidget(self.check_recurent)

        self.zile_widget = QWidget()
        self.zile_widget.setStyleSheet("border: none;")
        zile_layout = QHBoxLayout(self.zile_widget)
        zile_layout.setContentsMargins(0, 0, 0, 0)
        zile_layout.setSpacing(6)

        self.zile_checks = {}
        zile = [("Lun", "mon"), ("Mar", "tue"), ("Mie", "wed"),
                ("Joi", "thu"), ("Vin", "fri"), ("Sam", "sat"), ("Dum", "sun")]

        for nume, cod in zile:
            cb = QCheckBox(nume)
            cb.setStyleSheet("""
                QCheckBox {
                    color: #a6adc8;
                    font-size: 11px;
                    border: none;
                }
                QCheckBox::indicator {
                    width: 14px;
                    height: 14px;
                    border: 1px solid #313244;
                    border-radius: 3px;
                    background: #1e1e2e;
                }
                QCheckBox::indicator:checked {
                    background: #cba6f7;
                    border-color: #cba6f7;
                }
            """)
            self.zile_checks[cod] = cb
            zile_layout.addWidget(cb)

        self.zile_widget.setVisible(False)
        form_layout.addWidget(self.zile_widget)

        dt_layout = QHBoxLayout()
        dt_label = QLabel("Data si ora:")
        dt_label.setStyleSheet("color: #a6adc8; font-size: 12px; border: none;")
        dt_label.setFixedWidth(90)

        self.dt_picker = QDateTimeEdit()
        self.dt_picker.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.dt_picker.setDisplayFormat("dd.MM.yyyy  HH:mm")
        self.dt_picker.setFixedHeight(38)
        self.dt_picker.setCalendarPopup(True)
        self.dt_picker.setStyleSheet("""
            QDateTimeEdit {
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 0 12px;
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-size: 12px;
            }
            QDateTimeEdit:focus { border-color: #cba6f7; }
        """)

        dt_layout.addWidget(dt_label)
        dt_layout.addWidget(self.dt_picker)
        form_layout.addLayout(dt_layout)

        adauga_btn = QPushButton("+ Adauga reminder")
        adauga_btn.setFixedHeight(40)
        adauga_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #b48eed; }
        """)
        adauga_btn.clicked.connect(self._adauga)
        form_layout.addWidget(adauga_btn)

        layout.addWidget(form_frame)

        lista_titlu = QLabel("Remindere active")
        lista_titlu.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lista_titlu.setStyleSheet("color: #cdd6f4;")
        layout.addWidget(lista_titlu)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.lista_widget = QWidget()
        self.lista_layout = QVBoxLayout(self.lista_widget)
        self.lista_layout.setSpacing(8)
        self.lista_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.lista_widget)
        layout.addWidget(scroll)

    def _toggle_zile(self, checked: bool):
        self.zile_widget.setVisible(checked)

    def _get_zile_selectate(self) -> str:
        return ",".join(
            cod for cod, cb in self.zile_checks.items() if cb.isChecked()
        )

    def _adauga(self):
        titlu = self.input_titlu.text().strip()
        if not titlu:
            QMessageBox.warning(self, "Atentie", "Titlul este obligatoriu!")
            return

        mesaj = self.input_mesaj.text().strip()
        qt_dt = self.dt_picker.dateTime()
        dt = datetime(
            qt_dt.date().year(), qt_dt.date().month(), qt_dt.date().day(),
            qt_dt.time().hour(), qt_dt.time().minute()
        )

        recurent = self.check_recurent.isChecked()
        zile = self._get_zile_selectate()

        if recurent and not zile:
            QMessageBox.warning(self, "Atentie", "Selecteaza cel putin o zi!")
            return

        if not recurent and dt <= datetime.now():
            QMessageBox.warning(self, "Atentie", "Selecteaza o data in viitor!")
            return

        self.manager.adauga(titlu, mesaj, dt, recurent, zile)
        self.input_titlu.clear()
        self.input_mesaj.clear()
        self.check_recurent.setChecked(False)
        self._refresh_lista()

    def _sterge(self, rid: str):
        self.manager.sterge(rid)
        self._refresh_lista()

    def _refresh_lista(self):
        while self.lista_layout.count():
            item = self.lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        remindere = self.manager.lista()
        if not remindere:
            gol = QLabel("Nu ai niciun reminder activ.")
            gol.setStyleSheet("color: #6c7086; font-size: 12px;")
            gol.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lista_layout.addWidget(gol)
        else:
            for r in remindere:
                card = ReminderCard(r, self._sterge)
                self.lista_layout.addWidget(card)