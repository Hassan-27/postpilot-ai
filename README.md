# PostPilot AI 🚀

PostPilot AI is an automated content publishing backend built with FastAPI. It lets authenticated users create posts, generate content with Gemini, schedule posts, and publish them to Discord through a webhook.

> **Publishing note:** PostPilot currently publishes to Discord. LinkedIn post publishing is not enabled because LinkedIn's posting API is not generally available to regular personal accounts. LinkedIn-related fields remain in parts of the codebase for future OAuth work, but the active publishing flow does not call LinkedIn.

## What it does

- Register and authenticate users with JWT
- Create, update, list, and delete posts
- Generate post content with LangChain and Gemini
- Schedule posts for automatic publishing at a specified time
- Publish immediately or through scheduled background jobs
- Deliver published content to Discord using a Discord webhook
- Record successful and failed publishing events in post logs

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy (async) |
| Migrations | Alembic |
| Auth | JWT + bcrypt |
| Task Queue | Celery + Redis |
| Scheduler | Celery Beat |
| AI | LangChain + Gemini API |
| Publishing | Discord Webhooks |
| Config | pydantic-settings |
| Server | Uvicorn |

## Project Structure

```
postpilot-ai/
├── app/
│   ├── api/v1/routes/        # HTTP endpoints (auth, posts)
│   ├── core/                 # Config, logging, security
│   ├── db/                   # Database session, dependencies, model registry
│   ├── models/               # SQLAlchemy models (User, Post, Schedule, PostLog)
│   ├── schemas/              # Pydantic schemas for request/response
│   ├── services/             # Business logic and Discord publishing
│   └── workers/              # Celery tasks and Beat scheduler
├── alembic/                  # Database migrations
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
├── .env.example              # Environment variable template
├── requirements.txt
└── README.md
```

## Architecture

```
Client
  └── FastAPI (API layer)
        ├── PostgreSQL (data persistence)
        └── Redis (message broker)
              └── Celery Worker (background publishing)
                    ├── Discord Webhook (post delivery)
                    └── Gemini API (AI content generation)
```

Celery Beat checks every minute for posts due for publishing and enqueues them. The Celery worker sends the post content to the configured Discord webhook and records the result as `published` or `failed`.

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (or Memurai on Windows)
- A Discord server and channel with a configured webhook

### Setup

**1. Clone the repo**

```bash
git clone https://github.com/Hassan-27/postpilot-ai.git
cd postpilot-ai
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\\Scripts\\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create your environment file**

```bash
cp .env.example .env
```

At minimum, configure the database, Redis, application secret, Gemini API key, and Discord webhook URL:

```env
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/postpilot
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
GEMINI_API_KEY=your_gemini_api_key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
```

The `DISCORD_WEBHOOK_URL` value is the webhook URL copied from **Discord → Server Settings → Integrations → Webhooks**. Keep it private and do not commit it.

The current settings module still declares the legacy LinkedIn variables. They are retained for compatibility with the unfinished LinkedIn OAuth work; they are not used to publish posts. LinkedIn publishing is not part of the current application flow.

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**5. Create the database**

In PgAdmin or psql:

```sql
CREATE DATABASE postpilot;
```

**6. Run migrations**

```bash
alembic upgrade head
```

### Running the App

Run these processes in separate terminal windows:

**Terminal 1 — FastAPI server**

```bash
uvicorn app.main:app --reload
```

**Terminal 2 — Celery worker**

```bash
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 — Celery Beat scheduler**

```bash
celery -A app.workers.celery_app beat --loglevel=info
```

API available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

## API Endpoints

### Auth

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and get a JWT token | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### Posts

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/posts` | Create a new post | Yes |
| GET | `/api/v1/posts` | List your posts | Yes |
| GET | `/api/v1/posts/{id}` | Get a single post | Yes |
| PATCH | `/api/v1/posts/{id}` | Update a post | Yes |
| DELETE | `/api/v1/posts/{id}` | Delete a post | Yes |
| POST | `/api/v1/posts/{id}/schedule` | Schedule a post | Yes |
| POST | `/api/v1/posts/{id}/publish` | Queue immediate Discord publishing | Yes |
| POST | `/api/v1/posts/generate` | Generate AI-assisted content | Yes |

## How Publishing Works

1. Create a post with `POST /api/v1/posts`.
2. Publish immediately with `POST /api/v1/posts/{id}/publish`, or schedule it with `POST /api/v1/posts/{id}/schedule`.
3. Celery Beat checks every minute for due schedules.
4. A Celery worker calls the Discord webhook with the post content.
5. A successful webhook response marks the post `published`; failures mark it `failed` and create a corresponding post log.

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | JWT signing key | Yes |
| `DATABASE_URL` | PostgreSQL async connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `CELERY_BROKER_URL` | Celery message broker | Yes |
| `CELERY_RESULT_BACKEND` | Celery result backend | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `DISCORD_WEBHOOK_URL` | Discord webhook used for publishing | Yes |
| `DEBUG` | Enable debug mode | No (default: `False`) |
| `LINKEDIN_CLIENT_ID` | Legacy LinkedIn OAuth setting; not used for publishing | Legacy |
| `LINKEDIN_CLIENT_SECRET` | Legacy LinkedIn OAuth setting; not used for publishing | Legacy |
| `LINKEDIN_REDIRECT_URI` | Legacy LinkedIn OAuth callback setting | Legacy |

## Roadmap

- [x] User authentication (JWT)
- [x] Post CRUD
- [x] Scheduled publishing with Celery Beat
- [x] Discord webhook publishing
- [x] AI content generation with Gemini
- [ ] LinkedIn OAuth integration, subject to API access
- [ ] Post analytics and logging improvements
- [ ] Docker containerization
- [ ] Expanded test suite

## License

MIT
