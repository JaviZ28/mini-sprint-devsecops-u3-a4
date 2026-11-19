# API de práctica DevSecOps

API local corregida: consulta parametrizada, contraseñas con hash y credenciales en variables de entorno.

## Ejecución en PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Crea `.env` a partir de `.env.example` y asigna valores privados a `API_KEY`, `ADMIN_PASSWORD` y `STUDENT_PASSWORD`. No compartas ni subas `.env`. Para generar valores aleatorios en un archivo nuevo:

```powershell
.\.venv\Scripts\python -c "from pathlib import Path; import secrets; Path('.env').open('x').writelines(k+'='+secrets.token_hex(24)+'\n' for k in ('API_KEY','ADMIN_PASSWORD','STUDENT_PASSWORD'))"
.\.venv\Scripts\python app.py
```

La API escucha en `127.0.0.1:5000`. `GET /api/health` comprueba el servicio; `GET /api/profile` requiere `X-API-Key`; `POST /api/login` recibe `username` y `password` de las cuentas `admin` o `estudiante`. La base `practica_sprint.db` es independiente de la base original. Al reiniciar se actualizan los hashes a partir de las contraseñas del entorno.

## Pruebas

```powershell
.\.venv\Scripts\python -m unittest -v
```

El flujo de GitHub Actions ejecuta Bandit, pip-audit, pruebas y genera un SBOM.
