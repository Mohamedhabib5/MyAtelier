from __future__ import annotations

import json
import os
import sys
import time
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import pandas as pd
from plotly.utils import PlotlyJSONEncoder

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import logic
from logic import SessionLocal, Booking, Customer, Service, Dress, Payment, Department
