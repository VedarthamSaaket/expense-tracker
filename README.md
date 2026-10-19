# Expense Tracker

A small personal expense tracker api built with flask and sqlite.
I made it to practice api testing, ci pipelines and a normal git workflow with github actions.

## What it does

You can add, list, update and delete expenses.
Each expense has a title, amount, category and the date it was spent on.
You can filter expenses by category or by month.
There is a summary endpoint that gives the total spent per category.

## Endpoints

GET /health checks the api is up.
GET /categories lists the allowed categories.
GET /expenses lists expenses, optional ?category=food and ?month=2026-10.
POST /expenses creates an expense.
GET /expenses/<id> gets one expense.
PUT /expenses/<id> updates any of the fields.
DELETE /expenses/<id> deletes an expense.
GET /summary gives totals by category, optional ?month=2026-10.

Example body for POST:

```
{"title": "Groceries", "amount": 1250.5, "category": "food", "spent_on": "2026-10-15"}
```

Category defaults to other and spent_on defaults to today if you leave them out.

## Running locally

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python run.py
```

The api runs on http://localhost:5000 and the database is saved to expenses.db.
Set DATABASE_PATH or PORT if you want something different.

## Tests

Unit tests use pytest with a temp sqlite file for each test.

```
pytest -v
flake8
```

API tests are in the postman folder.
You can import the collection and environment into postman and run them with the server running.
Or run them from the terminal with newman:

```
npx newman run postman/expense-tracker.postman_collection.json -e postman/local.postman_environment.json
```

The collection creates an expense, saves its id, then gets, updates, summarises and deletes it, with assertions on every request.

## CI and deployment

The workflow is in .github/workflows/ci.yml and runs on every push and pull request to main.
The test job runs flake8 and pytest on python 3.11 and 3.12.
The api-test job starts the api with gunicorn and runs the postman collection with newman, the junit report is uploaded as an artifact.
The deploy job only runs on pushes to main after both test jobs pass.
It builds the docker image, pushes it to github container registry and smoke tests it.
If a RENDER_DEPLOY_HOOK secret is set in the repo it also triggers a deploy on render.

## Files

app/__init__.py creates the flask app.
app/db.py handles the sqlite connection and the table.
app/routes.py has all the endpoints.
app/validation.py checks the request bodies.
run.py starts the app.
tests/ has the pytest tests.
postman/ has the collection and local environment.
Dockerfile builds the production image with gunicorn.
