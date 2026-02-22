from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import ScanRequest, ScanResponse
from app.seo_checker import run_scan

app = FastAPI(
    title="SEO Health Checker API",
    description="Analyze a website's SEO health across multiple pages.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "SEO Health Checker API",
        "version": "1.0.0",
        "docs": "/docs",
        "by": "Janssens & Janssens Webservices",
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/scan", response_model=ScanResponse)
def scan_website(req: ScanRequest):
    result = run_scan(str(req.url))
    return result