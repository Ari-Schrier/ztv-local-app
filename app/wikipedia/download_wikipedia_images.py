import os
import metadata_fetcher as mf
import re
import requests
from urllib.parse import urlparse, unquote

def download_all_images(location, imagesDict):
    """
    Download all images described by `imagesDict` into `location`.

    Parameters
    ----------
    location : str
        Directory path to save images (created if it doesn't exist).
    imagesDict : list[dict] | dict[str, dict]
        Either:
          - a list of dicts like those returned by get_pd_cc0_images(...)
            (expects keys: 'image_url' (or 'url'), 'file_title' (optional)), OR
          - a dict mapping file_title -> info dict.

    Returns
    -------
    list[dict]
        One entry per image with keys:
        {
          "file_title": str | None,
          "url": str | None,
          "path": str | None,       # final file path if ok
          "ok": bool,
          "error": str | None
        }
    """
    os.makedirs(location, exist_ok=True)

    def _safe_name(file_title, url):
        # Prefer the Wikimedia title; else derive from URL
        if file_title:
            name = file_title.replace("File:", "")
        else:
            path = urlparse(url).path
            name = os.path.basename(path)
        name = unquote(name).split("?")[0]

        # Strip common thumbnail prefix like "1200px-Filename.jpg"
        name = re.sub(r'^\d{2,4}px-', '', name)

        # Replace characters illegal on common filesystems
        name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()

        # Fallback
        return name or "image"

    results = []

    # Support both a list of dicts and a dict keyed by title
    items = imagesDict.items() if isinstance(imagesDict, dict) else enumerate(imagesDict)

    for _, info in items:
        url = info.get("image_url") or info.get("url")
        file_title = info.get("file_title") or info.get("title")

        if not url:
            results.append({"file_title": file_title, "url": url, "path": None, "ok": False,
                            "error": "missing image_url"})
            continue

        filename = _safe_name(file_title, url)
        path = os.path.join(location, filename)
        base, ext = os.path.splitext(path)

        # Ensure unique filename if it already exists
        counter = 1
        while os.path.exists(path):
            path = f"{base} ({counter}){ext}"
            counter += 1

        try:
            with requests.get(url, stream=True, timeout=60,
                              headers={"User-Agent": "wikimedia-image-fetcher/1.0"}) as r:
                r.raise_for_status()

                # If no extension, infer from Content-Type
                if not ext and "content-type" in r.headers:
                    ct = r.headers["content-type"].split(";")[0].strip().lower()
                    guessed = {
                        "image/jpeg": ".jpg",
                        "image/png": ".png",
                        "image/gif": ".gif",
                        "image/webp": ".webp",
                        "image/svg+xml": ".svg",
                        "image/tiff": ".tif",
                    }.get(ct)
                    if guessed:
                        path = base + guessed

                with open(path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 15):
                        if chunk:
                            f.write(chunk)

            results.append({"file_title": file_title, "url": url, "path": path, "ok": True, "error": None})

        except Exception as e:
            results.append({"file_title": file_title, "url": url, "path": None, "ok": False, "error": str(e)})

    return results
