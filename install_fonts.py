#!/usr/bin/env python3
"""
install_nerd_fonts.py
Descomprime e instala todas las Nerd Fonts en Windows o Linux.
En Windows, debe ejecutarse como Administrador para instalar para todos los usuarios.
En Linux, instala en ~/.local/share/fonts (o /usr/share/fonts si se ejecuta como root).

Uso:
  python install_nerd_fonts.py [directorio_con_zips]

Por defecto busca los ZIPs en: ~/nerd-fonts
"""

import sys
import os
import zipfile
import shutil
import glob
import subprocess
import tempfile

# Extensiones de fuente válidas
FONT_EXTENSIONS = (".ttf", ".otf")

IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"

if IS_WINDOWS:
    import ctypes

    # Directorio de fuentes del sistema (para todos los usuarios, requiere admin)
    SYSTEM_FONTS_DIR = r"C:\Windows\Fonts"
    # Clave de registro para registrar las fuentes
    REG_FONTS_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
elif IS_MACOS:
    # Root instala para todos los usuarios; usuario normal instala solo para sí mismo
    SYSTEM_FONTS_DIR = (
        "/Library/Fonts/nerd-fonts"
        if os.geteuid() == 0
        else os.path.join(os.path.expanduser("~"), "Library", "Fonts", "nerd-fonts")
    )
else:
    # Root instala para todos los usuarios; usuario normal instala solo para sí mismo
    SYSTEM_FONTS_DIR = (
        "/usr/share/fonts/nerd-fonts"
        if os.geteuid() == 0
        else os.path.join(os.path.expanduser("~"), ".local", "share", "fonts", "nerd-fonts")
    )


def is_admin():
    if IS_WINDOWS:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    return os.geteuid() == 0


def get_font_name_from_file(font_path):
    """Devuelve el nombre del archivo sin extensión como nombre de registro."""
    return os.path.splitext(os.path.basename(font_path))[0]


def install_font(font_path):
    """
    Copia la fuente al directorio del sistema y la registra en el registro.
    Retorna True si fue instalada, False si ya existía.
    """
    font_filename = os.path.basename(font_path)
    dest_path = os.path.join(SYSTEM_FONTS_DIR, font_filename)

    # Si ya existe, omitir
    if os.path.exists(dest_path):
        return False

    # Copiar al directorio de fuentes
    shutil.copy2(font_path, dest_path)

    if not IS_WINDOWS:
        return True

    import winreg

    # Registrar en el registro de Windows
    font_name = get_font_name_from_file(font_path)
    ext = os.path.splitext(font_path)[1].lower()
    reg_value_name = f"{font_name} (TrueType)" if ext == ".ttf" else f"{font_name} (OpenType)"

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REG_FONTS_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, reg_value_name, 0, winreg.REG_SZ, font_filename)
    except Exception:
        pass  # La copia ya es suficiente en la mayoría de los casos

    return True


def notify_font_change():
    """Notifica al sistema que hubo cambios en las fuentes."""
    if IS_WINDOWS:
        HWND_BROADCAST = 0xFFFF
        WM_FONTCHANGE = 0x001D
        ctypes.windll.user32.PostMessageW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0)
    else:
        try:
            subprocess.run(["fc-cache", "-f"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"  ⚠ No se pudo ejecutar fc-cache: {e}")


def process_zip(zip_path, temp_dir):
    """Extrae fuentes de un ZIP e instálalas. Retorna (instaladas, omitidas)."""
    instaladas = 0
    omitidas = 0

    font_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_dir = os.path.join(temp_dir, font_name)
    os.makedirs(extract_dir, exist_ok=True)

    try:
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)
        except zipfile.BadZipFile:
            print(f"  ✗ ZIP corrupto, omitiendo.")
            return 0, 0
        except OSError as e:
            print(f"  ✗ Error de disco al extraer ({e}), omitiendo.")
            return 0, 0

        # Buscar fuentes recursivamente
        for ext in FONT_EXTENSIONS:
            for font_file in glob.glob(os.path.join(extract_dir, "**", f"*{ext}"), recursive=True):
                try:
                    if install_font(font_file):
                        instaladas += 1
                    else:
                        omitidas += 1
                except Exception as e:
                    print(f"  ⚠ No se pudo instalar {os.path.basename(font_file)}: {e}")

        return instaladas, omitidas
    finally:
        # Liberar espacio temporal de inmediato, no al final de todo el lote
        shutil.rmtree(extract_dir, ignore_errors=True)


def main():
    # Verificar permisos de administrador (solo obligatorio en Windows)
    if IS_WINDOWS and not is_admin():
        print("=" * 54)
        print("  ✗ Se requieren permisos de Administrador")
        print("  Haz clic derecho en el script y selecciona:")
        print("  'Ejecutar como administrador'")
        print("=" * 54)
        input("\nPresiona Enter para salir...")
        sys.exit(1)

    os.makedirs(SYSTEM_FONTS_DIR, exist_ok=True)

    # Directorio con los ZIPs
    zips_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "nerd-fonts")

    if not os.path.isdir(zips_dir):
        print(f"✗ Directorio no encontrado: {zips_dir}")
        sys.exit(1)

    zip_files = sorted(glob.glob(os.path.join(zips_dir, "*.zip")))

    if not zip_files:
        print(f"✗ No se encontraron archivos .zip en: {zips_dir}")
        sys.exit(1)

    total_zips = len(zip_files)
    total_instaladas = 0
    total_omitidas = 0
    total_errores = 0

    print("=" * 54)
    os_name = "Windows" if IS_WINDOWS else "macOS" if IS_MACOS else "Linux"
    print(f"  Nerd Fonts Installer — {os_name}")
    print(f"  ZIPs encontrados : {total_zips}")
    print(f"  Fuentes destino  : {SYSTEM_FONTS_DIR}")
    print("=" * 54)

    with tempfile.TemporaryDirectory(prefix="nerd_fonts_") as temp_dir:
        for i, zip_path in enumerate(zip_files, start=1):
            name = os.path.splitext(os.path.basename(zip_path))[0]
            print(f"\n[{i:02d}/{total_zips}] {name}")

            instaladas, omitidas = process_zip(zip_path, temp_dir)

            if instaladas == 0 and omitidas == 0:
                print(f"  ⚠ Sin fuentes válidas en el ZIP")
                total_errores += 1
            else:
                print(f"  ✓ Instaladas: {instaladas}  |  Ya existían: {omitidas}")
                total_instaladas += instaladas
                total_omitidas += omitidas

    # Notificar a Windows
    print(f"\n  Notificando cambios a {'Windows' if IS_WINDOWS else 'fontconfig'}...")
    notify_font_change()

    print()
    print("=" * 54)
    print("  Instalación completada")
    print(f"  ✓ Fuentes instaladas  : {total_instaladas}")
    print(f"  ○ Ya existían         : {total_omitidas}")
    print(f"  ✗ ZIPs con problemas  : {total_errores}")
    print("=" * 54)
    input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()