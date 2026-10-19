from datetime import date

CATEGORIES = {"food", "transport", "bills", "shopping", "health", "fun", "other"}


def validate_expense(data, partial=False):
    if not isinstance(data, dict):
        return None, ["body must be a json object"]

    errors = []
    clean = {}

    if "title" in data:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            errors.append("title must be a non empty string")
        else:
            clean["title"] = title.strip()
    elif not partial:
        errors.append("title is required")

    if "amount" in data:
        amount = data["amount"]
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            errors.append("amount must be a number")
        elif amount <= 0:
            errors.append("amount must be greater than 0")
        else:
            clean["amount"] = round(float(amount), 2)
    elif not partial:
        errors.append("amount is required")

    if "category" in data:
        category = data["category"]
        if category not in CATEGORIES:
            errors.append("category must be one of " + ", ".join(sorted(CATEGORIES)))
        else:
            clean["category"] = category
    elif not partial:
        clean["category"] = "other"

    if "spent_on" in data:
        try:
            clean["spent_on"] = date.fromisoformat(data["spent_on"]).isoformat()
        except (TypeError, ValueError):
            errors.append("spent_on must be a date like 2026-10-19")
    elif not partial:
        clean["spent_on"] = date.today().isoformat()

    if partial and not clean and not errors:
        errors.append("nothing to update")

    return clean, errors
