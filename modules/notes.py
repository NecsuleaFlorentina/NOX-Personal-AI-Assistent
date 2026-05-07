import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/notes.json")

CULORI = {
    "violet": "#cba6f7",
    "verde": "#a6e3a1",
    "albastru": "#89dceb",
    "portocaliu": "#fab387",
    "roz": "#f38ba8",
    "galben": "#f9e2af",
}


def _incarca() -> list:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _salveaza(notite: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notite, f, ensure_ascii=False, indent=2)


def adauga_notita(titlu: str, continut: str, culoare: str = "violet") -> dict:
    notite = _incarca()
    notita = {
        "id": f"n_{int(datetime.now().timestamp())}",
        "titlu": titlu,
        "continut": continut,
        "culoare": culoare,
        "creat_la": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "modificat_la": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    notite.append(notita)
    _salveaza(notite)
    return notita


def editeaza_notita(nid: str, titlu: str, continut: str, culoare: str):
    notite = _incarca()
    for n in notite:
        if n["id"] == nid:
            n["titlu"] = titlu
            n["continut"] = continut
            n["culoare"] = culoare
            n["modificat_la"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            break
    _salveaza(notite)


def sterge_notita(nid: str):
    notite = [n for n in _incarca() if n["id"] != nid]
    _salveaza(notite)


def lista_notite() -> list:
    return _incarca()