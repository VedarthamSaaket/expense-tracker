from flask import Blueprint, jsonify, request

from app.db import get_db
from app.validation import CATEGORIES, validate_expense

bp = Blueprint("api", __name__)


def row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "amount": row["amount"],
        "category": row["category"],
        "spent_on": row["spent_on"],
        "created_at": row["created_at"],
    }


def find_expense(expense_id):
    return get_db().execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()


def not_found():
    return jsonify(error="expense not found"), 404


@bp.get("/health")
def health():
    return jsonify(status="ok")


@bp.get("/categories")
def categories():
    return jsonify(sorted(CATEGORIES))


@bp.get("/expenses")
def list_expenses():
    query = "SELECT * FROM expenses WHERE 1 = 1"
    params = []
    category = request.args.get("category")
    if category:
        query += " AND category = ?"
        params.append(category)
    month = request.args.get("month")
    if month:
        query += " AND substr(spent_on, 1, 7) = ?"
        params.append(month)
    query += " ORDER BY spent_on DESC, id DESC"
    rows = get_db().execute(query, params).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@bp.post("/expenses")
def create_expense():
    clean, errors = validate_expense(request.get_json(silent=True))
    if errors:
        return jsonify(errors=errors), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO expenses (title, amount, category, spent_on) VALUES (?, ?, ?, ?)",
        (clean["title"], clean["amount"], clean["category"], clean["spent_on"]),
    )
    db.commit()
    return jsonify(row_to_dict(find_expense(cur.lastrowid))), 201


@bp.get("/expenses/<int:expense_id>")
def get_expense(expense_id):
    row = find_expense(expense_id)
    if row is None:
        return not_found()
    return jsonify(row_to_dict(row))


@bp.put("/expenses/<int:expense_id>")
def update_expense(expense_id):
    if find_expense(expense_id) is None:
        return not_found()
    clean, errors = validate_expense(request.get_json(silent=True), partial=True)
    if errors:
        return jsonify(errors=errors), 400
    sets = ", ".join(f"{field} = ?" for field in clean)
    db = get_db()
    db.execute(f"UPDATE expenses SET {sets} WHERE id = ?", (*clean.values(), expense_id))
    db.commit()
    return jsonify(row_to_dict(find_expense(expense_id)))


@bp.delete("/expenses/<int:expense_id>")
def delete_expense(expense_id):
    if find_expense(expense_id) is None:
        return not_found()
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    return "", 204


@bp.get("/summary")
def summary():
    month = request.args.get("month")
    where = ""
    params = []
    if month:
        where = "WHERE substr(spent_on, 1, 7) = ?"
        params.append(month)
    rows = get_db().execute(
        "SELECT category, ROUND(SUM(amount), 2) AS total, COUNT(*) AS count "
        f"FROM expenses {where} GROUP BY category ORDER BY total DESC",
        params,
    ).fetchall()
    by_category = {r["category"]: {"total": r["total"], "count": r["count"]} for r in rows}
    total = round(sum(v["total"] for v in by_category.values()), 2)
    count = sum(v["count"] for v in by_category.values())
    return jsonify(month=month, total=total, count=count, by_category=by_category)
