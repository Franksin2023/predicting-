import time

def search_index(query, index):
    """
    Baseline search implementation.
    Jules will mutate this file.
    """
    start = time.time()

    results = []
    q = query.lower()

    for item in index:
        text = item.get("text", "").lower()
        if q in text:
            results.append(item)

    latency = (time.time() - start) * 1000
    return {
        "results": results,
        "latency_ms": latency
    }
