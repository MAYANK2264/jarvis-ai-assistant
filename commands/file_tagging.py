def smart_search_files(query):
    import os

    query = query.strip().lower()
    matches = []

    if not os.path.exists(TAG_FILE):
        return []

    with open(TAG_FILE, "r") as f:
        for line in f:
            if "::" not in line:
                continue
            file_name, meta = line.strip().split("::", 1)
            file_name_lower = file_name.lower()
            meta_lower = meta.lower()

            if query in file_name_lower or query in meta_lower:
                # Score relevance
                score = 0
                if query in file_name_lower:
                    score += 2
                if query in meta_lower:
                    score += 1
                matches.append((score, file_name, meta))

    # Sort by relevance score (higher = more relevant)
    matches.sort(reverse=True)
    return [(file, meta) for _, file, meta in matches]
