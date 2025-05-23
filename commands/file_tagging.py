def smart_search_files(query):
    query = query.lower()
    matches = []

    if not os.path.exists(TAG_FILE):
        return []

    with open(TAG_FILE, "r") as f:
        for line in f:
            if "::" not in line:
                continue
            file_name, meta = line.strip().split("::", 1)
            if query in file_name.lower() or query in meta.lower():
                matches.append((file_name, meta))

    return matches
