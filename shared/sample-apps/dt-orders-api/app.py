"""dt-orders-api — a deliberately small sample service for the
Defending Tomorrow DevSecOps labs.

This is the SECURE baseline. Individual labs copy it and introduce a
single, clearly labelled weakness so that one security control can be
observed in isolation. Never deploy lab variants outside a sandbox.
"""
import os
import sqlite3

import yaml
from flask import Flask, g, jsonify, request

app = Flask(__name__)
DB_PATH = os.environ.get("ORDERS_DB", "orders.db")
CONFIG_PATH = os.environ.get("ORDERS_CONFIG", "config.yaml")


def load_config(path: str = CONFIG_PATH) -> dict:
    """Load service configuration. safe_load prevents arbitrary object construction."""
    if not os.path.exists(path):
        return {"service_name": "dt-orders-api", "max_results": 50}
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = sqlite3.connect(DB_PATH)
    db.execute(
        "CREATE TABLE IF NOT EXISTS orders ("
        "id INTEGER PRIMARY KEY, customer TEXT NOT NULL, item TEXT NOT NULL, qty INTEGER NOT NULL)"
    )
    if db.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0:
        # Synthetic records only — no real customer data is ever used in the labs.
        db.executemany(
            "INSERT INTO orders (customer, item, qty) VALUES (?, ?, ?)",
            [("alice", "widget", 2), ("bob", "gadget", 1), ("carol", "sprocket", 5)],
        )
    db.commit()
    db.close()


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/orders")
def list_orders():
    customer = request.args.get("customer", "")
    limit = int(load_config().get("max_results", 50))
    # Parameterised query: user input is bound, never concatenated into SQL.
    rows = get_db().execute(
        "SELECT id, customer, item, qty FROM orders WHERE customer = ? LIMIT ?",
        (customer, limit),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return response


init_db()

if __name__ == "__main__":
    # Development server only. Containers use gunicorn (see Dockerfile).
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8080")))
