import json
from src.search.engine import search_index

def test_correctness():
    index = [
        {"id": 1, "text": "Apple banana carrot"},
        {"id": 2, "text": "Banana smoothie"},
        {"id": 3, "text": "Carrot cake recipe"}
    ]

    result = search_index("banana", index)
    ids = [item["id"] for item in result["results"]]

    assert 1 in ids
    assert 2 in ids
    assert 3 not in ids

def test_latency():
    index = [{"id": i, "text": "sample text"} for i in range(50000)]
    result = search_index("sample", index)
    assert result["latency_ms"] < 200

if __name__ == "__main__":
    test_correctness()
    test_latency()
    print("Search performance tests passed.")
