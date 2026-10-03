"""Unsplash MCP Server
Provides search_photos and get_photo tools for Next.js and frontend applications.
Supports official Unsplash API with automatic fallback to an authentic Unsplash CDN photo catalogue.
"""

import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("UnsplashServer")

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()

# Authentic curated Unsplash CDN photography catalogue across core SaaS & product domains
CURATED_UNSPLASH_PHOTOS = [
    # Dashboard & Analytics & Data
    {
        "id": "photo-1551288049-bebda4e38f71",
        "title": "Financial charts and dashboard telemetry visualization",
        "url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=400&q=80",
        "author": "Luke Chesser",
        "author_url": "https://unsplash.com/@lukechesser",
        "tags": ["dashboard", "analytics", "data", "telemetry", "chart", "metrics", "finance", "business"],
    },
    {
        "id": "photo-1460925895917-afdab827c52f",
        "title": "Data analytics and performance growth indicators",
        "url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=400&q=80",
        "author": "Carlos Muza",
        "author_url": "https://unsplash.com/@kmuza",
        "tags": ["analytics", "dashboard", "charts", "growth", "seo", "statistics", "report"],
    },
    # Cybersecurity & Infrastructure & Cloud
    {
        "id": "photo-1558494949-ef010cbdcc31",
        "title": "High density enterprise server rack and datacenter infrastructure",
        "url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=400&q=80",
        "author": "Lars Kienle",
        "author_url": "https://unsplash.com/@larskienle",
        "tags": ["server", "datacenter", "cloud", "infrastructure", "devops", "hosting", "hardware", "network"],
    },
    {
        "id": "photo-1563986768609-322da13575f3",
        "title": "Cybersecurity digital shield and information security protection",
        "url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=400&q=80",
        "author": "FLY:D",
        "author_url": "https://unsplash.com/@flyd2069",
        "tags": ["security", "cybersecurity", "privacy", "protection", "shield", "encryption", "auth", "devsecops"],
    },
    {
        "id": "photo-1526374965328-7f61d4dc18c5",
        "title": "Software code matrix and security terminal stream",
        "url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=400&q=80",
        "author": "Markus Spiske",
        "author_url": "https://unsplash.com/@markusspiske",
        "tags": ["code", "software", "programming", "matrix", "terminal", "developer", "hacker", "tech"],
    },
    # Modern Workspace, Team & Collaboration
    {
        "id": "photo-1497366216548-37526070297c",
        "title": "Minimalist modern open-plan office architectural interior",
        "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=400&q=80",
        "author": "Nastuh Abootalebi",
        "author_url": "https://unsplash.com/@nas_abootalebi",
        "tags": ["office", "workspace", "architecture", "interior", "minimal", "modern", "design", "corporate"],
    },
    {
        "id": "photo-1522071820081-009f0129c71c",
        "title": "Agile engineering team collaborating around workspace laptops",
        "url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=400&q=80",
        "author": "Annie Spratt",
        "author_url": "https://unsplash.com/@anniespratt",
        "tags": ["team", "collaboration", "people", "meeting", "agile", "startup", "developer", "work"],
    },
    # Architecture, Minimalist & Design
    {
        "id": "photo-1600585154340-be6161a56a0c",
        "title": "High-end contemporary modern residential and commercial architecture",
        "url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=400&q=80",
        "author": "R Architecture",
        "author_url": "https://unsplash.com/@rarchitecture_melbourne",
        "tags": ["architecture", "building", "luxury", "modern", "minimal", "interior", "exterior", "real estate"],
    },
    {
        "id": "photo-1618005182384-a83a8bd57fbe",
        "title": "Minimalist geometric 3D abstract waves and iridescent lighting",
        "url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=400&q=80",
        "author": "Milad Fakurian",
        "author_url": "https://unsplash.com/@fakurian",
        "tags": ["abstract", "3d", "minimal", "gradient", "geometry", "hero", "background", "creative"],
    },
    # Education, Exam, Learning & CEFR
    {
        "id": "photo-1523240795612-9a054b0db644",
        "title": "University students engaged in academic study and discussion",
        "url": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=400&q=80",
        "author": "Priscilla Du Preez",
        "author_url": "https://unsplash.com/@priscilladupreez",
        "tags": ["education", "students", "learning", "exam", "university", "cefr", "study", "language", "school"],
    },
    {
        "id": "photo-1434030216411-0b793f4b4173",
        "title": "Student writing notes and preparing for examination",
        "url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=400&q=80",
        "author": "Green Chameleon",
        "author_url": "https://unsplash.com/@craftedbygc",
        "tags": ["exam", "test", "writing", "notes", "study", "cefr", "assessment", "education", "course"],
    },
    # AI, Neural Networks & Future Tech
    {
        "id": "photo-1677442136019-21780ecad995",
        "title": "Artificial intelligence neural network cognitive interface",
        "url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=400&q=80",
        "author": "Steve Johnson",
        "author_url": "https://unsplash.com/@steve_j",
        "tags": ["ai", "artificial intelligence", "neural", "machine learning", "future", "algorithm", "robot"],
    },
    # Finance, Fintech & Banking
    {
        "id": "photo-1559526324-4b87b5e36e44",
        "title": "Fintech payment processing and corporate portfolio growth",
        "url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1600&q=80",
        "thumb": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=400&q=80",
        "author": "Austin Distel",
        "author_url": "https://unsplash.com/@austindistel",
        "tags": ["finance", "fintech", "banking", "payment", "investment", "money", "accounting", "economy"],
    },
]


