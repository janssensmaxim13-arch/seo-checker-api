"""
SEO Health Checker - Scanner Engine
Based on the original script, adapted to return data instead of printing.
"""

import re
import time
from urllib.parse import urljoin, urlparse
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from app.config import MAX_PAGES, REQUEST_DELAY, TIMEOUT, HEADERS, WEIGHTS


# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch(url: str):
    """Fetch a URL and return response + load time in ms"""
    try:
        start = time.time()
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        elapsed = round((time.time() - start) * 1000)
        return r, elapsed
    except Exception:
        return None, None


def is_same_domain(base: str, url: str) -> bool:
    """Check if two URLs are on the same domain"""
    return urlparse(base).netloc == urlparse(url).netloc


def clean_text(text: str) -> str:
    """Clean up whitespace in text"""
    return " ".join(text.split()) if text else ""


def get_grade(score: int) -> str:
    """Convert score to letter grade"""
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


# ── Per-page checks ──────────────────────────────────────────────────────────

def check_page(url: str, response, load_time_ms: int) -> dict:
    """Run all SEO checks on a single page and return results as dict"""
    soup = BeautifulSoup(response.text, "html.parser")
    issues = []
    passed = []
    score = 0

    def ok(key, msg):
        passed.append(f"✅ {msg}")
        return WEIGHTS.get(key, 0)

    def fail(key, msg):
        issues.append(f"❌ {msg}")
        return 0

    def warn(key, msg):
        issues.append(f"⚠️ {msg}")
        return WEIGHTS.get(key, 0) // 2

    # 1. HTTPS
    if url.startswith("https://"):
        score += ok("https", "HTTPS enabled")
    else:
        score += fail("https", "Page is not served over HTTPS")

    # 2. Title tag
    title_tag = soup.find("title")
    title = clean_text(title_tag.get_text()) if title_tag else ""
    if not title:
        score += fail("title", "Missing <title> tag")
    elif len(title) < 30:
        score += warn("title", f"Title too short ({len(title)} chars): '{title}'")
    elif len(title) > 60:
        score += warn("title", f"Title too long ({len(title)} chars): '{title[:60]}...'")
    else:
        score += ok("title", f"Title length OK ({len(title)} chars)")

    # 3. Meta description
    meta_desc = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    desc = clean_text(meta_desc["content"]) if meta_desc and meta_desc.get("content") else ""
    if not desc:
        score += fail("meta_description", "Missing meta description")
    elif len(desc) < 70:
        score += warn("meta_description", f"Meta description too short ({len(desc)} chars)")
    elif len(desc) > 160:
        score += warn("meta_description", f"Meta description too long ({len(desc)} chars)")
    else:
        score += ok("meta_description", f"Meta description length OK ({len(desc)} chars)")

    # 4. H1 tag
    h1s = soup.find_all("h1")
    if not h1s:
        score += fail("h1", "Missing <h1> tag")
    elif len(h1s) > 1:
        score += warn("h1", f"Multiple <h1> tags found ({len(h1s)})")
    else:
        score += ok("h1", "Single <h1> tag present")

    # 5. Canonical
    canonical = soup.find("link", rel=lambda r: r and "canonical" in r)
    if canonical:
        score += ok("canonical", f"Canonical URL set: {canonical.get('href', '')[:60]}")
    else:
        score += fail("canonical", "No canonical <link> tag")

    # 6. Robots meta
    robots = soup.find("meta", attrs={"name": re.compile("robots", re.I)})
    if robots:
        content = robots.get("content", "").lower()
        if "noindex" in content:
            score += fail("robots_meta", f"Page is set to noindex: '{content}'")
        else:
            score += ok("robots_meta", f"Robots meta OK: '{content}'")
    else:
        score += warn("robots_meta", "No robots meta tag (defaults to index,follow)")

    # 7. Open Graph
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    og_count = sum(1 for x in [og_title, og_desc, og_image] if x)
    if og_count == 3:
        score += ok("open_graph", "Open Graph tags present (title, description, image)")
    elif og_count > 0:
        score += warn("open_graph", f"Incomplete Open Graph tags ({og_count}/3 found)")
    else:
        score += fail("open_graph", "No Open Graph tags found")

    # 8. Images without alt
    images = soup.find_all("img")
    missing_alt = [img.get("src", "")[:50] for img in images if not img.get("alt")]
    if not images:
        score += ok("images_alt", "No images found (nothing to check)")
    elif not missing_alt:
        score += ok("images_alt", f"All {len(images)} image(s) have alt attributes")
    else:
        ratio = len(missing_alt) / len(images)
        if ratio < 0.25:
            score += warn("images_alt", f"{len(missing_alt)}/{len(images)} images missing alt text")
        else:
            score += fail("images_alt", f"{len(missing_alt)}/{len(images)} images missing alt text")

    # 9. Page speed (load time)
    if load_time_ms is None:
        score += fail("page_speed", "Could not measure load time")
    elif load_time_ms < 800:
        score += ok("page_speed", f"Fast load time: {load_time_ms}ms")
    elif load_time_ms < 2000:
        score += warn("page_speed", f"Moderate load time: {load_time_ms}ms (aim for <800ms)")
    else:
        score += fail("page_speed", f"Slow load time: {load_time_ms}ms (aim for <800ms)")

    # 10. Mobile viewport
    viewport = soup.find("meta", attrs={"name": re.compile("viewport", re.I)})
    if viewport:
        score += ok("mobile_viewport", "Mobile viewport meta tag present")
    else:
        score += fail("mobile_viewport", "Missing mobile viewport meta tag")

    # 11. Structured data
    json_ld = soup.find_all("script", type="application/ld+json")
    microdata = soup.find_all(attrs={"itemscope": True})
    if json_ld or microdata:
        score += ok("structured_data", f"Structured data found ({len(json_ld)} JSON-LD, {len(microdata)} microdata)")
    else:
        score += warn("structured_data", "No structured data (JSON-LD / microdata) found")

    # 12. Internal links
    links = soup.find_all("a", href=True)
    internal = [l["href"] for l in links if is_same_domain(url, urljoin(url, l["href"]))]
    if len(internal) >= 3:
        score += ok("internal_links", f"{len(internal)} internal links found")
    elif internal:
        score += warn("internal_links", f"Only {len(internal)} internal link(s) - add more")
    else:
        score += fail("internal_links", "No internal links found")

    # 13. Broken links (sample up to 10)
    broken = []
    sampled = links[:10]
    for a in sampled:
        href = urljoin(url, a["href"])
        if not href.startswith("http"):
            continue
        try:
            r = requests.head(href, headers=HEADERS, timeout=5, allow_redirects=True)
            if r.status_code >= 400:
                broken.append(f"{href} ({r.status_code})")
        except Exception:
            broken.append(f"{href} (timeout/error)")
        time.sleep(0.1)

    if not broken:
        score += ok("broken_links", f"No broken links detected (checked {len(sampled)})")
    else:
        score += fail("broken_links", f"{len(broken)} broken link(s): {broken[0]}" + (f" +{len(broken)-1} more" if len(broken) > 1 else ""))

    # Collect discovered links for crawl queue
    discovered = []
    for a in links:
        href = urljoin(url, a["href"])
        parsed = urlparse(href)
        if parsed.scheme in ("http", "https") and is_same_domain(url, href):
            clean = parsed._replace(fragment="").geturl()
            discovered.append(clean)

    max_score = sum(WEIGHTS.values())
    pct = round(score / max_score * 100)

    return {
        "url": url,
        "status": response.status_code,
        "load_ms": load_time_ms,
        "score": pct,
        "passed": passed,
        "issues": issues,
        "title": title,
        "h1": clean_text(h1s[0].get_text()) if h1s else "",
        "discovered": discovered,
    }


