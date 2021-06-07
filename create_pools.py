import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Wingman.settings')
import django
django.setup()

from bs4 import BeautifulSoup
from main_app.models import Matches, Pools
from datetime import datetime, timedelta


all_matches = Matches.objects.order_by('match_date')
last_matches = Matches.objects.filter(match_pool = Pools.objects.last())

print(len(last_matches))
