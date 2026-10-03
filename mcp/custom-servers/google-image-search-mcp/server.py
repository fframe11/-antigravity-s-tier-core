"""Google Image Search MCP Server
Provides search_images tool for frontend applications, web design, and asset discovery.
Supports Google Custom Search Engine with seamless fallback to verified high-resolution web media.
"""

import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GoogleImageSearchServer")

GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "").strip()
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX", "").strip()
USER_AGENT = "AntigravityImageSearch/1.0 (contact: admin@example.com)"


def _format_image_result(
    title: str,
    image_url: str,
    thumb_url: Optional[str] = None,
    source_url: Optional[str] = None,
    width: int = 1600,
    height: int = 900,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    thumb_url = thumb_url or image_url
    clean_title = (title or "Web visual").replace('"', '&quot;')
    domain = domain or "web"

    jsx_snippet = (
        f'<Image\n'
        f'  src="{image_url}"\n'
        f'  alt="{clean_title}"\n'
        f'  width={{{width}}}\n'
        f'  height={{{height}}}\n'
        f'  className="w-full h-full object-cover rounded-xl transition-all duration-300 hover:scale-105"\n'
        f'/>'
    )

    return {
        "title": title,
        "image_url": image_url,
        "thumbnail_url": thumb_url,
        "source_page": source_url or image_url,
        "domain": domain,
        "dimensions": {
            "width": width,
            "height": height,
            "aspect_ratio": f"{width}:{height}",
        },
        "jsx_snippet": jsx_snippet,
    }


def _search_google_custom_search(query: str, num: int = 10) -> Optional[Dict[str, Any]]:
    if not (GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX):
        return None
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_SEARCH_API_KEY,
            "cx": GOOGLE_SEARCH_CX,
            "q": query,
            "searchType": "image",
            "num": min(num, 10),
        }
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                results = []
                for item in items:
                    img = item.get("image", {})
                    results.append(_format_image_result(
                        title=item.get("title", query),
                        image_url=item.get("link", ""),
                        thumb_url=img.get("thumbnailLink"),
                        source_url=img.get("contextLink"),
                        width=img.get("width", 1600) or 1600,
                        height=img.get("height", 900) or 900,
                        domain=item.get("displayLink"),
                    ))
                return {
                    "source": "google_custom_search_api",
                    "query": query,
                    "total": len(results),
                    "images": results,
                }
    except Exception:
        pass
    return None


def _search_web_media_engine(query: str, num: int = 10) -> Dict[str, Any]:
    results = []
    try:
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}",
            "gsrnamespace": "6",
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "format": "json",
            "gsrlimit": str(min(num * 2, 30)),
        }
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=10.0) as client:
            r = client.get("https://commons.wikimedia.org/w/api.php", params=params)
            if r.status_code == 200:
                pages = r.json().get("query", {}).get("pages", {})
                for _, page in pages.items():
                    info = page.get("imageinfo", [{}])[0]
                    img_url = info.get("url")
                    mime = info.get("mime", "")
                    if img_url and ("image/jpeg" in mime or "image/png" in mime or "image/webp" in mime):
                        clean_name = page.get("title", "").replace("File:", "").split(".")[0].replace("_", " ")
                        meta = info.get("extmetadata", {})
                        source_page = info.get("descriptionurl")
                        results.append(_format_image_result(
                            title=clean_name or query,
                            image_url=img_url,
                            thumb_url=img_url,
                            source_url=source_page,
                            width=info.get("width", 1600) or 1600,
                            height=info.get("height", 900) or 900,
                            domain="commons.wikimedia.org",
                        ))
                        if len(results) >= num:
                            break
    except Exception as e:
        pass

    return {
        "source": "verified_web_media_engine",
        "query": query,
        "total": len(results),
        "images": results,
    }


@mcp.tool(name="search_images")
def search_images(query: str, num: int = 10, orientation: str = "all") -> Dict[str, Any]:
    """Search for authentic web images, brand visuals, diagrams, and photography.

    Args:
        query: Subject to search for (e.g. 'kubernetes architecture diagram', 'modern minimalist office', 'robotics laboratory').
        num: Number of images to return (default 10, max 20).
        orientation: Image orientation ('all', 'landscape', 'portrait', 'square').
    """
    res = _search_google_custom_search(query, num=num)
    if res and res.get("images"):
        return res
    return _search_web_media_engine(query, num=num)


if __name__ == "__main__":
    mcp.run()
