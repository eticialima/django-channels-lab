
## Installation

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
# Copy example to actual .env
cp .env.example .env

# Edit .env with your settings (optional for development)
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional - for Django admin)

```bash
python manage.py createsuperuser
```

## Running the Project

### Start Redis (using Docker)

```bash
docker compose up -d
```

Verify Redis is running:
```bash
redis-cli ping
# Output: PONG
```

### Start Django Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000`

**Important:** Use `runserver` for testing. For production-like ASGI, use:
```bash
daphne -b 127.0.0.1 -p 8000 ProjectChannels.asgi:application
```
