# Setup Local Development Environment

## Prerequisites
- Python 3.9+
- Git

## Installation Steps

### 1. Clone the repository
```bash
git clone <repository-url>
cd porvoz
```

### 2. Create and activate Python virtual environment
```bash
# Create venv
python -m venv venv

# Activate venv
# On Windows (Git Bash):
source venv/Scripts/activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
# Copy the template
cp .env.example .env

# Edit .env with your actual credentials:
# - EMAIL_HOST_USER: Your Gmail address
# - EMAIL_HOST_PASSWORD: Gmail App Password (see .env.example for how to get one)
# - TWILIO_*: Get from https://www.twilio.com/console
# - GEMINI_API_KEY: Get from https://ai.google.dev/
nano .env  # or open with your editor
```

### 5. Run database migrations
```bash
python manage.py migrate
```

### 6. Create superuser (optional, for Django admin)
```bash
python manage.py createsuperuser
```

### 7. Start development server
```bash
python manage.py runserver
```

The app will be available at `http://localhost:8000`

## Running Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.notificaciones

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## Important Files

| File | Purpose |
|------|---------|
| `.env.example` | Template with all required environment variables |
| `.env` | Your local configuration (**NEVER commit this**) |
| `requirements.txt` | Python dependencies |
| `manage.py` | Django management commands |

## Environment Variables Explained

**Development essentials:**
- `DJANGO_SECRET_KEY`: Secret for Django (can be anything for dev, use strong value in production)
- `TWILIO_*`: Required only if testing voice call features
- `GEMINI_API_KEY`: Required only if testing call transcription/classification
- `EMAIL_*`: Required only if testing email notifications

**Optional for dev:**
- `TWILIO_DRY_RUN=true`: Skip actual Twilio calls (useful for testing without charges)
- `TWILIO_BASE_URL`: Your server's public URL (for Twilio webhooks)

## Troubleshooting

### "ModuleNotFoundError: No module named..."
Activate your venv and run `pip install -r requirements.txt`

### "Permission denied" on migrations
Run `python manage.py migrate --run-syncdb`

### Email not sending
- Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env
- For Gmail, use an [App Password](https://myaccount.google.com/apppasswords), not your regular password
- If not configured, emails print to console (development.py fallback)

### Twilio errors
Set `TWILIO_DRY_RUN=true` in .env to simulate calls without charges

## Next Steps
1. See README.md for feature overview
2. Check sprint2.md for sprint goals and test coverage
3. Read doc strings in `apps/llamadas/services/` for call logic
