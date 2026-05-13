"""
Dev helper — exposes the local Django server (port 8000) over ngrok.

Usage:
    python scripts/ngrok_run.py

After it prints the public URL, copy it into .env as TWILIO_BASE_URL so Twilio
webhooks can reach the development machine.
"""
import time

from pyngrok import ngrok

tunnel = ngrok.connect(8000)
print(f"\nURL publica: {tunnel.public_url}")
print("Pon esa URL en .env como TWILIO_BASE_URL")
print("\nNgrok corriendo... Ctrl+C para parar\n")

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    ngrok.kill()
    print("Ngrok detenido.")
