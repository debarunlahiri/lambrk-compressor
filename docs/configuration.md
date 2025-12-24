# Configuration Documentation

Complete configuration guide for the Lambrk Compression Service.

## Environment Variables

All configuration is done through environment variables. You can set them in:

1. `.env` file in the project root
2. System environment variables
3. Shell export commands

### Database Configuration

#### POSTGRES_HOST
- **Description**: PostgreSQL server hostname
- **Default**: `localhost`
- **Example**: `localhost` or `192.168.1.100`

```bash
export POSTGRES_HOST=localhost
```

#### POSTGRES_PORT
- **Description**: PostgreSQL server port
- **Default**: `5432`
- **Example**: `5432`

```bash
export POSTGRES_PORT=5432
```

#### POSTGRES_USER
- **Description**: PostgreSQL username
- **Default**: `debarunlahiri`
- **Example**: `lambrk_user`

```bash
export POSTGRES_USER=debarunlahiri
```

#### POSTGRES_PASSWORD
- **Description**: PostgreSQL password
- **Default**: `` (empty string)
- **Example**: `my_secure_password`

```bash
export POSTGRES_PASSWORD=my_secure_password
```

**Note**: If password is empty, the service will attempt passwordless authentication (useful for local development with trust authentication).

#### POSTGRES_DB
- **Description**: PostgreSQL database name
- **Default**: `lambrk`
- **Example**: `lambrk_production`

```bash
export POSTGRES_DB=lambrk
```

---

### Directory Configuration

#### PENDING_DIR
- **Description**: Directory where pending video files are stored
- **Default**: `/Volumes/Expansion/Lambrk/pending`
- **Example**: `/var/videos/pending`

```bash
export PENDING_DIR=/Volumes/Expansion/Lambrk/pending
```

**Requirements:**
- Directory must exist or be creatable
- Service must have read permissions
- Video files should be placed here before compression

#### COMPLETED_DIR
- **Description**: Directory where compressed videos are saved
- **Default**: `/Volumes/Expansion/Lambrk/completed`
- **Example**: `/var/videos/completed`

```bash
export COMPLETED_DIR=/Volumes/Expansion/Lambrk/completed
```

**Requirements:**
- Directory must exist or be creatable
- Service must have write permissions
- Structure: `{COMPLETED_DIR}/{video_id}/{filename}_{quality}.mp4`

---

### API Configuration

#### API_HOST
- **Description**: Host address to bind the API server
- **Default**: `0.0.0.0` (all interfaces)
- **Example**: `0.0.0.0` or `127.0.0.1`

```bash
export API_HOST=0.0.0.0
```

**Options:**
- `0.0.0.0`: Listen on all network interfaces (accessible from network)
- `127.0.0.1`: Listen only on localhost (local access only)

#### API_PORT
- **Description**: Port number for the API server
- **Default**: `4500`
- **Example**: `4500` or `3000`

```bash
export API_PORT=4500
```

**Note**: Ensure the port is not already in use by another service.

---

### Logging Configuration

#### LOG_LEVEL
- **Description**: Logging verbosity level
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

```bash
export LOG_LEVEL=INFO
```

**Levels:**
- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical error messages

---

## Configuration File Example

Create a `.env` file in the project root:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=debarunlahiri
POSTGRES_PASSWORD=
POSTGRES_DB=lambrk

# Directory Configuration
PENDING_DIR=/Volumes/Expansion/Lambrk/pending
COMPLETED_DIR=/Volumes/Expansion/Lambrk/completed

# API Configuration
API_HOST=0.0.0.0
API_PORT=4500

# Logging Configuration
LOG_LEVEL=INFO
```

## Configuration Loading

The service uses `pydantic-settings` to load configuration:

1. Environment variables (highest priority)
2. `.env` file in project root
3. Default values (lowest priority)

Configuration is loaded in `app/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    # ... other settings
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

## Production Configuration

For production environments, consider:

### Security
- Use strong PostgreSQL passwords
- Restrict API_HOST to internal network if possible
- Use environment variables instead of `.env` file
- Enable SSL/TLS for database connections

### Performance
- Adjust `max_workers` for batch processing based on CPU cores
- Use SSD storage for video directories
- Configure PostgreSQL connection pool size
- Monitor disk space for completed videos

### High Availability
- Use PostgreSQL replication
- Implement health checks
- Set up monitoring and alerting
- Configure automatic restarts

## Environment-Specific Configurations

### Development

```bash
POSTGRES_HOST=localhost
POSTGRES_USER=debarunlahiri
POSTGRES_PASSWORD=
LOG_LEVEL=DEBUG
API_HOST=127.0.0.1
```

### Staging

```bash
POSTGRES_HOST=staging-db.example.com
POSTGRES_USER=lambrk_staging
POSTGRES_PASSWORD=staging_password
LOG_LEVEL=INFO
API_HOST=0.0.0.0
```

### Production

```bash
POSTGRES_HOST=prod-db.example.com
POSTGRES_USER=lambrk_prod
POSTGRES_PASSWORD=secure_production_password
LOG_LEVEL=WARNING
API_HOST=0.0.0.0
```

## Validation

The configuration is validated on startup. Invalid values will cause the service to fail with clear error messages.

## Dynamic Configuration

Some settings can be adjusted at runtime:

- **Batch processing workers**: Set via API request `max_workers` parameter
- **Quality selection**: Configured in `utils/video_utils.py` QUALITY_CONFIGS

## Troubleshooting

### Configuration not loading

1. Check `.env` file exists and is readable
2. Verify environment variables are set correctly
3. Check for typos in variable names
4. Ensure no conflicting values

### Database connection issues

1. Verify PostgreSQL is running
2. Check credentials are correct
3. Ensure database exists
4. Check network connectivity
5. Verify firewall rules

### Directory access issues

1. Check directory exists
2. Verify read/write permissions
3. Check disk space
4. Ensure correct path format

## Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong passwords** in production
3. **Set appropriate log levels** for each environment
4. **Monitor configuration changes** in production
5. **Document custom configurations** for your deployment
6. **Use secrets management** for sensitive values in production

