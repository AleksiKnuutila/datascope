from .base import *

DATABASES["default"]["ENGINE"] = 'django.db.backends.mysql'
DATABASES["default"]["NAME"] = 's52573__datascope'
DATABASES["default"]["USER"] = 's52573'
DATABASES["default"]["PASSWORD"] = MYSQL_PASSWORD
DATABASES["default"]["HOST"] = 'tools-db'

STATIC_URL = "http://tools-static.wmflabs.org/algo-news/static/"

# TODO: add STATIC_IP