# ── Crawl ─────────────────────────────────────────────────────────────────────

def run_scan(start_url: str) -> dict:
    """
    Crawl a website and return complete SEO report as dict.
    This is the main function called by the API.
    """
    if not start_url.startswith("http"):
        start_url = "https://" + start_url

    visited = set()
    queue = [start_url]
    results = []

    while queue and len(visited) < MAX_PAGES:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        response, load_ms = fetch(url)
        if response is None:
            continue
        if "text/html" not in response.headers.get("content-type", ""):
            continue

        result = check_page(url, response, load_ms)
        results.append(result)

        for link in result["discovered"]:
            if link not in visited and link not in queue:
                queue.append(link)

        time.sleep(REQUEST_DELAY)

    if not results:
        return {
            "url": start_url,
            "pages_crawled": 0,
            "overall_score": 0,
            "grade": "F",
            "results": [],
            "top_issues": [],
            "recommendations": ["Could not fetch any pages from this URL."],
        }

    # Calculate overall score
    avg_score = round(sum(r["score"] for r in results) / len(results))

    # Find top issues across all pages
    issue_counts = defaultdict(int)
    for r in results:
        for issue in r["issues"]:
            clean = re.sub(r'^[^\w]+', '', issue).strip()
            issue_counts[clean] += 1

    top_issues = [
        {"issue": issue, "count": count}
        for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1])[:8]
    ]

    # Generate recommendations
    recommendations = []
    all_issues = " ".join(i for r in results for i in r["issues"])

    if "title" in all_issues.lower():
        recommendations.append("Fix title tags: aim for 30-60 characters, include target keyword.")
    if "meta description" in all_issues.lower():
        recommendations.append("Write meta descriptions: 70-160 chars, compelling for CTR.")
    if "h1" in all_issues.lower():
        recommendations.append("Ensure each page has exactly one <h1> with the primary keyword.")
    if "canonical" in all_issues.lower():
        recommendations.append("Add canonical <link> tags to prevent duplicate content issues.")
    if "alt" in all_issues.lower():
        recommendations.append("Add descriptive alt text to all images.")
    if "slow" in all_issues.lower() or "load" in all_issues.lower():
        recommendations.append("Improve page speed: compress images, enable caching, use a CDN.")
    if "open graph" in all_issues.lower():
        recommendations.append("Add Open Graph tags (og:title, og:description, og:image) for social sharing.")
    if "structured" in all_issues.lower():
        recommendations.append("Implement JSON-LD structured data (Schema.org) for rich snippets.")
    if "https" in all_issues.lower():
        recommendations.append("Migrate to HTTPS - it's a confirmed Google ranking signal.")
    if not recommendations:
        recommendations.append("Great job! Keep monitoring regularly and build quality backlinks.")

    # Remove discovered links from results (not needed in API response)
    clean_results = [
        {k: v for k, v in r.items() if k != "discovered"}
        for r in results
    ]

    return {
        "url": start_url,
        "pages_crawled": len(results),
        "overall_score": avg_score,
        "grade": get_grade(avg_score),
        "results": clean_results,
        "top_issues": top_issues,
        "recommendations": recommendations,
    }
