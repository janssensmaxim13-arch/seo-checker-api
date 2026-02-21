"""
SEO Health Checker - Configuration
"""

# Crawl settings
MAX_PAGES = 10
REQUEST_DELAY = 0.5
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEOHealthChecker/1.0)"
}

# Score weights (total = 100)
WEIGHTS = {
    "title": 15,
    "meta_description": 10,
    "h1": 10,
    "canonical": 5,
    "robots_meta": 5,
    "open_graph": 5,
    "images_alt": 10,
    "page_speed": 10,
    "https": 5,
    "mobile_viewport": 5,
    "structured_data": 5,
    "internal_links": 5,
    "broken_links": 10,
}

# CORS - allowed origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://*.vercel.app",
]
