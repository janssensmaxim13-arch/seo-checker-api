MAX_PAGES = 10
REQUEST_TIMEOUT = 10
REQUEST_DELAY = 0.5
TIMEOUT = 10

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEOHealthChecker/1.0)"
}

WEIGHTS = {
    "https": 5,
    "title": 15,
    "meta_desc": 10,
    "h1": 10,
    "canonical": 5,
    "robots_meta": 5,
    "og_tags": 5,
    "img_alt": 10,
    "page_speed": 10,
    "mobile": 5,
    "structured_data": 5,
    "internal_links": 5,
    "broken_links": 10,
}

ALLOWED_ORIGINS = ["*"]