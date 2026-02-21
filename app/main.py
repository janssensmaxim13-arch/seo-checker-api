"""
SEO Health Checker - FastAPI Application
Main entry point for the API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import ScanRequest, ScanResponse
from app.seo_checker import run_scan

# ── App Setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SEO Health Checker API",
    description="Analyze a website's SEO health across multiple pages.",
    version="1.0.0",
)

# CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Root endpoint - API info"""
    return {
        "name": "SEO Health Checker API",
        "version": "1.0.0",
        "docs": "/docs",
        "by": "Janssens & Janssens Webservices",
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint for Railway"""
    return {"status": "ok"}


@app.post("/api/scan", response_model=ScanResponse)
def scan_website(request: ScanRequest):
    """
    Scan a website for SEO issues.
    Send a URL and get back a full SEO health report.
    """
    url = request.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        result = run_scan(url)
        return ScanResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
