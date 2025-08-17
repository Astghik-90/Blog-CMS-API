# Contributing to Flask REST API

## Development Setup

Ensure you have completed the [installation steps](README#installation) before proceeding.

## Model Changes & Migrations

When you modify database models, follow these steps:

### Step-by-Step Process

1. **Make your model changes** (edit files in `models/` directory)

2. **Ensure containers are running**
   ```bash
   docker compose up -d
   ```

3. **Access the container**
   ```bash
   docker compose exec web bash
   ```

4. **Generate migration**
   ```bash
   flask db migrate -m "Describe your changes"
   ```

5. **Review the migration** (check `migrations/versions/` folder)

6. **Apply the migration**
   ```bash
   flask db upgrade
   ```

7. **Exit container**
   ```bash
   exit
   ```

8. **Restart application** (if needed)
   ```bash
   docker compose restart web
   ```

### Example
```bash
# After editing models/user.py
docker compose up -d                              # Ensure containers are running
docker compose exec web bash                      # Access container
flask db migrate -m "Add phone number to user"    # Create migration
flask db upgrade                                   # Apply migration
exit                                              # Exit container
docker compose restart web                        # Restart if needed
```

## Development Commands

### View Logs
```bash
# View all logs
docker compose logs

# View web service logs
docker compose logs -f web

# View database logs
docker compose logs db
```

### Container Management
```bash
# Stop containers
docker compose down

# Stop and remove volumes (deletes database data)
docker compose down -v

# Rebuild containers
docker compose up --build

# Restart specific service
docker compose restart web
```

### Database Operations
**Note:** Ensure containers are running first: `docker compose up -d`

```bash
# Access database directly
docker compose exec db psql -U postgres -d myapp

# Check migration status
docker compose exec web flask db current

# View migration history
docker compose exec web flask db history

# Downgrade migration
docker compose exec web flask db downgrade
```

### Reset Environment
```bash
# Complete reset (removes all data)
docker compose down -v
docker compose up --build
```

## Code Changes

### Making Changes
1. Edit your code files
2. If models changed, follow [migration steps](#model-changes--migrations)
3. Restart containers if needed: `docker compose restart web`

### Testing Changes
1. Test via Swagger UI: http://localhost:5000/swagger-ui
2. Use curl commands for API testing
3. Check logs for errors: `docker compose logs -f web`
