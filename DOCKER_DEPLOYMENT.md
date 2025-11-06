# Docker Deployment Guide

This guide explains how to deploy the Cinephile Automation server using Docker.

## Prerequisites

- Docker installed on your system ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Install Docker Compose](https://docs.docker.com/compose/install/))
- Your `.env` file configured with API keys (see [.env.example](.env.example))

## Quick Start

### 1. Configure Environment Variables

Create a `.env` file in the project root (if you haven't already):

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required API Keys
GTA_OMDB_API_KEY=your_omdb_key_here
GTA_TMDB_API_KEY=your_tmdb_key_here

# Optional: Backblaze B2 Cloud Storage
B2_APPLICATION_KEY_ID=your_b2_key_id_here
B2_APPLICATION_KEY=your_b2_key_here
B2_BUCKET_NAME=your_bucket_name_here
```

### 2. Start the Server

```bash
# Build and start the container
docker-compose up -d
```

The server will be available at: `http://localhost:8080`

### 3. View Logs

```bash
# View real-time logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### 4. Stop the Server

```bash
# Stop the container
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Docker Commands Reference

### Building

```bash
# Build the Docker image
docker-compose build

# Build without cache (fresh build)
docker-compose build --no-cache
```

### Running

```bash
# Start in background (detached mode)
docker-compose up -d

# Start in foreground (see logs directly)
docker-compose up

# Restart the service
docker-compose restart
```

### Monitoring

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f cinephile-automation

# Check resource usage
docker stats
```

### Maintenance

```bash
# Stop all services
docker-compose down

# Stop and remove all volumes (WARNING: removes output files)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# Execute commands inside container
docker-compose exec cinephile-automation bash
```

## Directory Structure

The Docker setup includes the following volumes:

```
/app/assets     - Background audio/video files (read-only)
/app/output     - Generated video output (read-write)
```

### Assets Directory

Place your background media files in the `assets/` directory:

```
assets/
├── background_audio.mp3
└── background_video.mp4
```

These files will be mounted as read-only in the container.

### Output Directory

Generated videos (when not using B2 upload) will be saved to the `output/` directory on your host machine.

## Environment Variables

The following environment variables can be configured:

| Variable | Required | Description |
|----------|----------|-------------|
| `GTA_OMDB_API_KEY` | Yes | OMDB API key for movie poster downloads |
| `GTA_TMDB_API_KEY` | Yes | TMDB API key for movie data |
| `B2_APPLICATION_KEY_ID` | No | Backblaze B2 application key ID |
| `B2_APPLICATION_KEY` | No | Backblaze B2 application key |
| `B2_BUCKET_NAME` | No | Backblaze B2 bucket name |

## Health Checks

The Docker container includes health checks that verify the server is running correctly:

- **Interval**: Check every 30 seconds
- **Timeout**: 10 seconds per check
- **Retries**: 3 failed checks before marking unhealthy
- **Start Period**: 10 seconds grace period on startup

View health status:

```bash
docker-compose ps
```

## Port Configuration

By default, the server runs on port `8080`. To change the port:

1. Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8080"  # Change 9000 to your desired port
```

2. Restart the container:
```bash
docker-compose up -d
```

## Troubleshooting

### Container Won't Start

1. Check logs for errors:
```bash
docker-compose logs
```

2. Verify `.env` file exists and has valid API keys

3. Check if port 8080 is already in use:
```bash
# Linux/Mac
lsof -i :8080

# Windows
netstat -ano | findstr :8080
```

### Permission Errors

If you encounter permission errors with volumes:

```bash
# Fix output directory permissions
chmod -R 777 output/
```

### Out of Memory

If video rendering fails due to memory:

1. Edit `docker-compose.yml` to add memory limits:
```yaml
services:
  cinephile-automation:
    # ... existing config ...
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### API Connection Issues

If the container can't reach external APIs:

1. Verify DNS resolution:
```bash
docker-compose exec cinephile-automation ping api.themoviedb.org
```

2. Check firewall settings
3. Verify API keys are correct in `.env`

## API Endpoints

Once the server is running, the following endpoints are available:

- `GET /` - Web UI
- `POST /create_tiktok_video` - Create video from manifest
- `POST /generate_manifest` - Generate manifest from actor name
- `POST /shutdown` - Gracefully shutdown server

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed API documentation.

## Production Deployment

For production deployments, consider:

1. **Using a reverse proxy** (nginx, Traefik) for HTTPS
2. **Setting resource limits** in docker-compose.yml
3. **Using Docker secrets** for API keys instead of .env
4. **Enabling logging to external service** (ELK, Splunk, etc.)
5. **Setting up monitoring** (Prometheus, Grafana)
6. **Regular backups** of output directory if not using B2

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Docker Image Management

### View Images

```bash
docker images | grep cinephile
```

### Remove Old Images

```bash
# Remove unused images
docker image prune

# Remove specific image
docker rmi cinephile-automation-cinephile-automation
```

### Export/Import Images

```bash
# Export image to tar file
docker save -o cinephile-automation.tar cinephile-automation-cinephile-automation

# Import image from tar file
docker load -i cinephile-automation.tar
```

## Development with Docker

To develop with Docker while seeing code changes:

1. Add a volume mount for code in `docker-compose.yml`:
```yaml
volumes:
  - .:/app
  - ./assets:/app/assets:ro
  - ./output:/app/output
```

2. Use development mode:
```bash
docker-compose up
```

Note: Python files will need container restart to reflect changes since we don't use auto-reload.

## Security Considerations

1. **Never commit `.env`** - Contains sensitive API keys
2. **Use Docker secrets** in production for sensitive data
3. **Run as non-root user** - Consider adding USER directive to Dockerfile
4. **Keep base images updated** - Regularly rebuild with latest Python image
5. **Scan for vulnerabilities** - Use `docker scan` to check for CVEs

## Performance Optimization

### Multi-stage Builds

For smaller images, consider a multi-stage build (future enhancement):

```dockerfile
# Builder stage
FROM python:3.11 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
```

### Build Cache

Speed up builds by ordering Dockerfile commands from least to most frequently changed.

## Support

For issues or questions:
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Review [B2_SETUP_GUIDE.md](B2_SETUP_GUIDE.md) for cloud storage setup
- Check Docker logs: `docker-compose logs -f`
