#!/usr/bin/env python
"""
Celery Worker Script
Run this to start the Celery worker for background tasks

Usage:
    celery -A celery_worker.celery worker --loglevel=info --pool=solo
    celery -A celery_worker.celery beat --loglevel=info
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run import app, celery


if __name__ == '__main__':
    
    celery.worker_main(['worker', '--loglevel=info', '--pool=solo'])

