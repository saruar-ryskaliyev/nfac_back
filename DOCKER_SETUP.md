# Docker PostgreSQL Setup Guide

This guide provides step-by-step instructions to run the PostgreSQL database with Docker for this FastAPI project.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Database Credentials

### PostgreSQL Database Configuration
- **Host**: `localhost` (or `postgresql` when connecting from within Docker network)
- **Port**: `5432`
- **Database**: `postgres`
- **Username**: `postgres`
- **Password**: `postgres`
- **Container Name**: `postgresql`

### Connection URLs
- **Local connection**: `postgresql://postgres:postgres@localhost:5432/postgres`
- **Docker network connection**: `postgresql://postgres:postgres@postgresql:5432/postgres`

## Step-by-Step Setup Instructions

### 1. Navigate to Project Directory
```bash
cd /path/to/fastapi-postgresql-boilerplate
```

### 2. Ensure Environment Files Exist
Make sure these files exist in your project root:
- `.env` (application environment variables)
- `.db.env` (database environment variables)

If they don't exist, copy from examples:
```bash
cp .env.example .env
cp .db.env.example .db.env
```

### 3. Start PostgreSQL Container
```bash
# Start only PostgreSQL service
docker-compose up -d postgresql

# Or start all services (app + database)
docker-compose up -d
```

### 4. Verify PostgreSQL is Running
```bash
# Check container status
docker-compose ps

# Check PostgreSQL logs
docker-compose logs postgresql

# Test database connection
docker exec postgresql psql -U postgres -d postgres -c "SELECT version();"
```

## Common Commands

### Starting Services
```bash
# Start PostgreSQL only
docker-compose up -d postgresql

# Start all services
docker-compose up -d

# Start with logs visible
docker-compose up postgresql
```

### Stopping Services
```bash
# Stop PostgreSQL
docker-compose stop postgresql

# Stop all services
docker-compose stop

# Stop and remove containers
docker-compose down
```

### Database Management
```bash
# Connect to PostgreSQL shell
docker exec -it postgresql psql -U postgres -d postgres

# Run SQL commands from host
docker exec postgresql psql -U postgres -d postgres -c "YOUR_SQL_COMMAND;"

# Create a new database
docker exec postgresql psql -U postgres -c "CREATE DATABASE your_new_db;"

# List all databases
docker exec postgresql psql -U postgres -c "\l"
```

### Backup and Restore
```bash
# Create backup
docker exec postgresql pg_dump -U postgres postgres > backup.sql

# Restore backup
docker exec -i postgresql psql -U postgres postgres < backup.sql
```

## Data Persistence

Database data is stored in a Docker volume named `postgresql_data`. This ensures your data persists even if you recreate the container.

### Volume Management
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect fastapi-postgresql-boilerplate_postgresql_data

# Remove volume (WARNING: This will delete all data!)
docker volume rm fastapi-postgresql-boilerplate_postgresql_data
```

## Application Connection

When connecting from your FastAPI application:

### From Host Machine (Development)
```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
```

### From Docker Container (Production)
```python
DATABASE_URL = "postgresql://postgres:postgres@postgresql:5432/postgres"
```

## Troubleshooting

### Port Already in Use
If port 5432 is already in use:
1. Check what's using the port: `lsof -i :5432`
2. Stop the conflicting service or change the port in `docker-compose.yml`

### Container Won't Start
1. Check logs: `docker-compose logs postgresql`
2. Ensure `.db.env` file exists with correct variables
3. Try removing and recreating: `docker-compose down && docker-compose up -d postgresql`

### Permission Issues
If you encounter permission issues:
```bash
# Fix ownership (Linux/Mac)
sudo chown -R $USER:$USER .

# Or run with sudo (not recommended)
sudo docker-compose up -d postgresql
```

### Database Connection Refused
1. Ensure container is running: `docker-compose ps`
2. Check if port is accessible: `telnet localhost 5432`
3. Verify firewall settings

## Environment Variables Reference

### .db.env file contents:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_PORT=5432
DEFAULT_DATABASE=postgres
LISTEN_ADDRESSES=*
```

### .env file (application):
```env
APP_ENV=dev
```

## Security Notes

⚠️ **Important**: The default credentials (`postgres`/`postgres`) are for development only. 

For production:
1. Change the password in `.db.env`
2. Use environment-specific configuration
3. Consider using Docker secrets for sensitive data
4. Restrict network access appropriately

## Quick Start Summary

```bash
# 1. Navigate to project
cd /path/to/fastapi-postgresql-boilerplate

# 2. Start PostgreSQL
docker-compose up -d postgresql

# 3. Verify it's running
docker-compose ps

# 4. Connect to database
docker exec -it postgresql psql -U postgres -d postgres
```

That's it! Your PostgreSQL database is now running and ready for development.