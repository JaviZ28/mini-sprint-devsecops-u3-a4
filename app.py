from contextlib import closing
import hmac
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16384
DB_PATH = Path(__file__).with_name("practica_sprint.db")


def init_db():
    accounts = [(1, "admin", os.getenv("ADMIN_PASSWORD")),
                (2, "estudiante", os.getenv("STUDENT_PASSWORD"))]
    if not os.getenv("API_KEY") or any(not password for _, _, password in accounts):
        raise RuntimeError("Completa API_KEY, ADMIN_PASSWORD y STUDENT_PASSWORD en .env")
    with closing(sqlite3.connect(DB_PATH)) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)")
        for user_id, username, password in accounts:
            db.execute("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET password_hash = excluded.password_hash", (user_id, username, generate_password_hash(password)))


@app.get("/api/health")
def health():
    return jsonify(status="ok", service="API de práctica")


@app.get("/api/profile")
def profile():
    expected = os.getenv("API_KEY")
    supplied = request.headers.get("X-API-Key", "")
    if not expected or not hmac.compare_digest(expected.encode(), supplied.encode()):
        return jsonify(error="No autorizado"), 401
    return jsonify(user="admin", message="Acceso de demostración")


@app.post("/api/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Se esperaba un objeto JSON"), 400
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify(error="Envía username y password como texto"), 400
    with closing(sqlite3.connect(DB_PATH)) as db, db:
        user = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,)).fetchone()
    if user and check_password_hash(user[2], password):
        return jsonify(message="Login correcto", user={"id": user[0], "username": user[1]})
    return jsonify(error="Credenciales inválidas"), 401


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
