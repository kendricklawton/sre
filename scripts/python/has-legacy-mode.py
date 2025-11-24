def has_legacy_mode(data):
    # Base Case: Dictionary
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "legacy_mode" and value is True:
                return True
            # Recursive step for nested dicts
            if has_legacy_mode(value):
                return True

    # Base Case: List
    elif isinstance(data, list):
        for item in data:
            if has_legacy_mode(item):
                return True

    return False


# Example Usage
config = {
    "cluster": "alpha",
    "nodes": [
        {"id": 1, "settings": {"legacy_mode": False}},
        {"id": 2, "settings": {"advanced": {"legacy_mode": True}}},  # Deeply nested
    ],
}
# print(has_legacy_mode(config)) # Returns True
