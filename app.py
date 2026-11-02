import os
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, g, redirect, render_template, request, url_for

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
# DATABASE_URL(Supabase Postgres 연결 문자열)이 있으면 Supabase에, 없으면 로컬 SQLite에 저장
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_PG = bool(DATABASE_URL)
DB_PATH = BASE_DIR / "todos.db"

app = Flask(__name__)

PRIORITIES = {"high": "높음", "medium": "보통", "low": "낮음"}

SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    due_date TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
)
"""

SCHEMA_PG = """
CREATE TABLE IF NOT EXISTS todos (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium',
    due_date TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


def connect():
    if USE_PG:
        import psycopg
        from psycopg.rows import dict_row

        # Supabase 풀러(6543, transaction mode)는 prepared statement를 지원하지 않음
        return psycopg.connect(DATABASE_URL, row_factory=dict_row, prepare_threshold=None)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if "db" not in g:
        g.db = connect()
    return g.db


def query(sql, params=()):
    """SQLite 스타일(?) 쿼리를 실행. Postgres일 때는 %s로 바꿔서 실행."""
    if USE_PG:
        sql = sql.replace("?", "%s")
    return get_db().execute(sql, params)


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with connect() as db:
        db.execute(SCHEMA_PG if USE_PG else SCHEMA_SQLITE)


@app.route("/")
def index():
    status = request.args.get("status", "all")
    q = request.args.get("q", "").strip()

    sql = "SELECT * FROM todos WHERE 1=1"
    params = []
    if status == "active":
        sql += " AND done = 0"
    elif status == "done":
        sql += " AND done = 1"
    if q:
        sql += " AND title ILIKE ?" if USE_PG else " AND title LIKE ?"
        params.append(f"%{q}%")
    sql += """
        ORDER BY done,
                 CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                 due_date IS NULL, due_date, id DESC
    """
    todos = query(sql, params).fetchall()

    counts = query(
        "SELECT COUNT(*) AS total, COALESCE(SUM(done), 0) AS done FROM todos"
    ).fetchone()

    return render_template(
        "index.html",
        todos=todos,
        status=status,
        q=q,
        total=counts["total"],
        done_count=counts["done"],
        priorities=PRIORITIES,
        today=date.today().isoformat(),
    )


@app.post("/add")
def add():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    due_date = request.form.get("due_date") or None
    if title:
        if priority not in PRIORITIES:
            priority = "medium"
        query(
            "INSERT INTO todos (title, priority, due_date) VALUES (?, ?, ?)",
            (title, priority, due_date),
        )
        get_db().commit()
    return redirect(url_for("index"))


@app.post("/toggle/<int:todo_id>")
def toggle(todo_id):
    query("UPDATE todos SET done = 1 - done WHERE id = ?", (todo_id,))
    get_db().commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    todo = query("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if todo is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        priority = request.form.get("priority", "medium")
        due_date = request.form.get("due_date") or None
        if title:
            if priority not in PRIORITIES:
                priority = "medium"
            query(
                "UPDATE todos SET title = ?, priority = ?, due_date = ? WHERE id = ?",
                (title, priority, due_date, todo_id),
            )
            get_db().commit()
        return redirect(url_for("index"))

    return render_template("edit.html", todo=todo, priorities=PRIORITIES)


@app.post("/delete/<int:todo_id>")
def delete(todo_id):
    query("DELETE FROM todos WHERE id = ?", (todo_id,))
    get_db().commit()
    return redirect(request.referrer or url_for("index"))


@app.post("/clear-done")
def clear_done():
    query("DELETE FROM todos WHERE done = 1")
    get_db().commit()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
