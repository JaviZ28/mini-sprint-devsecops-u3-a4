from contextlib import closing
import os
import secrets
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import check_password_hash
import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.values = {name: secrets.token_hex(16) for name in ("API_KEY", "ADMIN_PASSWORD", "STUDENT_PASSWORD")}
        self.addCleanup(patch.stopall)
        patch.dict(os.environ, self.values).start()
        patch.object(app, "DB_PATH", Path(folder.name) / "test.db").start()
        app.init_db()
        self.client = app.app.test_client()

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)

    def test_profile(self):
        self.assertEqual(self.client.get("/api/profile").status_code, 401)
        self.assertEqual(self.client.get("/api/profile", headers={"X-API-Key": self.values["API_KEY"]}).status_code, 200)

    def test_login_valido(self):
        for name, key in (("admin", "ADMIN_PASSWORD"), ("estudiante", "STUDENT_PASSWORD")):
            self.assertEqual(self.client.post("/api/login", json={"username": name, "password": self.values[key]}).status_code, 200)

    def test_login_invalido_e_inyeccion(self):
        for body in ({"username": "admin", "password": ""}, {"username": "' OR 1=1 --", "password": "x"}):
            self.assertEqual(self.client.post("/api/login", json=body).status_code, 401)
        self.assertEqual(self.client.post("/api/login", json=[]).status_code, 400)

    def test_password_guardado_como_hash(self):
        with closing(sqlite3.connect(app.DB_PATH)) as db:
            stored = db.execute("SELECT password_hash FROM users WHERE username = ?", ("admin",)).fetchone()[0]
        self.assertNotEqual(stored, self.values["ADMIN_PASSWORD"])
        self.assertTrue(check_password_hash(stored, self.values["ADMIN_PASSWORD"]))

