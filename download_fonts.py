#!/usr/bin/env python3
"""
download_nerd_fonts.py
Descarga todos los ZIPs de Nerd Fonts v3.4.0
Uso: python download_nerd_fonts.py [directorio_destino]
"""

import sys
import os
import urllib.request
import urllib.error
import time

BASE_URL = "https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0"

FONTS = [
    "0xProto", "3270", "AdwaitaMono", "Agave", "AnonymousPro",
    "Arimo", "AtkinsonHyperlegibleMono", "AurulentSansMono", "BigBlueTerminal",
    "BitstreamVeraSansMono", "IBMPlexMono", "CascadiaCode", "CascadiaMono",
    "CodeNewRoman", "ComicShannsMono", "CommitMono", "Cousine", "D2Coding",
    "DaddyTimeMono", "DejaVuSansMono", "DepartureMono", "DroidSansMono",
    "EnvyCodeR", "FantasqueSansMono", "FiraCode", "FiraMono", "GeistMono",
    "Go-Mono", "Gohu", "Hack", "Hasklig", "HeavyData", "Hermit", "iA-Writer",
    "Inconsolata", "InconsolataGo", "InconsolataLGC", "IntelOneMono",
    "Iosevka", "IosevkaTerm", "IosevkaTermSlab", "JetBrainsMono", "Lekton",
    "LiberationMono", "Lilex", "MartianMono", "Meslo", "Monaspace", "Monofur",
    "Monoid", "Mononoki", "MPlus", "Noto", "OpenDyslexic", "Overpass",
    "ProFont", "ProggyClean", "Recursive", "RobotoMono", "ShareTechMono",
    "SourceCodePro", "SpaceMono", "NerdFontsSymbolsOnly", "Terminus", "Tinos",
    "Ubuntu", "UbuntuMono", "UbuntuSans", "VictorMono", "ZedMono",
]


def format_size(bytes_count):
    for unit in ("B", "KB", "MB"):
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} GB"


def show_progress(downloaded, total):
    bar_width = 30
    pct = downloaded / total if total else 0
    filled = int(bar_width * pct)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"\r  [{bar}] {format_size(downloaded)} / {format_size(total)} ({pct:.0%})", end="", flush=True)


def download_font(url, dest_path, retries=3):
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 8192
                with open(dest_path, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            show_progress(downloaded, total)
            print()  # nueva línea tras la barra
            return os.path.getsize(dest_path)
        except Exception as e:
            print()
            if attempt < retries:
                print(f"  ⚠ Intento {attempt} fallido ({e}). Reintentando...")
                time.sleep(2)
            else:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                raise


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "nerd-fonts")
    os.makedirs(dest, exist_ok=True)

    total = len(FONTS)
    exitosas = 0
    fallidas = []

    print("=" * 54)
    print("  Nerd Fonts Downloader — v3.4.0")
    print(f"  Total de fuentes : {total}")
    print(f"  Destino          : {dest}")
    print("=" * 54)

    for i, font in enumerate(FONTS, start=1):
        url = f"{BASE_URL}/{font}.zip"
        path = os.path.join(dest, f"{font}.zip")
        prefix = f"[{i:02d}/{total}] {font:<35}"

        if os.path.exists(path):
            print(f"{prefix} → Ya existe, omitiendo.")
            exitosas += 1
            continue

        print(f"{prefix} ↓ Descargando...")
        try:
            size = download_font(url, path)
            print(f"  ✓ OK ({format_size(size)})")
            exitosas += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            fallidas.append(font)

    print()
    print("=" * 54)
    print("  Descarga completada")
    print(f"  ✓ Exitosas : {exitosas} / {total}")
    print(f"  ✗ Fallidas  : {len(fallidas)} / {total}")
    if fallidas:
        print(f"  Fuentes fallidas: {', '.join(fallidas)}")
    print(f"  Archivos en: {dest}")
    print("=" * 54)


if __name__ == "__main__":
    main()