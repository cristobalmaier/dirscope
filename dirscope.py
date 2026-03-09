#!/usr/bin/env python3
"""
DIRSCOPE - Directory & File Fuzzer
Uso: python3 dirscope.py <url> <wordlist> [hilos]
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

STATUS_COLOR = {
    200: GREEN,
    201: GREEN,
    204: GREEN,
    301: CYAN,
    302: CYAN,
    307: CYAN,
    308: CYAN,
    401: YELLOW,
    403: YELLOW,
    405: YELLOW,
    500: RED,
    503: RED,
}

STATUS_LABEL = {
    200: "OK",
    201: "CREATED",
    204: "NO CONTENT",
    301: "MOVED",
    302: "FOUND",
    307: "REDIRECT",
    308: "PERMANENT",
    401: "UNAUTH",
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
\033[90m  \033[0m
""")


def probe(base_url, word):
    """Hace una peticion HTTP. Devuelve (word, status, size, url) o None."""
    url = f"{base_url}/{word}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "dirscope/1.0"})
        res = urllib.request.urlopen(req, timeout=5)
        size = len(res.read())
        return (word, res.status, size, res.geturl())
    except urllib.error.HTTPError as e:
        if e.code in STATUS_COLOR:
            return (word, e.code, 0, url)
        return None
    except:
        return None


def load_wordlist(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("#")]
    except FileNotFoundError:
        print(f"  {RED}[!] Wordlist no encontrada: {path}{RESET}\n")
        sys.exit(1)


def fmt_size(size):
    """Formatea bytes de forma legible."""
    if size >= 1024:
        return f"{size/1024:.1f} KB"
    return f"{size} B"


def main():
    banner()

    if len(sys.argv) < 3:
        print(f"  Uso: python3 dirscope.py <url> <wordlist> [hilos]")
        print(f"  Ej:  python3 dirscope.py http://172.17.0.2 /usr/share/wordlists/dirb/common.txt\n")
        sys.exit(0)

    base_url = sys.argv[1].rstrip("/")
    wordlist = sys.argv[2]
    threads  = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    words    = load_wordlist(wordlist)
    start    = datetime.now()

    # ── Info del escaneo ─────────────────────────────
    print(f"  {GRAY}Target   {RESET} {BOLD}{WHITE}{base_url}{RESET}")
    print(f"  {GRAY}Wordlist {RESET} {WHITE}{wordlist}{RESET}  {GRAY}({len(words)} palabras){RESET}")
    print(f"  {GRAY}Hilos    {RESET} {WHITE}{threads}{RESET}")
    print(f"  {GRAY}Inicio   {RESET} {WHITE}{start.strftime('%H:%M:%S')}{RESET}")

    # ── Cabecera de tabla ────────────────────────────
    print(f"\n  {GRAY}{'─'*68}{RESET}")
    print(f"  {GRAY}{'STATUS':<18} {'SIZE':>8}   {'URL'}{RESET}")
    print(f"  {GRAY}{'─'*68}{RESET}\n")

    found   = []
    scanned = 0
    total   = len(words)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(probe, base_url, w): w for w in words}
        for future in as_completed(futures):
            scanned += 1
            result = future.result()

            # Barra de progreso
            pct = int((scanned / total) * 40)
            bar = f"{'=' * pct}{' ' * (40 - pct)}"
            print(f"\r  {GRAY}[{bar}] {scanned}/{total}{RESET}", end="", flush=True)

            if result:
                word, status, size, url = result
                color = STATUS_COLOR.get(status, WHITE)
                label = STATUS_LABEL.get(status, str(status))
                tag   = f"[{status} {label}]"
                size_str = fmt_size(size)

                # Limpiar barra e imprimir resultado alineado
                print(f"\r  {' '*60}\r", end="")
                print(f"  {BOLD}{color}{tag:<18}{RESET} {GRAY}{size_str:>8}{RESET}   {color}{url}{RESET}")
                found.append(result)

    # Limpiar barra final
    print(f"\r  {' '*60}\r", end="")

    # ── Resumen ──────────────────────────────────────
    elapsed = (datetime.now() - start).total_seconds()
    print(f"\n  {GRAY}{'─'*68}{RESET}")
    print(f"  {BOLD}{WHITE}{len(found)} encontrados{RESET}  {GRAY}/{RESET}  {WHITE}{total} probados{RESET}  {GRAY}|  {elapsed:.2f}s{RESET}")
    print(f"  {GRAY}{'─'*68}{RESET}\n")

    if found:
        by_status = {}
        for w, status, size, url in sorted(found, key=lambda x: x[1]):
            by_status.setdefault(status, []).append((size, url))

        for status, items in sorted(by_status.items()):
            color = STATUS_COLOR.get(status, WHITE)
            label = STATUS_LABEL.get(status, str(status))
            print(f"  {BOLD}{color}[{status} {label}]{RESET}  {GRAY}{len(items)} ruta(s){RESET}")
            for size, url in items:
                print(f"  {GRAY}  └─{RESET}  {color}{url:<50}{RESET}  {GRAY}{fmt_size(size)}{RESET}")
            print()

    print(f"  {GRAY}Dirscope done: {elapsed:.2f}s — {len(found)} rutas encontradas{RESET}\n")


if __name__ == "__main__":
    main()