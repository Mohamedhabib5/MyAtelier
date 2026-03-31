import json
import os
import time
from datetime import date, timedelta
from pathlib import Path
from PIL import Image

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


BASE_URL = os.environ.get('APP_URL', 'http://127.0.0.1:8050')
HEADLESS = os.environ.get('HEADLESS', '0').lower() not in ('0', 'false', 'no')
USERNAME = os.environ.get('APP_USER', 'admin')
PASSWORD = os.environ.get('APP_PASS', 'admin123')
BOOKING_ONLY = os.environ.get('BOOKING_ONLY', '0').lower() not in ('0', 'false', 'no')
CORE_SMOKE = os.environ.get('CORE_SMOKE', '0').lower() not in ('0', 'false', 'no')
CUSTODY_SMOKE = os.environ.get('CUSTODY_SMOKE', '0').lower() not in ('0', 'false', 'no')
FULL_REGRESSION = os.environ.get('FULL_REGRESSION', '0').lower() not in ('0', 'false', 'no')
FULL_PHASE = os.environ.get('FULL_PHASE', 'all').strip().lower()
RESPONSIVE_SMOKE = os.environ.get('RESPONSIVE_SMOKE', '0').lower() not in ('0', 'false', 'no')
COMPENSATION_SMOKE = os.environ.get('COMPENSATION_SMOKE', '0').lower() not in ('0', 'false', 'no')
NEXT_ACTION_LABEL = 'الإجراء التالي'