def _format_photo_result(
    photo_id: str,
    title: str,
    regular_url: str,
    full_url: Optional[str] = None,
    thumb_url: Optional[str] = None,
    author: Optional[str] = None,
    author_url: Optional[str] = None,
    width: int = 1600,
    height: int = 900,
) -> Dict[str, Any]:
    full_url = full_url or regular_url
    thumb_url = thumb_url or regular_url
    author = author or "Unsplash Photographer"
    author_url = author_url or "https://unsplash.com"
    clean_title = (title or "Modern photography").replace('"', '&quot;')

    jsx_snippet = (
        f'<Image\n'
        f'  src="{regular_url}"\n'
        f'  alt="{clean_title}"\n'
        f'  width={{{width}}}\n'
        f'  height={{{height}}}\n'
        f'  className="w-full h-full object-cover rounded-xl transition-all duration-300 hover:scale-105"\n'
        f'/>'
    )

    return {
        "id": photo_id,
        "title": title,
        "url": regular_url,
        "urls": {
            "regular": regular_url,
            "full": full_url,
            "thumb": thumb_url,
        },
        "author": {
            "name": author,
            "profile_url": author_url,
        },
        "dimensions": {
            "width": width,
            "height": height,
            "aspect_ratio": "16:9",
        },
        "jsx_snippet": jsx_snippet,
    }


def _search_unsplash_official(query: str, per_page: int = 10, orientation: str = "landscape") -> Optional[Dict[str, Any]]:
    if not UNSPLASH_ACCESS_KEY:
        return None
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": min(per_page, 30),
            "client_id": UNSPLASH_ACCESS_KEY,
        }
        if orientation in ("landscape", "portrait", "squarish"):
            params["orientation"] = orientation
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get("results", []):
                    urls = item.get("urls", {})
                    user = item.get("user", {})
                    results.append(_format_photo_result(
                        photo_id=item.get("id", "photo"),
                        title=item.get("alt_description") or item.get("description") or query,
                        regular_url=urls.get("regular") or urls.get("full") or "",
                        full_url=urls.get("full"),
                        thumb_url=urls.get("thumb"),
                        author=user.get("name"),
                        author_url=user.get("links", {}).get("html"),
                        width=item.get("width", 1600),
                        height=item.get("height", 900),
                    ))
                return {
                    "source": "unsplash_official_api",
                    "query": query,
                    "total": data.get("total", len(results)),
                    "photos": results,
                }
    except Exception:
        pass
    return None


