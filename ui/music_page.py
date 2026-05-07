from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSlider, QScrollArea, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from modules.music import MusicPlayer, download_song, get_local_path


class AddSongThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, player, url):
        super().__init__()
        self.player = player
        self.url = url

    def run(self):
        try:
            title = self.player.add_to_playlist(self.url)
            self.finished.emit(title)
        except Exception as e:
            self.error.emit(str(e))


class MusicPage(QWidget):
    progress_signal = pyqtSignal(float)
    status_signal = pyqtSignal(str)
    title_signal = pyqtSignal(str)
    # Semnale download
    download_progress_signal = pyqtSignal(int, float)   # (index, percent)
    download_done_signal = pyqtSignal(int, str)          # (index, filepath)
    download_error_signal = pyqtSignal(int, str)         # (index, err)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = MusicPlayer()
        self.player.set_progress_callback(lambda v: self.progress_signal.emit(v))
        self.player.set_status_callback(lambda s: self.status_signal.emit(s))
        self.player.set_title_callback(lambda t: self.title_signal.emit(t))

        self.progress_signal.connect(self._update_progress)
        self.status_signal.connect(self._update_status)
        self.title_signal.connect(self._update_title)
        self.download_progress_signal.connect(self._on_download_progress)
        self.download_done_signal.connect(self._on_download_done)
        self.download_error_signal.connect(self._on_download_error)

        self._download_bars = {}  # index -> QProgressBar

        self._build_ui()
        self._refresh_playlist()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(12)

        title = QLabel("🎵 Player Muzică")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #cba6f7;")
        main_layout.addWidget(title)

        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #181825; border-radius: 16px; }")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(20, 20, 20, 20)

        self.lbl_title = QLabel("Nicio melodie selectată")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #cdd6f4;")
        card_layout.addWidget(self.lbl_title)

        self.lbl_status = QLabel("Oprit")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("font-size: 12px; color: #6c7086;")
        card_layout.addWidget(self.lbl_status)

        progress_layout = QHBoxLayout()
        self.lbl_elapsed = QLabel("0:00")
        self.lbl_elapsed.setStyleSheet("color: #6c7086; font-size: 11px;")
        self.lbl_elapsed.setFixedWidth(40)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; background: #313244; border-radius: 2px; }
            QSlider::handle:horizontal { background: #cba6f7; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::sub-page:horizontal { background: #cba6f7; border-radius: 2px; }
        """)
        self.progress_slider.sliderMoved.connect(self._on_seek)

        self.lbl_total = QLabel("0:00")
        self.lbl_total.setStyleSheet("color: #6c7086; font-size: 11px;")
        self.lbl_total.setFixedWidth(40)
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)

        progress_layout.addWidget(self.lbl_elapsed)
        progress_layout.addWidget(self.progress_slider)
        progress_layout.addWidget(self.lbl_total)
        card_layout.addLayout(progress_layout)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ctrl_layout.setSpacing(14)

        btn_style = """
            QPushButton {
                background-color: transparent;
                color: #6c7086;
                border: none;
                font-size: 22px;
                min-width: 44px; min-height: 44px;
                max-width: 44px; max-height: 44px;
            }
            QPushButton:hover { color: #cba6f7; }
            QPushButton:pressed { color: #b48eed; }
        """
        btn_play_style = """
            QPushButton {
                background-color: transparent;
                color: #cba6f7;
                border: none;
                font-size: 26px;
                min-width: 52px; min-height: 52px;
                max-width: 52px; max-height: 52px;
            }
            QPushButton:hover { color: #d0bcff; }
            QPushButton:pressed { color: #b48eed; }
        """

        self.btn_prev = QPushButton("⏮"); self.btn_prev.setStyleSheet(btn_style); self.btn_prev.clicked.connect(self._prev)
        self.btn_play = QPushButton("▶"); self.btn_play.setStyleSheet(btn_play_style); self.btn_play.clicked.connect(self._play_pause)
        self.btn_stop = QPushButton("⏹"); self.btn_stop.setStyleSheet(btn_style); self.btn_stop.clicked.connect(self._stop)
        self.btn_next = QPushButton("⏭"); self.btn_next.setStyleSheet(btn_style); self.btn_next.clicked.connect(self._next)

        for b in [self.btn_prev, self.btn_play, self.btn_stop, self.btn_next]:
            ctrl_layout.addWidget(b)
        card_layout.addLayout(ctrl_layout)

        vol_layout = QHBoxLayout()
        vol_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vol_label = QLabel("🔊"); vol_label.setStyleSheet("font-size: 14px;")
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100); self.vol_slider.setValue(70); self.vol_slider.setFixedWidth(180)
        self.vol_slider.setStyleSheet("""
            QSlider::groove:horizontal { height: 4px; background: #313244; border-radius: 2px; }
            QSlider::handle:horizontal { background: #a6e3a1; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::sub-page:horizontal { background: #a6e3a1; border-radius: 2px; }
        """)
        self.vol_slider.valueChanged.connect(self._on_volume)
        self.player.set_volume(70)
        vol_layout.addWidget(vol_label); vol_layout.addWidget(self.vol_slider)
        card_layout.addLayout(vol_layout)

        add_layout = QHBoxLayout()
        self.entry_url = QLineEdit()
        self.entry_url.setPlaceholderText("Lipește link YouTube aici...")
        self.entry_url.setStyleSheet("""
            QLineEdit { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a;
                        border-radius: 8px; padding: 8px 12px; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #cba6f7; }
        """)
        self.entry_url.returnPressed.connect(self._add_song)

        btn_add = QPushButton("➕ Adaugă")
        btn_add.setFixedHeight(38)
        btn_add.setStyleSheet("""
            QPushButton { background-color: #cba6f7; color: #1e1e2e; border: none;
                          border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background-color: #d0bcff; }
        """)
        btn_add.clicked.connect(self._add_song)
        add_layout.addWidget(self.entry_url); add_layout.addWidget(btn_add)
        card_layout.addLayout(add_layout)

        self.lbl_add_status = QLabel("")
        self.lbl_add_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_add_status.setStyleSheet("font-size: 11px; color: #6c7086;")
        card_layout.addWidget(self.lbl_add_status)

        pl_label = QLabel("📋 Playlist")
        pl_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #cdd6f4;")
        card_layout.addWidget(pl_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(220)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { background: #313244; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #585b70; border-radius: 3px; }
        """)

        self.playlist_container = QWidget()
        self.playlist_container.setStyleSheet("background-color: transparent;")
        self.playlist_layout = QVBoxLayout(self.playlist_container)
        self.playlist_layout.setContentsMargins(0, 0, 0, 0)
        self.playlist_layout.setSpacing(4)
        self.playlist_layout.addStretch()

        scroll.setWidget(self.playlist_container)
        card_layout.addWidget(scroll)

        main_layout.addWidget(card)
        main_layout.addStretch()

    def _refresh_playlist(self):
        self._download_bars.clear()
        while self.playlist_layout.count() > 1:
            item = self.playlist_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        titles = self.player.get_playlist()
        if not titles:
            lbl = QLabel("Playlist gol — adaugă melodii!")
            lbl.setStyleSheet("color: #6c7086; padding: 10px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.playlist_layout.insertWidget(0, lbl)
            return

        for i, title in enumerate(titles):
            entry = self.player.playlist[i]
            is_local = get_local_path(title) is not None
            is_current = (i == self.player.current_index)

            # Container rand
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(2)

            row = QFrame()
            row.setStyleSheet("QFrame { background-color: #1e1e2e; border-radius: 8px; }")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 4, 8, 4)

            # Icona local/online
            icon = "💾 " if is_local else "🌐 "
            prefix = "▶ " if is_current else ""
            btn = QPushButton(f"{prefix}{icon}{title}")
            btn.setStyleSheet(f"""
                QPushButton {{ background: transparent; color: {'#cba6f7' if is_current else '#cdd6f4'};
                               border: none; text-align: left; font-size: 12px;
                               {'font-weight: bold;' if is_current else ''} }}
                QPushButton:hover {{ color: #cba6f7; }}
            """)
            btn.clicked.connect(lambda _, x=i: self._play_index(x))

            # Buton download (doar daca nu e deja descarcat)
            if not is_local:
                btn_dl = QPushButton("⬇️")
                btn_dl.setFixedSize(28, 28)
                btn_dl.setToolTip("Descarcă offline")
                btn_dl.setStyleSheet("""
                    QPushButton { background: transparent; border: none; color: #89dceb; font-size: 14px; }
                    QPushButton:hover { color: #a6e3a1; }
                    QPushButton:disabled { color: #45475a; }
                """)
                btn_dl.clicked.connect(lambda _, x=i, t=title, u=entry["url"], b=btn_dl: self._start_download(x, t, u, b))
            else:
                btn_dl = QLabel("✅")
                btn_dl.setFixedSize(28, 28)
                btn_dl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                btn_dl.setStyleSheet("background: transparent; font-size: 14px;")
                btn_dl.setToolTip("Disponibil offline")

            btn_del = QPushButton("🗑")
            btn_del.setFixedSize(28, 28)
            btn_del.setStyleSheet("QPushButton { background: transparent; border: none; color: #6c7086; font-size: 14px; } QPushButton:hover { color: #f38ba8; }")
            btn_del.clicked.connect(lambda _, x=i: self._remove_song(x))

            row_layout.addWidget(btn)
            row_layout.addWidget(btn_dl)
            row_layout.addWidget(btn_del)
            container_layout.addWidget(row)

            # Bara progres download (ascunsa initial)
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setFixedHeight(4)
            progress_bar.setTextVisible(False)
            progress_bar.setVisible(False)
            progress_bar.setStyleSheet("""
                QProgressBar { background: #313244; border-radius: 2px; border: none; }
                QProgressBar::chunk { background: #a6e3a1; border-radius: 2px; }
            """)
            container_layout.addWidget(progress_bar)
            self._download_bars[i] = progress_bar

            self.playlist_layout.insertWidget(i, container)

    # ── Download ──────────────────────────────────────────────────────────

    def _start_download(self, index, title, url, btn):
        btn.setEnabled(False)
        btn.setText("⏳")
        if index in self._download_bars:
            self._download_bars[index].setVisible(True)

        download_song(
            url=url,
            title=title,
            progress_callback=lambda p: self.download_progress_signal.emit(index, p),
            done_callback=lambda path: self.download_done_signal.emit(index, path),
            error_callback=lambda err: self.download_error_signal.emit(index, err),
        )

    def _on_download_progress(self, index, percent):
        if index in self._download_bars:
            self._download_bars[index].setValue(int(percent))

    def _on_download_done(self, index, filepath):
        self.lbl_add_status.setStyleSheet("color: #a6e3a1; font-size: 11px;")
        self.lbl_add_status.setText(f"✅ Descărcat cu succes!")
        self._refresh_playlist()

    def _on_download_error(self, index, err):
        # Verifica daca lipseste ffmpeg
        if "ffmpeg" in err.lower() or "postprocessor" in err.lower():
            self.lbl_add_status.setStyleSheet("color: #f9e2af; font-size: 11px;")
            self.lbl_add_status.setText("⚠️ Instalează ffmpeg pentru download MP3")
        else:
            self.lbl_add_status.setStyleSheet("color: #f38ba8; font-size: 11px;")
            self.lbl_add_status.setText(f"❌ Eroare download: {err[:60]}")
        if index in self._download_bars:
            self._download_bars[index].setVisible(False)
        self._refresh_playlist()

    # ── Player controls ───────────────────────────────────────────────────

    def _update_progress(self, pos):
        self.progress_slider.setValue(int(pos * 1000))
        elapsed, total = self.player.get_time()
        self.lbl_elapsed.setText(self._format_time(elapsed))
        self.lbl_total.setText(self._format_time(total))

    def _update_status(self, status):
        self.lbl_status.setText(status)
        self.btn_play.setText("⏸" if "Se reda" in status else "▶")
        self._refresh_playlist()

    def _update_title(self, title):
        self.lbl_title.setText(title)

    def _play_pause(self):
        if self.player.is_playing:
            self.player.pause()
        else:
            self.player.play()

    def _stop(self): self.player.stop()
    def _next(self): self.player.next_track()
    def _prev(self): self.player.prev_track()
    def _play_index(self, index): self.player.play(index)
    def _on_volume(self, val): self.player.set_volume(val)
    def _on_seek(self, val): self.player.seek(val / 1000.0)

    def _add_song(self):
        url = self.entry_url.text().strip()
        if not url:
            return
        self.lbl_add_status.setStyleSheet("color: #6c7086; font-size: 11px;")
        self.lbl_add_status.setText("⏳ Se caută melodia...")
        self._add_thread = AddSongThread(self.player, url)
        self._add_thread.finished.connect(self._on_add_success)
        self._add_thread.error.connect(self._on_add_error)
        self._add_thread.start()

    def _on_add_success(self, title):
        self.entry_url.clear()
        short = title[:50] + ("..." if len(title) > 50 else "")
        self.lbl_add_status.setStyleSheet("color: #a6e3a1; font-size: 11px;")
        self.lbl_add_status.setText(f"✅ Adăugat: {short}")
        self._refresh_playlist()

    def _on_add_error(self, err):
        self.lbl_add_status.setStyleSheet("color: #f38ba8; font-size: 11px;")
        self.lbl_add_status.setText(f"❌ {err}")

    def _remove_song(self, index):
        self.player.remove_from_playlist(index)
        self._refresh_playlist()

    @staticmethod
    def _format_time(seconds):
        seconds = max(0, int(seconds))
        m, s = divmod(seconds, 60)
        return f"{m}:{s:02d}"