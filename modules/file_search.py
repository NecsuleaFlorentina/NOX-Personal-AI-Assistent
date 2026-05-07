import os
from pathlib import Path


def cauta_fisiere(termen: str, folder: str = None, max_rezultate: int = 50) -> list:
    rezultate = []
    termen = termen.lower().strip()

    if not termen:
        return []

    if folder:
        locatii = [Path(folder)]
    else:
        locatii = [
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Pictures",
            Path.home() / "Music",
            Path.home() / "Videos",
        ]

    for locatie in locatii:
        if not locatie.exists():
            continue
        try:
            for root, dirs, files in os.walk(locatie):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for fisier in files:
                    if termen in fisier.lower():
                        rezultate.append(str(Path(root) / fisier))
                        if len(rezultate) >= max_rezultate:
                            return rezultate
        except PermissionError:
            continue

    return rezultate


def deschide_fisier(cale: str):
    os.startfile(cale)


def deschide_folder(cale: str):
    os.startfile(str(Path(cale).parent))