def _search_curated_and_commons(query: str, per_page: int = 10) -> Dict[str, Any]:
    query_tokens = [t.lower().strip() for t in query.split() if t.strip()]
    matched_photos = []

    # Score curated photos
    for photo in CURATED_UNSPLASH_PHOTOS:
        score = 0
        photo_tags = photo.get("tags", [])
        photo_title = photo.get("title", "").lower()
        for token in query_tokens:
            if any(token in tag for tag in photo_tags):
                score += 3
            if token in photo_title:
                score += 2
        if score > 0:
            matched_photos.append((score, photo))

    matched_photos.sort(key=lambda x: x[0], reverse=True)
    results = []
    for _, photo in matched_photos[:per_page]:
        results.append(_format_photo_result(
            photo_id=photo["id"],
            title=photo["title"],
            regular_url=photo["url"],
            thumb_url=photo["thumb"],
            author=photo.get("author"),
            author_url=photo.get("author_url"),
        ))

    # If results are fewer than requested, enrich with Wikimedia Commons bitmap images
    if len(results) < per_page:
        needed = per_page - len(results)
        try:
            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": f"filetype:bitmap {query}",
                "gsrnamespace": "6",
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "format": "json",
                "gsrlimit": str(min(needed * 2, 20)),
            }
            with httpx.Client(headers={"User-Agent": "AntigravityDev/1.0 (contact: admin@example.com)"}, timeout=8.0) as client:
                r = client.get("https://commons.wikimedia.org/w/api.php", params=params)
                if r.status_code == 200:
                    pages = r.json().get("query", {}).get("pages", {})
                    for _, page in pages.items():
                        info = page.get("imageinfo", [{}])[0]
                        img_url = info.get("url")
                        mime = info.get("mime", "")
                        if img_url and ("image/jpeg" in mime or "image/png" in mime or "image/webp" in mime):
                            clean_name = page.get("title", "").replace("File:", "").split(".")[0].replace("_", " ")
                            results.append(_format_photo_result(
                                photo_id=f"commons_{page.get('pageid')}",
                                title=clean_name or query,
                                regular_url=img_url,
                                author="Wikimedia Commons Contributor",
                                author_url="https://commons.wikimedia.org",
                                width=info.get("width", 1600) or 1600,
                                height=info.get("height", 900) or 900,
                            ))
                            if len(results) >= per_page:
                                break
        except Exception:
            pass

    # If still empty, fall back to high-grade default photo
    if not results:
        fallback = CURATED_UNSPLASH_PHOTOS[0]
        results.append(_format_photo_result(
            photo_id=fallback["id"],
            title=f"{query} photographic visual",
            regular_url=fallback["url"],
            thumb_url=fallback["thumb"],
            author=fallback.get("author"),
            author_url=fallback.get("author_url"),
        ))

    return {
        "source": "curated_and_commons_engine",
        "query": query,
        "total": len(results),
        "photos": results,
    }


@mcp.tool(name="search_photos")
def search_photos(query: str, per_page: int = 10, orientation: str = "landscape") -> Dict[str, Any]:
    """Search high-resolution royalty-free photos on Unsplash with JSX snippet and direct CDN URLs.

    Args:
        query: Subject to search (e.g. 'modern glass office', 'cybersecurity dashboard', 'minimalist architecture').
        per_page: Number of photos to retrieve (default 10, max 30).
        orientation: Photo orientation ('landscape', 'portrait', or 'squarish').
    """
    res = _search_unsplash_official(query, per_page=per_page, orientation=orientation)
    if res and res.get("photos"):
        return res
    return _search_curated_and_commons(query, per_page=per_page)


@mcp.tool(name="get_photo")
def get_photo(photo_id: str) -> Dict[str, Any]:
    """Retrieve details and direct high-resolution URLs for a specific Unsplash photo ID.

    Args:
        photo_id: The Unsplash photo ID or identifier.
    """
    if UNSPLASH_ACCESS_KEY:
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(
                    f"https://api.unsplash.com/photos/{photo_id}",
                    params={"client_id": UNSPLASH_ACCESS_KEY},
                )
                if resp.status_code == 200:
                    item = resp.json()
                    urls = item.get("urls", {})
                    user = item.get("user", {})
                    return _format_photo_result(
                        photo_id=item.get("id", photo_id),
                        title=item.get("alt_description") or item.get("description") or photo_id,
                        regular_url=urls.get("regular") or urls.get("full") or "",
                        full_url=urls.get("full"),
                        thumb_url=urls.get("thumb"),
                        author=user.get("name"),
                        author_url=user.get("links", {}).get("html"),
                        width=item.get("width", 1600),
                        height=item.get("height", 900),
                    )
        except Exception:
            pass

    for p in CURATED_UNSPLASH_PHOTOS:
        if p["id"] == photo_id or photo_id in p["url"]:
            return _format_photo_result(
                photo_id=p["id"],
                title=p["title"],
                regular_url=p["url"],
                thumb_url=p["thumb"],
                author=p.get("author"),
                author_url=p.get("author_url"),
            )

    cdn_url = f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w=1600&q=80"
    return _format_photo_result(
        photo_id=photo_id,
        title=f"Unsplash Photo {photo_id}",
        regular_url=cdn_url,
    )


if __name__ == "__main__":
    mcp.run()
