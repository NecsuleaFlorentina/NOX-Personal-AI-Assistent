import json
import winsound
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from PyQt6.QtCore import QObject, pyqtSignal


DATA_FILE = Path("data/reminders.json")


def _incarca():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _salveaza(remindere):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(remindere, f, ensure_ascii=False, indent=2)


class ReminderSignals(QObject):
    declansat = pyqtSignal(str, str)


class ReminderManager:
    def __init__(self):
        self.signals = ReminderSignals()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self._reincarca_din_json()

    def _reincarca_din_json(self):
        for r in _incarca():
            self._programeaza(r)

    def _programeaza(self, r):
        dt = datetime.fromisoformat(r["datetime"])

        if r.get("recurent") and r.get("zile_saptamana"):
            # Reminder recurent - se repeta in zilele selectate
            self.scheduler.add_job(
                self._declanseaza,
                trigger="cron",
                day_of_week=r["zile_saptamana"],
                hour=dt.hour,
                minute=dt.minute,
                args=[r["titlu"], r.get("mesaj", "Reminder!")],
                id=r["id"],
                replace_existing=True
            )
        else:
            # Reminder normal - o singura data
            if dt > datetime.now():
                self.scheduler.add_job(
                    self._declanseaza,
                    trigger="date",
                    run_date=dt,
                    args=[r["titlu"], r.get("mesaj", "Reminder!")],
                    id=r["id"],
                    replace_existing=True
                )

    def _declanseaza(self, titlu: str, mesaj: str):
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        self.signals.declansat.emit(titlu, mesaj)

    def adauga(self, titlu: str, mesaj: str, dt: datetime,
               recurent: bool = False, zile_saptamana: str = "") -> dict:
        remindere = _incarca()
        r = {
            "id": f"r_{int(dt.timestamp())}",
            "titlu": titlu,
            "mesaj": mesaj,
            "datetime": dt.isoformat(),
            "recurent": recurent,
            "zile_saptamana": zile_saptamana
        }
        remindere.append(r)
        _salveaza(remindere)
        self._programeaza(r)
        return r

    def sterge(self, rid: str):
        remindere = [r for r in _incarca() if r["id"] != rid]
        _salveaza(remindere)
        try:
            self.scheduler.remove_job(rid)
        except Exception:
            pass

    def lista(self) -> list:
        return _incarca()

    def opreste(self):
        self.scheduler.shutdown(wait=False)