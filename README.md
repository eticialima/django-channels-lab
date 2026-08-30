# Django Channels Chat - Real-Time WebSocket Chat

A simple, educational Django project demonstrating real-time chat functionality using Django Channels and WebSockets.

## Project Overview

This project showcases:
- **Django Channels** for WebSocket support
- **ASGI** application server configuration
- **WebSocket Consumer** for handling real-time communication
- **Redis** as the channel layer for multi-process deployment
- **Bootstrap 5** for responsive UI
- **Vanilla JavaScript** for WebSocket client management

## Project Architecture

```
Client (Browser)
      ↓ (WebSocket)
Daphne (ASGI Server)
      ↓
Django Channels Consumer
      ↓
Redis Channel Layer
```

**Components:**
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Backend:** Django + Django Channels
- **WebSocket Server:** Daphne (ASGI)
- **Message Broker:** Redis
- **Database:** SQLite (development)

## Features

✅ Real-time chat messaging  
✅ User presence notifications (join/leave)  
✅ Connection status indicator  
✅ Message history persistence  
✅ Responsive Bootstrap UI  
✅ Auto-reconnection on disconnect  
✅ HTML escape for security  

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

## Testing the Chat

1. **Open first browser tab:**
   ```
   http://127.0.0.1:8000/
   ```

2. **Enter your name and click "Join Chat"**
   - You'll be redirected to the chat room

3. **Open second browser tab:**
   ```
   http://127.0.0.1:8000/
   ```

4. **Enter a different name and join**
   - See "User joined" notification in both tabs
   - Send messages from either tab
   - Messages appear in real-time in both tabs

5. **Test disconnect:**
   - Close one browser tab
   - See "User left" notification in the other tab

## Project Structure

```
django-channels-chat/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                # Example environment variables
├── docker-compose.yml           # Redis container configuration
├── README.md                    # This file
│
├── ProjectChannels/             # Main Django project
│   ├── settings.py             # Django settings (ASGI, Channels config)
│   ├── asgi.py                 # ASGI application with WebSocket routing
│   ├── urls.py                 # Main URL router
│   ├── wsgi.py                 # WSGI application (production)
│   └── __init__.py
│
└── chat/                        # Chat application
    ├── models.py               # Message model for persistence
    ├── views.py                # HTTP views (index, room)
    ├── consumers.py            # WebSocket consumer (handles WS events)
    ├── routing.py              # WebSocket URL routing
    ├── urls.py                 # HTTP URL routing
    ├── admin.py                # Django admin configuration
    ├── apps.py                 # App configuration
    ├── tests.py                # Unit tests
    ├── __init__.py
    │
    ├── migrations/
    │   └── __init__.py
    │
    ├── templates/chat/
    │   ├── index.html          # Home page (enter username)
    │   └── room.html           # Chat room page
    │
    └── static/
        ├── css/
        │   └── style.css       # Chat styling (Bootstrap + custom)
        └── js/
            └── chat.js         # WebSocket client (ChatWebSocket class)
```

## Key Files Explained

### `ProjectChannels/asgi.py`
Configures ASGI application with WebSocket routing. Uses `ProtocolTypeRouter` to route HTTP and WebSocket protocols separately.

### `chat/consumers.py`
WebSocket consumer that handles:
- Connection/disconnection events
- User join/leave notifications
- Message broadcasting
- Database persistence

### `chat/static/js/chat.js`
Frontend WebSocket client (`ChatWebSocket` class) that:
- Establishes WebSocket connection
- Sends/receives messages
- Updates UI
- Handles auto-reconnection

### `chat/models.py`
Message model that persists chat messages to SQLite database.

## Environment Variables

Create `.env` file based on `.env.example`:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
REDIS_URL=redis://127.0.0.1:6379/0
```

- `SECRET_KEY`: Django secret key (change in production)
- `DEBUG`: Set to `False` in production
- `REDIS_URL`: Redis connection string

## Troubleshooting

### Redis Connection Error
```
ConnectionError: Error -2 connecting to 127.0.0.1:6379
```
**Solution:** Ensure Redis is running:
```bash
docker compose up -d
docker compose ps  # Verify redis service is running
```

### Messages Not Updating
1. Check WebSocket connection status (badge in navbar)
2. Open browser DevTools (F12) → Console tab
3. Look for connection errors
4. Verify Redis is running

### Port Already in Use
```
Address already in use
```
Change Django port:
```bash
python manage.py runserver 8001
```

## Development Tips

### Enable Debug Logging
Add to `settings.py`:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.channels': {'handlers': ['console'], 'level': 'DEBUG'},
    },
}
```

### Test WebSocket Connection
In browser console:
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws/chat/test/');
ws.onopen = () => console.log('Connected!');
ws.send(JSON.stringify({type: 'user_join', username: 'test'}));
```

### View Database Queries
Use Django admin:
```
http://127.0.0.1:8000/admin/
```
Login with superuser credentials to see Message records.

## Deployment Considerations

This setup is for **development only**. For production:

1. **Use production ASGI server:**
   - Daphne with multiple workers
   - Gunicorn with uvicorn workers

2. **Configure Redis:**
   - Use managed Redis service (AWS ElastiCache, Azure Cache, etc.)
   - Set up persistence and backup

3. **Database:**
   - Use PostgreSQL instead of SQLite
   - Set up proper backups

4. **Security:**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Use HTTPS/WSS

5. **Load Balancing:**
   - Use multiple Daphne instances
   - Ensure Redis is the shared channel layer

## Learning Resources

- [Django Channels Documentation](https://channels.readthedocs.io/)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Redis Documentation](https://redis.io/docs/)

## License

MIT License - Free to use for educational purposes.

## Author

Created as an educational project demonstrating Django Channels and WebSocket integration.
