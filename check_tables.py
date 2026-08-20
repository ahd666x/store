import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.dev'
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
print([row[0] for row in cursor.fetchall()])
