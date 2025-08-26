import requests
from html import unescape
import re
from urllib.parse import quote

# --------- small helpers ---------

def _html_to_text(s: str | None) -> str | None:
    if not s:
        return s
    return unescape(re.sub(r"<[^>]+>", "", s)).strip()

def _chunk(iterable, n):
    it = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(n):
                chunk.append(next(it))
        except StopIteration:
            pass
        if not chunk:
            return
        yield chunk

def _is_cc0_or_public_domain(extmeta: dict) -> bool:
    """
    extmeta is the 'extmetadata' dict from imageinfo.
    We conservatively accept CC0 and Public Domain (including PD variants).
    """
    getv = lambda k: (extmeta.get(k) or {}).get("value", "")
    license_short = getv("LicenseShortName").lower()      # e.g., "CC0", "Public domain"
    license_url   = getv("LicenseUrl").lower()            # e.g., CC0 or PD Mark URLs
    license_code  = getv("License").lower()               # e.g., "cc-zero", "pd-usgov", etc.

    # CC0 checks
    ##SET TO TRUE IF WE WANT TO START USING CC0
    if "cc0" in license_short or "cc0" in license_code or "publicdomain/zero" in license_url:
        return False

    # Public domain checks
    if "public domain" in license_short:
        return True
    if "pd" in license_code:  # covers many PD templates like pd-usgov, pd-old, pd-self, etc.
        return True
    if "/publicdomain/mark/" in license_url:
        return True

    return False

# --------- core functions ---------

def _get_page_file_titles(title: str, lang: str = "en") -> list[str]:
    """
    Return a de-duplicated list of 'File:...' titles used on the page (including images used via templates).
    """
    API = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "images",
        "titles": title,
        "imlimit": "max",
        "redirects": 1,
    }

    files = set()
    cont = {}
    while True:
        r = requests.get(API, params={**params, **cont}, timeout=30)
        r.raise_for_status()
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for _, page in pages.items():
            for img in page.get("images", []) or []:
                t = img.get("title")
                if t and t.startswith("File:"):
                    files.add(t)

        # pagination
        if "continue" in data:
            cont = data["continue"]
        else:
            break

    return sorted(files)

def _get_imageinfo_with_extmetadata(file_titles: list[str], api: str) -> dict[str, dict]:
    """
    Query one MediaWiki API endpoint (enwiki or Commons) for imageinfo&extmetadata
    in batches. Returns mapping: file_title -> imageinfo dict (or {} if missing).
    """
    out: dict[str, dict] = {t: {} for t in file_titles}
    for batch in _chunk(file_titles, 50):  # API titles limit ~50
        params = {
            "action": "query",
            "format": "json",
            "prop": "imageinfo",
            "titles": "|".join(batch),
            "iiprop": "url|extmetadata|size",
        }
        r = requests.get(api, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        for _, page in (data.get("query", {}).get("pages", {}) or {}).items():
            title = page.get("title")
            if not title:
                continue
            infos = page.get("imageinfo") or []
            if infos:
                out[title] = infos[0]
    return out

def get_pd_cc0_images(title: str, lang: str = "en", skip_svg: bool = True) -> list[dict]:
    file_titles = _get_page_file_titles(title, lang=lang)

    # NEW: drop SVGs early so we don’t even query them
    if skip_svg:
        file_titles = [t for t in file_titles if not t.lower().endswith(".svg")]

    if not file_titles:
        return []

    commons_api = "https://commons.wikimedia.org/w/api.php"
    lang_api = f"https://{lang}.wikipedia.org/w/api.php"

    info_lang    = _get_imageinfo_with_extmetadata(file_titles, lang_api)
    missing      = [t for t, ii in info_lang.items() if not ii]
    info_commons = _get_imageinfo_with_extmetadata(missing, commons_api) if missing else {}

    results = []
    for t in file_titles:
        ii = info_lang.get(t) or info_commons.get(t) or {}
        if not ii:
            continue

        # extra safety: if an SVG sneaks in via URL somehow, skip it
        if skip_svg:
            url_lc = (ii.get("url") or "").lower()
            if url_lc.endswith(".svg") or ".svg." in url_lc:  # e.g., rare .svg.png cases
                continue

        extmeta = ii.get("extmetadata") or {}
        if not _is_cc0_or_public_domain(extmeta):
            continue

        license_short = (extmeta.get("LicenseShortName") or {}).get("value")
        license_url   = (extmeta.get("LicenseUrl") or {}).get("value")
        artist_html   = (extmeta.get("Artist") or {}).get("value")
        credit_html   = (extmeta.get("Credit") or {}).get("value")

        results.append({
            "file_title": t,
            "image_url": ii.get("url"),
            "width": ii.get("width"),
            "height": ii.get("height"),
            "license": license_short,
            "license_url": license_url,
            "artist_html": artist_html,
            "artist_text": _html_to_text(artist_html),
            "credit_html": credit_html,
            "credit_text": _html_to_text(credit_html),
        })

    return results

# ------------------ Example ------------------
if __name__ == "__main__":
    # Try a page, e.g., Pike Place Market
    images = get_pd_cc0_images("Pike Place Market", lang="en")
    for img in images:
        print(img["file_title"], "=>", img["license"], img["image_url"])
