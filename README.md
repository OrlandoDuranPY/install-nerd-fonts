# Nerd Fonts — Descarga e Instalación Automática

Scripts en Python para descargar e instalar todas las [Nerd Fonts](https://www.nerdfonts.com/) en Windows, Linux o macOS. No requieren librerías externas, solo Python 3.6+.

---

## Requisitos

- Python 3.6 o superior
- Conexión a internet (para la descarga)
- Windows 10/11, Linux (con `fontconfig`) o macOS
- Windows: permisos de **Administrador** (solo para instalar). Linux/macOS: root opcional para instalar en todo el sistema

---

## Scripts incluidos

| Archivo | Descripción |
|---|---|
| `download_fonts.py` | Descarga los 70 ZIPs de Nerd Fonts desde GitHub |
| `install_fonts.py` | Descomprime e instala las fuentes en el directorio del sistema |

---

## Paso 1 — Descargar las fuentes

```bash
python download_fonts.py
```

Por defecto guarda los ZIPs en `./nerd-fonts` (junto al script).
Puedes especificar otro directorio como argumento:

```bash
python download_fonts.py /ruta/destino
```

### ¿Qué hace?

- Descarga los 70 ZIPs de Nerd Fonts v3.4.0 desde GitHub Releases
- Muestra una barra de progreso en tiempo real para cada fuente
- **Omite los ZIPs que ya existen**, por lo que puedes relanzarlo si se corta la conexión
- Reintenta automáticamente hasta 3 veces si falla una descarga
- Al finalizar muestra un resumen con las fuentes descargadas y las que fallaron

### Ejemplo de salida

```
==================================================
  Nerd Fonts Downloader — v3.4.0
  Total de fuentes : 70
  Destino          : /home/usuario/install-nerd-fonts/nerd-fonts
==================================================
[01/70] 0xProto                              ↓ Descargando...
  [██████████████████████████████] 2.1 MB / 2.1 MB (100%)
  ✓ OK (2.1 MB)
[02/70] 3270                                 ↓ Descargando...
  ...
==================================================
  Descarga completada
  ✓ Exitosas : 70 / 70
  ✗ Fallidas  : 0 / 70
  Archivos en: /home/usuario/install-nerd-fonts/nerd-fonts
==================================================
```

---

## Paso 2 — Instalar las fuentes

> ⚠️ **En Windows, este script debe ejecutarse como Administrador. En Linux/macOS no es obligatorio** (sin root instala solo para tu usuario).

```bash
python install_fonts.py
```

Si descargaste los ZIPs en un directorio diferente al predeterminado:

```bash
python install_fonts.py /ruta/nerd-fonts
```

### ¿Cómo ejecutar como Administrador / root?

**Windows — Opción A (menú de inicio):**
1. Busca `cmd` o `PowerShell`
2. Haz clic derecho → **Ejecutar como administrador**
3. Navega a la carpeta del script y ejecútalo

**Windows — Opción B (Explorador de archivos):**
1. Navega hasta `install_fonts.py`
2. Haz clic derecho sobre el archivo
3. Selecciona **Abrir con → Python** (si tienes Python asociado)

> En Windows, si no tienes permisos de administrador, el script lo detecta automáticamente y muestra un mensaje de error antes de salir.

**Linux:**
- Sin `sudo`: instala solo para tu usuario en `~/.local/share/fonts/nerd-fonts` (recomendado)
- Con `sudo python install_fonts.py`: instala para todos los usuarios en `/usr/share/fonts/nerd-fonts`

**macOS:**
- Sin `sudo`: instala solo para tu usuario en `~/Library/Fonts/nerd-fonts`
- Con `sudo python install_fonts.py`: instala para todos los usuarios en `/Library/Fonts/nerd-fonts`

### ¿Qué hace?

- Descomprime cada ZIP en una carpeta temporal (se limpia automáticamente al terminar)
- Busca archivos `.ttf` y `.otf` dentro de cada ZIP de forma recursiva
- Copia las fuentes al directorio de fuentes del sistema:
  - Windows: `C:\Windows\Fonts`, registrándolas en el Registro de Windows
  - Linux: `~/.local/share/fonts/nerd-fonts` (o `/usr/share/fonts/nerd-fonts` con root)
  - macOS: `~/Library/Fonts/nerd-fonts` (o `/Library/Fonts/nerd-fonts` con root)
- **Omite fuentes que ya están instaladas**
- Al finalizar, notifica al sistema para que reconozca las fuentes sin reiniciar (Windows: mensaje `WM_FONTCHANGE`; Linux/macOS: `fc-cache -f`)

### Ejemplo de salida

```
==================================================
  Nerd Fonts Installer — Linux
  ZIPs encontrados : 70
  Fuentes destino  : /home/usuario/.local/share/fonts/nerd-fonts
==================================================

[01/70] 0xProto
  ✓ Instaladas: 8  |  Ya existían: 0
[02/70] 3270
  ✓ Instaladas: 6  |  Ya existían: 0
  ...
==================================================
  Instalación completada
  ✓ Fuentes instaladas  : 487
  ○ Ya existían         : 0
  ✗ ZIPs con problemas  : 0
==================================================
```

---

## Flujo completo recomendado

```bash
# 1. Descargar todos los ZIPs (sin permisos especiales)
python download_fonts.py

# 2. Instalar
python install_fonts.py          # Linux/macOS: para tu usuario
sudo python install_fonts.py     # Linux/macOS: para todo el sistema
# Windows: abrir terminal como Administrador antes de ejecutar
```

---

## Solución de problemas

| Problema | Solución |
|---|---|
| `✗ Se requieren permisos de Administrador` | (Windows) Ejecuta la terminal como Administrador |
| Descarga interrumpida | Vuelve a ejecutar `download_fonts.py`, omite los ZIPs ya descargados |
| `✗ ZIP corrupto` | Elimina el ZIP afectado de `./nerd-fonts` y vuelve a descargar |
| Las fuentes no aparecen en las apps | Cierra y vuelve a abrir la aplicación; si persiste, reinicia (Linux/macOS: verifica con `fc-list \| grep -i <fuente>`) |
| `⚠ No se pudo ejecutar fc-cache` | (Linux/macOS) Instala `fontconfig`: `sudo apt install fontconfig` / `sudo dnf install fontconfig` / `brew install fontconfig` |
| `✗ Directorio no encontrado` | Verifica la ruta del directorio o ejecuta primero el script de descarga |

---

## Notas

- Windows: las fuentes se instalan para **todos los usuarios** (requiere admin).
- Linux/macOS: por defecto se instalan solo para tu usuario; con `sudo` quedan para todo el sistema.
- La versión instalada es la **v3.4.0** de Nerd Fonts.
- El script de instalación es **idempotente**: ejecutarlo varias veces no duplica fuentes.
- Para desinstalar: Windows, ve a `C:\Windows\Fonts` y elimina las fuentes manualmente. Linux, borra el contenido de `~/.local/share/fonts/nerd-fonts` (o `/usr/share/fonts/nerd-fonts`) y ejecuta `fc-cache -f`. macOS, borra `~/Library/Fonts/nerd-fonts` (o `/Library/Fonts/nerd-fonts`).
