import requests

def get_public_domain_image(query):
    base_url = "https://commons.wikimedia.org/w/api.php"
    
    # Step 1: Search for matching file pages (namespace 6 = File)
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,
        "format": "json"
    }
    search_response = requests.get(base_url, params=search_params).json()
    search_results = search_response.get("query", {}).get("search", [])
    
    if not search_results:
        return {"status": "not_found", "message": "No file results found."}

    # Step 2: Try each result until we find a public domain or CC0 *image*
    for result in search_results:
        file_title = result["title"]
        
        metadata_params = {
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|mime|mediatype",
            "format": "json"
        }
        meta_response = requests.get(base_url, params=metadata_params).json()
        pages = meta_response.get("query", {}).get("pages", {})
        page_data = next(iter(pages.values()), {})
        imageinfos = page_data.get("imageinfo", [])
        
        if not imageinfos:
            continue
        
        imageinfo = imageinfos[0]
        extmeta = imageinfo.get("extmetadata", {})
        
        mime_type = imageinfo.get("mime", "")
        if not mime_type.startswith("image/"):
            continue  # Skip PDFs, audio, etc.

        license_short = extmeta.get("LicenseShortName", {}).get("value", "").lower()
        license_url = extmeta.get("LicenseUrl", {}).get("value", "").lower()
        attribution_required = extmeta.get("AttributionRequired", {}).get("value", "").lower()
        
        if "public domain" in license_short or "cc0" in license_url:
            return {
                "status": "success",
                "title": file_title,
                "image_url": imageinfo.get("url"),
                "license": license_short.title(),
                "license_url": license_url,
                "attribution_required": attribution_required
            }

    return {"status": "no_public_domain", "message": "No public domain or CC0 image found."}

def main():
    queries = [
        "Charles Sumner preston brooks",
        "FIFA logo",
        "Stormont Parliament northern ireland"
    ]

    
    for query in queries:
        print(f"\n🔍 Searching for: {query}")
        result = get_public_domain_image(query)
        
        if result["status"] == "success":
            print("✅ Found public domain image:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['image_url']}")
            print(f"License: {result['license']} ({result['license_url']})")
            print(f"Attribution Required: {result['attribution_required']}")
        else:
            print(f"❌ {result['message']}")


if __name__ == "__main__":
    main()