# CrimsonRep - Gym Tracker API

![Build Status](https://img.shields.io/badge/build-passing-brightgreen) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

A modern FastAPI-powered workout tracking application that logs exercises, tracks sets, and calculates personal records.

## Overview

CrimsonRep is built for fitness enthusiasts who want to track their workout progress with precision through a clean REST API. It leverages modern Python technologies to provide a secure, performant, and testable backend.

## Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                        Client Layer                           │
├───────────────────────────────────────────────────────────────┤
│  Swagger UI / ReDoc  │  HTMX Frontend (planned)  │  API Clients │
├───────────────────────────────────────────────────────────────┤
│                      Application Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │   Auth Router   │  │  Sessions Router│  │ Exercises     │  │
│  │ (signup, login) │  │ (CRUD Sessions) │  │ Router        │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
├───────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │   Pydantic      │  │   SQLAlchemy    │  │   Utils       │  │
│  │   Models        │  │   ORM/Services  │  │   (1RM calc)  │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
├───────────────────────────────────────────────────────────────┤
│                      Data Layer                               │
│  PostgreSQL (via SQLAlchemy)                                  │
│  Tables: users, exercises, workout_sessions, sets             │
└───────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Why |
|-------|------------|-----|
| API | FastAPI | Automatic OpenAPI docs, async, Pydantic integration |
| Database | PostgreSQL | Reliable, JSON support, widely used in production |
| ORM | SQLAlchemy 2.0 | Modern ORM with type annotations |
| Migrations | Alembic | Version-controlled database schema |
| Auth | JWT + bcrypt | Secure, stateless authentication |
| Testing | pytest | Industry standard Python test framework |
| Container | Docker | Consistent development/production environments |

## API Design Decisions

### "Best vs Last" Exercise Feature

This is the interview-worthy feature. Here's how we define progress:

- **Last:** The most recent workout session containing that exercise.
- **Best:** Highest Estimated 1RM (Epley formula: `weight × (1 + reps/30)`) from that session.

**Edge Cases Handled:**
- First-ever session returns `best = last`
- Bodyweight exercises (weight = 0) use reps only
- Ties are resolved by session proximity (most recent wins)

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- PostgreSQL
- Docker & Docker Compose

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/crimson_rep.git
cd crimson_rep
python3 -m venv gym
source gym/bin/activate  # On Windows: gym\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install fastapi uvicorn[standard] pydantic
```

### 3. Run Development Server

```bash
python3 -m CrimsonRep.app.main
```

Visit: http://localhost:8000/docs

### 4. Run with Docker

```bash
docker-compose up --build
```

## Project Structure

```
crimson_rep/
├── CrimsonRep/           # Main Python package
│   ├── app/              # FastAPI application
│   │   ├── api/          # Route handlers
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── main.py       # App entry point
│   ├── tests/            # Unit & integration tests
│   └── core/             # Config, security, database
├── alembic/              # Database migrations
├── docker/               # Docker configuration
├── requirements.txt
├── pyproject.toml        # Modern Python project config
└── README.md
```

## Development Lifecycle

| Phase | Goal | Deliverables |
|-------|------|--------------|
| Day 1 | Setup | Repo, venv, FastAPI skeleton |
| Day 2 | Database | PostgreSQL, SQLAlchemy models, migrations |
| Day 3 | Auth | Signup/Login endpoints, JWT tokens |
| Day 4 | Core API | Sessions, Exercises, Sets endpoints |
| Day 5 | Tests | 70%+ coverage, auth tests |
| Day 6 | Deploy | Docker image, cloud deployment |

## Environment Configuration

Create a `.env` file at the project root:

```bash
# Database
DATABASE_URL=postgresql+psycopg2://user:password@localhost/gym_tracker

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=CrimsonRep --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## Docker Usage

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Create new user account |
| POST | `/auth/login` | Get JWT access token |
| POST | `/sessions` | Log a new workout session |
| GET | `/sessions` | Get paginated list of sessions |
| GET | `/exercises/{id}/progress` | Get best vs last metric |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Design Philosophy

**Test-Driven:** Every core feature has comprehensive tests covering edge cases.

**Auth by Default:** Every user can only access their own data. Authorization is verified in tests.

**Error Handling:** Proper HTTP status codes and validation errors returned to clients.

**No Secrets:** All sensitive data lives in `.env` (which is gitignored).