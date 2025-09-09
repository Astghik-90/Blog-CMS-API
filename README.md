# Flask REST API

A Flask REST API application with JWT authentication and PostgreSQL database, containerized with Docker.

## Tech Stack

- **Backend**: Flask, Flask-Smorest, Flask-JWT-Extended
- **Database**: PostgreSQL 
- **Authentication**: JWT tokens with role-based access
- **Migration**: Flask-Migrate (Alembic)
- **Containerization**: Docker & Docker Compose
- **Documentation**: Swagger UI (OpenAPI 3.0)

## Features

- JWT Authentication with role-based access (Admin/Author)
- PostgreSQL database with UUID primary keys
- Database migrations with Flask-Migrate
- Swagger UI documentation at `/swagger-ui`
- Docker containerization for easy deployment

## Installation

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "python api"
   ```

2. **Create environment file** (`.env`)
   ```bash
   DATABASE_URL=postgresql://postgres:password@db:5432/myapp
   JWT_SECRET_KEY=your-super-secret-key-change-in-production
   MAILGUN_API_KEY=
   MAILGUN_DOMAIN=
   REDIS_URL=redis://redis:6379/0
   ```

## Quick Start

After completing the [Installation](#installation) steps above:

### 1. Run with Docker

```bash
# Activate virtual environment
source venv/bin/activate

# Build and start
docker compose up --build

# Or run in background
docker compose up --build -d
```

### 2. Access

- **API**: http://localhost:5000
- **Swagger UI**: http://localhost:5000/swagger-ui

## Development

For detailed development instructions, database migrations, and troubleshooting, see [CONTRIBUTING.md](CONTRIBUTING.md).

## API Usage

### Register User
```bash
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@example.com", "password": "password"}'
```

### Login
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

### Use Token
```bash
curl -X POST http://localhost:5000/category \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Technology"}'
```

### Basic Commands
```bash
# View logs
docker compose logs -f web

# Stop application
docker compose down

# Reset database
docker compose down -v && docker compose up --build
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Secret key for JWT tokens |
| `MAILGUN_API_KEY`| API key for Mailgun email service |
| `MAILGUN_DOMAIN`| Domain name configured in Mailgun for sending emails |
| `REDIS_URL`| Redis connection string for caching and background tasks | 