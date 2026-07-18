# PostPilot AI 🚀

An automated LinkedIn posting backend with AI-generated content. Built with a production-style architecture to demonstrate real-world backend engineering patterns.

## What it does

- Register and authenticate users with JWT
- Create and manage LinkedIn posts
- Schedule posts for automatic publishing at a specified time
- Background workers handle publishing without blocking the API
- AI-generated post content via LangChain + Gemini *(coming soon)*
- Full LinkedIn OAuth integration *(coming soon)*

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
│   ├── services/             # Business logic layer
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
                    ├── LinkedIn API (post publishing)
                    └── Gemini API (AI content)
```

Celery Beat runs as a separate process and checks every minute for posts due for publishing, enqueuing them automatically.

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (or Memurai on Windows)

### Setup

**1. Clone the repo**
```bash
git clone https://github.com/your-username/postpilot-ai.git
cd postpilot-ai
```

**2. Create and activate virtual environment**
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
```

Fill in your `.env` file:
```env
SECRET_KEY=your-generated-secret-key
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/postpilot
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

Generate a secure secret key:
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

You need three terminal windows running simultaneously:

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
| POST | `/api/v1/auth/login` | Login and get JWT token | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### Posts
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/posts` | Create a new post | Yes |
| GET | `/api/v1/posts` | List all your posts | Yes |
| GET | `/api/v1/posts/{id}` | Get a single post | Yes |
| PATCH | `/api/v1/posts/{id}` | Update a post | Yes |
| DELETE | `/api/v1/posts/{id}` | Delete a post | Yes |
| POST | `/api/v1/posts/{id}/schedule` | Schedule a post | Yes |
| POST | `/api/v1/posts/{id}/publish` | Publish immediately | Yes |

## How Scheduling Works

1. Create a post via `POST /api/v1/posts`
2. Schedule it via `POST /api/v1/posts/{id}/schedule` with a future datetime
3. Celery Beat checks every minute for due posts
4. When due, it enqueues a `publish_post_task`
5. The Celery worker executes the task and updates the post status to `published`

## Database Schema

- **users** — registered users with LinkedIn OAuth tokens
- **posts** — content with status (draft → scheduled → published/failed)
- **schedules** — one-to-one with posts, stores `scheduled_at` and `is_processed`
- **post_logs** — audit trail of every publishing event

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | JWT signing key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `CELERY_BROKER_URL` | Celery broker (Redis) | Yes |
| `CELERY_RESULT_BACKEND` | Celery results (Redis) | Yes |
| `LINKEDIN_CLIENT_ID` | LinkedIn OAuth client ID | Yes |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn OAuth client secret | Yes |
| `LINKEDIN_REDIRECT_URI` | LinkedIn OAuth callback URL | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `DEBUG` | Enable debug mode | No (default: False) |

## Roadmap

- [x] User authentication (JWT)
- [x] Post CRUD
- [x] Scheduled publishing (Celery Beat)
- [ ] AI content generation (LangChain + Gemini)
- [ ] LinkedIn OAuth integration
- [ ] Post analytics and logging
- [ ] Docker containerization
- [ ] Test suite

## License

MIT