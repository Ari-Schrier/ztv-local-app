import requests
import time
from html import unescape
import re
from typing import Iterable, Iterator
from urllib.parse import quote

# --------- config ---------

USER_AGENT = (
    "ZinniaWikiImageScraper/0.3 (+schrier.a@northeastern.edu) "
    "requests/+https://docs.python-requests.org/"
)

# One shared session for connection reuse and a single UA definition.
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})
DEFAULT_TIMEOUT = 30  # seconds

# --------- small helpers ---------

def _html_to_text(s: str | None) -> str | None:
    if not s:
        return s
    return unescape(re.sub(r"<[^>]+>", "", s)).strip()

def _chunk(iterable: Iterable[str], n: int) -> Iterator[list[str]]:
    it = iter(iterable)
    while True:
        batch = []
        try:
            for _ in range(n):
                batch.append(next(it))
        except StopIteration:
            pass
        if not batch:
            return
        yield batch

def _is_cc0_or_public_domain(extmeta: dict) -> bool:
    """
    extmeta is the 'extmetadata' dict from imageinfo.
    We conservatively accept Public Domain (including PD variants).
    CC0 is currently DISABLED per your comment.
    """
    getv = lambda k: (extmeta.get(k) or {}).get("value", "")
    license_short = getv("LicenseShortName").lower()      # e.g., "CC0", "Public domain"
    license_url   = getv("LicenseUrl").lower()            # e.g., CC0 or PD Mark URLs
    license_code  = getv("License").lower()               # e.g., "cc-zero", "pd-usgov", etc.

    # CC0 checks (currently OFF by design)
    # Set to True if you want CC0.
    if "cc0" in license_short or "cc0" in license_code or "publicdomain/zero" in license_url:
        return False

    # Public domain checks
    if "public domain" in license_short:
        return True
    if "pd" in license_code:  # pd-usgov, pd-old, pd-self, etc.
        return True
    if "/publicdomain/mark/" in license_url:
        return True

    return False

# --------- MediaWiki request wrapper ---------

def _mw_get(
    url: str,
    params: dict,
    session: requests.Session = SESSION,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = 5,
    base_sleep: float = 1.0,
) -> dict:
    """
    GET with polite retry for MediaWiki API:
      - Retries on 429/503 and 'maxlag' errors with exponential backoff.
      - Respects Retry-After header if present.
      - Raises with a clear message on 403.
    """
    attempt = 0
    while True:
        attempt += 1
        r = session.get(url, params=params, timeout=timeout)

        # Handle hard block / policy issues early and verbosely
        if r.status_code == 403:
            raise RuntimeError(
                "403 from Wikimedia API. Check your User-Agent (must be descriptive with contact info), "
                "IP reputation, and request volume. Response excerpt: "
                f"{r.text[:300]!r}"
            )

        # Polite retry when rate-limited or cluster is busy
        if r.status_code in (429, 503):
            if attempt >= max_retries:
                r.raise_for_status()
            retry_after = r.headers.get("Retry-After")
            if retry_after:
                try:
                    sleep_for = float(retry_after)
                except ValueError:
                    sleep_for = base_sleep * (2 ** (attempt - 1))
            else:
                sleep_for = base_sleep * (2 ** (attempt - 1))
            time.sleep(sleep_for)
            continue

        r.raise_for_status()
        data = r.json()

        # MediaWiki sometimes returns maxlag as a JSON error but 200/503
        err = data.get("error", {})
        if err.get("code") == "maxlag":
            if attempt >= max_retries:
                raise RuntimeError(f"Hit maxlag repeatedly: {err}")
            sleep_for = base_sleep * (2 ** (attempt - 1))
            time.sleep(sleep_for)
            continue

        return data

# --------- core functions ---------

def _get_page_file_titles(title: str, lang: str = "en") -> list[str]:
    """
    Return a de-duplicated list of 'File:...' titles used on the page
    (including images used via templates).
    """
    api = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "prop": "images",
        "titles": title,
        "imlimit": "max",
        "redirects": 1,
        "maxlag": 5,
    }

    files: set[str] = set()
    cont: dict = {}

    while True:
        data = _mw_get(api, {**params, **cont})
        pages = data.get("query", {}).get("pages", []) or []
        for page in pages:
            for img in page.get("images") or []:
                t = img.get("title")
                if t and t.startswith("File:"):
                    files.add(t)

        if "continue" in data:
            cont = data["continue"]  # will include imcontinue
        else:
            break

    return sorted(files)

def _get_imageinfo_with_extmetadata(file_titles: list[str], api: str) -> dict[str, dict]:
    """
    Query one MediaWiki API endpoint (e.g., enwiki or Commons) for
    imageinfo & extmetadata in batches. Returns mapping:
      file_title -> imageinfo dict (or {} if missing).
    """
    if not file_titles:
        return {}

    out: dict[str, dict] = {t: {} for t in file_titles}

    # Titles limit is ~50 for regular users.
    for batch in _chunk(file_titles, 50):
        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "prop": "imageinfo",
            "titles": "|".join(batch),
            "iiprop": "url|extmetadata|size",
            "redirects": 1,
            "maxlag": 5,
            # You could narrow extmetadata fields, but leaving default is fine:
            # "iiextmetadatafilter": "LicenseShortName|LicenseUrl|License|Artist|Credit",
        }

        data = _mw_get(api, params)
        pages = data.get("query", {}).get("pages", []) or []

        # With formatversion=2, each page has 'title' and maybe 'missing'
        for page in pages:
            title = page.get("title")
            if not title:
                continue
            infos = page.get("imageinfo") or []
            if infos:
                out[title] = infos[0]  # first revision is sufficient for url/size/extmetadata

    return out

def get_pd_cc0_images(title: str, lang: str = "en", skip_svg: bool = True) -> list[dict]:
    print("Getting file titles")
    file_titles = _get_page_file_titles(title, lang=lang)
    print("Got file titles")

    # Drop SVGs early so we don’t even query them
    if skip_svg:
        file_titles = [t for t in file_titles if not t.lower().endswith(".svg")]

    if not file_titles:
        return []

    commons_api = "https://commons.wikimedia.org/w/api.php"
    lang_api = f"https://{lang}.wikipedia.org/w/api.php"

    # Fetch from the local wiki first, then fall back to Commons for misses
    info_lang    = _get_imageinfo_with_extmetadata(file_titles, lang_api)
    missing      = [t for t, ii in info_lang.items() if not ii]
    info_commons = _get_imageinfo_with_extmetadata(missing, commons_api) if missing else {}

    results: list[dict] = []
    for t in file_titles:
        ii = info_lang.get(t) or info_commons.get(t) or {}
        if not ii:
            continue

        # Extra safety: if an SVG sneaks in via URL somehow, skip it
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
