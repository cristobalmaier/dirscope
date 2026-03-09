# DIRSCOPE - Directory & File Fuzzer

```
  ██████╗ ██╗██████╗ ███████╗ ██████╗ ██████╗ ██████╗ ███████╗
  ██╔══██╗██║██╔══██╗██╔════╝██╔════╝██╔════╝██╔═══██╗██╔════╝
  ██║  ██║██║██████╔╝███████╗██║     ██║     ██║   ██║█████╗
  ██║  ██║██║██╔══██╗╚════██║██║     ██║     ██║   ██║██╔══╝
  ██████╔╝██║██║  ██║███████║╚██████╗╚██████╗╚██████╔╝███████╗
  ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝╚══════╝
```

Fuzzer de directorios y archivos web escrito en Python puro. Descubre rutas ocultas en servidores HTTP/HTTPS usando una wordlist, similar a ffuf o dirbuster.


---

## Requisitos

- Python 3.6+
- Sin dependencias externas

---

## Uso

```bash
python3 dirscope.py <url> <wordlist> [hilos]
```

### Ejemplos

```bash
# Escaneo básico (30 hilos por defecto)
python3 dirscope.py http://172.17.0.2 /usr/share/wordlists/dirb/common.txt

# Más hilos para ir más rápido
python3 dirscope.py http://172.17.0.2 /usr/share/wordlists/dirb/common.txt 50

# Con wordlist más grande
python3 dirscope.py http://172.17.0.2 /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

---

## Sistema de colores

| Color | Código HTTP | Significado |
|-------|-------------|-------------|
| Verde | 200 OK | Accesible — directorio o archivo encontrado |
| Cyan | 301 / 302 | Existe pero redirige a otra ruta |
| Amarillo | 401 / 403 | Existe pero está protegido o bloqueado |
| Rojo | 500 | Error del servidor — puede ser interesante |

> El **403 Forbidden** es tan valioso como un 200 — confirma que el recurso existe aunque no puedas acceder todavía.

---

## Wordlists recomendadas (Kali Linux)

```
/usr/share/wordlists/dirb/common.txt                             #  4,613 palabras  (rápido)
/usr/share/wordlists/dirb/big.txt                                # 20,469 palabras  (completo)
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt     #  220k  palabras  (exhaustivo)
```

---

## Aviso legal

Solo usar en sistemas sobre los que tenés permiso explícito. El uso no autorizado puede ser ilegal según las leyes de tu país.