MAX_PAGES = 10
REQUEST_TIMEOUT = 10

SCORE_WEIGHTS = {
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

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://seo-checker-web-nine.vercel.app",
    "https://seo.janssens-janssens-webservices.be",
    "https://www.janssens-janssens-webservices.be",
]