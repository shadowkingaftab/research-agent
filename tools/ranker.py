def rank(results):

    seen = set()
    ranked = []

    for r in results:

        url = r.get("href") or r.get("url")

        if not url:
            continue

        if url in seen:
            continue

        seen.add(url)

        ranked.append(r)

    return ranked