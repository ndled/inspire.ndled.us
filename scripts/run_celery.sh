#!/bin/sh
su -m app -c "celery -A youtube_screen_grab.views worker --pool=solo -l INFO"