# Expense Manager API

A full-stack expense tracking application with a REST API backend and a lightweight web frontend. Users can register, log in, and manage their own expenses, which are automatically sorted into categories. Spending is visualized as a donut chart broken down by category.

**Live demo:** https://expense-manager-7cnf.onrender.com/ &nbsp;·&nbsp; **API docs:** https://expense-manager-7cnf.onrender.com/docs

> ⚠️ Hosted on a free tier, so the first request after a period of inactivity may take ~30–60 seconds to wake the server.

---

## What it does

- **User accounts** — register with email, phone, and password; log in to receive a token
- **Personal expenses** — every expense belongs to the user who created it; nobody can see or touch anyone else's data
- **Automatic categorization** — expenses are sorted into categories (groceries, entertainment, gas, housing, dining, utilities, other) based on their description
- **Filtering & pagination** — list expenses by category or date range, in pages
- **Spending summary** — totals per category, shown both as a list and as a donut chart
- **Interactive API docs** — auto-generated Swagger UI at `/docs`

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| Data validation | Pydantic |
| Database (local) | SQLite |
| Database (production) | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Authentication | JWT (PyJWT) + bcrypt password hashing |
| Testing | pytest |
| Frontend | HTML, CSS, vanilla JavaScript, Chart.js |
| Deployment | Docker on Render |

---

## Architecture

The backend is organized into layers, each with a single responsibility, so that HTTP handling, business logic, and database access stay separate and testable:

```
app/
├── main.py            # Routes — HTTP in, HTTP out; thin, delegates to crud
├── database.py        # DB engine + session factory (URL from env var)
├── dependencies.py    # Shared FastAPI dependencies (get_db)
├── models/            # SQLAlchemy models — what the database tables look like
├── schemas/           # Pydantic models — what the API accepts and returns
├── crud/              # The only place that actually queries the database
├── services/          # Business logic (e.g. keyword-based categorization)
└── auth/              # Password hashing + JWT creation/verification
alembic/               # Database migration history
tests/                 # pytest suite
static/                # Frontend (HTML/CSS/JS)
```

**Why this structure:** keeping database queries isolated in `crud/` and validation shapes in `schemas/` meant that big changes — like adding per-user data scoping, or switching the production database from SQLite to PostgreSQL — touched only one or two files instead of rippling through the whole codebase.

---

## Key design decisions

- **Separate input/output schemas.** A `UserCreate` schema accepts a password; the `User` response schema doesn't even have a password field — so a password can never accidentally leak into an API response.
- **Per-user data isolation enforced at the query level.** Expense lookups filter by both the expense ID *and* the owner's ID in a single query, so a request for someone else's expense returns a plain `404` — it never reveals that the record exists.
- **SQLAlchemy + Alembic instead of raw SQL.** Using an ORM with versioned migrations meant the same code runs on SQLite locally and PostgreSQL in production with only a connection-string change, and every schema change is tracked in version control.
- **Secrets and config via environment variables.** The JWT secret key and database URL are never hardcoded or committed — they're read from the environment, with a safe SQLite default for local development.
- **Stateless JWT authentication.** The server holds no session state; each request carries a signed token that's verified fresh, which is what lets the API scale and stay simple.

---

## Running it locally

```bash
# 1. Clone and enter the project
git clone https://github.com/your-username/expense-manager.git
cd expense-manager

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file with a secret key
#    Generate one with: python -c "import secrets; print(secrets.token_hex(32))"
echo "SECRET_KEY=your-generated-secret" > .env

# 5. Set up the database
alembic upgrade head

# 6. Run the server
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/` for the app, or `http://127.0.0.1:8000/docs` for the interactive API.

Locally the app defaults to SQLite — no database server needed. In production, setting a `DATABASE_URL` environment variable points it at PostgreSQL instead.

---

## Running the tests

```bash
pytest tests/ -v
```

The suite covers registration and its validation rules (email format, phone format, password length), login (correct and incorrect credentials), and — most importantly — that one user cannot read or delete another user's expenses.

---

## What I learned

I came into this with some coding background but had never built an API before — I genuinely didn't know what REST meant when I started. Building this from scratch taught me:

- **How the web actually fits together** — HTTP methods and status codes, the request/response cycle, why REST APIs are stateless, and how a frontend, a backend, and a database talk to each other.
- **Real backend fundamentals** — data validation, an ORM and database migrations, password hashing, and JWT-based authentication (and *why* each of those matters, not just how to wire them up).
- **That the debugging is the real learning.** The tutorials make it look smooth; the reality wasn't. I worked through a broken Alembic migration chain, a foreign-key typo that silently crashed every write, a `passlib`/`bcrypt` version conflict, environment and interpreter mismatches, and a full production deployment with its own surprises. Pushing through those — reading tracebacks, isolating the actual cause, fixing it — is the part I'm most proud of, because it's the part that doesn't come from following steps.
- **How to ship something real.** Taking a project from "runs on my laptop" to a live URL on managed PostgreSQL — Dockerizing it, handling secrets properly, and understanding the tradeoffs (like why SQLite doesn't survive on an ephemeral free tier) — was a whole skill of its own.

---

## Possible next steps

- Rebuild the frontend in React as a separate learning project (the API wouldn't need to change)
- Add editing of existing expenses
- Add monthly spending trends over time
- Add budget limits per category with warnings
