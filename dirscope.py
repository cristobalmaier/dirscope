#!/usr/bin/env python3
"""
DIRSCOPE - Directory & File Fuzzer
Uso: python3 dirscope.py <url> <wordlist>
"""

import sys
import urllib.request
import urllib.error
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Colores ──────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GRAY   = "\033[90m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
BLUE   = "\033[94m"

# ── Color por código de respuesta HTTP ───────────────
STATUS_COLOR = {
    200: GREEN,   # OK — encontrado
    201: GREEN,   # Created
    204: GREEN,   # No Content
    301: CYAN,    # Redirect permanente
    302: CYAN,    # Redirect temporal
    307: CYAN,    # Redirect temporal
    308: CYAN,    # Redirect permanente
    401: YELLOW,  # Unauthorized — existe pero requiere auth
    403: YELLOW,  # Forbidden — existe pero bloqueado
    405: YELLOW,  # Method Not Allowed
    500: RED,     # Error interno — puede ser interesante
    503: RED,     # Service Unavailable
}

STATUS_LABEL = {
    200: "OK",
    201: "CREATED",
    204: "NO CONTENT",
    301: "MOVED",
    302: "FOUND",
    307: "REDIRECT",
    308: "PERMANENT",
    401: "AUTH REQ",
    403: "FORBIDDEN",
    405: "NOT ALLOWED",
    500: "SERVER ERR",
    503: "UNAVAILABLE",
}


def banner():
    print(f"""
\033[92m\033[1m  ██████╗ ██╗██████╗ ███████╗ ██████╗ ██████╗ ██████╗ ███████╗
  ██╔══██╗██║██╔══██╗██╔════╝██╔════╝██╔════╝██╔═══██╗██╔════╝
  ██║  ██║██║██████╔╝███████╗██║     ██║     ██║   ██║█████╗
  ██║  ██║██║██╔══██╗╚════██║██║     ██║     ██║   ██║██╔══╝
  ██████╔╝██║██║  ██║███████║╚██████╗╚██████╗╚██████╔╝███████╗
  ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝╚══════╝\033[0m
\033[90m  Directory & File Fuzzer  |  Solo usar en sitios con permiso\033[0m
""")


def probe(base_url, word):
    """Hace una petición HTTP y devuelve (word, status, size, location)."""
    url = f"{base_url}/{word}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dirscope/1.0"})
        res = urllib.request.urlopen(req, timeout=5)
        size     = len(res.read())
        location = res.geturl()
        return (word, res.status, size, location)
    except urllib.error.HTTPError as e:
        if e.code in STATUS_COLOR:
            return (word, e.code, 0, "")
        return None
    except:
        return None


def load_wordlist(path):
    """Lee el archivo de palabras, una por línea."""
    try:
        with open(path, "r", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return words
    except FileNotFoundError:
        print(f"  {RED}[!] Wordlist no encontrada: {path}{RESET}\n")
        sys.exit(1)


def main():
    banner()

    if len(sys.argv) < 3:
        print(f"  Uso: python3 dirscope.py <url> <wordlist> [hilos]")
        print(f"  Ej:  python3 dirscope.py http://192.168.1.1 /usr/share/wordlists/dirb/common.txt")
        print(f"  Ej:  python3 dirscope.py http://10.0.0.1 wordlist.txt 50\n")
        sys.exit(0)

    base_url = sys.argv[1].rstrip("/")
    wordlist = sys.argv[2]
    threads  = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    words = load_wordlist(wordlist)

    # Info del escaneo
    start = datetime.now()
    print(f"  {GRAY}Target  :{RESET} {BOLD}{WHITE}{base_url}{RESET}")
    print(f"  {GRAY}Wordlist:{RESET} {WHITE}{wordlist}{RESET} {GRAY}({len(words)} palabras){RESET}")
    print(f"  {GRAY}Hilos   :{RESET} {WHITE}{threads}{RESET}")
    print(f"  {GRAY}Inicio  :{RESET} {WHITE}{start.strftime('%H:%M:%S')}{RESET}\n")

    print(f"  {GRAY}{'STATUS':<12} {'SIZE':>8}   {'URL'}{RESET}")
    print(f"  {GRAY}{'─'*65}{RESET}")

    found   = []
    scanned = 0
    total   = len(words)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(probe, base_url, w): w for w in words}
        for future in as_completed(futures):
            scanned += 1
            result = future.result()

            # Progreso en la misma línea
            pct = int((scanned / total) * 40)
            bar = f"[{'=' * pct}{' ' * (40 - pct)}]"
            print(f"\r  {GRAY}{bar} {scanned}/{total}{RESET}", end="", flush=True)

            if result:
                word, status, size, location = result
                color = STATUS_COLOR.get(status, WHITE)
                label = STATUS_LABEL.get(status, str(status))
                url   = location or f"{base_url}/{word}"

                # Limpiar la línea de progreso e imprimir resultado
                print(f"\r  {' '*60}\r", end="")
                print(f"  {BOLD}{color}[{status} {label}]{RESET}  {size:>7} bytes   {color}{url}{RESET}")
                found.append(result)

    # Limpiar barra de progreso
    print(f"\r  {' '*60}")

    # Resumen
    elapsed = (datetime.now() - start).total_seconds()
    print(f"  {GRAY}{'─'*65}{RESET}")
    print(f"  {BOLD}{WHITE}Resultados: {len(found)} encontrados / {total} probados{RESET}")
    print()

    if found:
        # Agrupar por status
        by_status = {}
        for word, status, size, location in sorted(found, key=lambda x: x[1]):
            by_status.setdefault(status, []).append((word, size, location))

        for status, items in sorted(by_status.items()):
            color = STATUS_COLOR.get(status, WHITE)
            label = STATUS_LABEL.get(status, str(status))
            print(f"  {color}{BOLD}[{status} {label}]{RESET}  {GRAY}({len(items)} rutas){RESET}")
            for word, size, loc in items:
                url = loc or f"{base_url}/{word}"
                print(f"  {GRAY}  └─{RESET} {color}{url}{RESET}  {GRAY}({size} bytes){RESET}")
            print()

    print(f"  {GRAY}Dirscope done: {elapsed:.2f}s — {len(found)} rutas encontradas{RESET}\n")


if __name__ == "__main__":
    main()