# Scrapy settings for scrapy_scrapers project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
import sys
import json
import django
from pathlib import Path

# Django Integration
settings_dir = Path(__file__).parent
scrapy_project_path = settings_dir.parent
django_project_path = scrapy_project_path.parent
sys.path.insert(0, str(settings_dir))
sys.path.insert(0, str(scrapy_project_path))
sys.path.insert(0, str(django_project_path))
os.environ['DJANGO_SETTINGS_MODULE'] = 'instaproj.settings'
# os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_scrapers.settings' # fixme
django.setup()
from django.conf import settings

BOT_NAME = 'scrapy_scrapers'

SPIDER_MODULES = ['scrapy_scrapers.spiders']
NEWSPIDER_MODULE = 'scrapy_scrapers.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'scrapy_scrapers (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'scrapy_scrapers.middlewares.ScrapyScrapersSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html

# EXTENSIONS = {
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

with open(settings.BASE_DIR / 'data/instagram_cookies.json') as file:
    INSTAGRAM_COOKIES: list[dict] = json.load(file)
for c in INSTAGRAM_COOKIES:
    expires = c['expiry']
    del c['expiry']
    c['expires'] = expires
    
