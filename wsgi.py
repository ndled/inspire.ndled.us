"""Entry point for gunicorn"""

from youtube_screen_grab import create_app

app = create_app()
