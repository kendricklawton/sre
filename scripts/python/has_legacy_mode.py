def has_legacy_mode(data):
    """
    Recursively searches a nested data structure (dictionaries and lists)
    to find if any key matches 'legacy_mode' with a value of True.

    Args:
        data: The list, dictionary, or primitive value to search.

    Returns:
        bool: True if "legacy_mode": True is found anywhere, otherwise False.
    """

    # --- Check 1: Is the current data a Dictionary? ---
    if isinstance(data, dict):
        # Iterate through every key-value pair in the dictionary
        for key, value in data.items():
            # SUCCESS CONDITION:
            # Check if we found the specific key AND the value is explicitly True.
            if key == "legacy_mode" and value is True:
                return True

            # RECURSIVE STEP (Depth-First Search):
            # If we didn't find the key here, pass the 'value' back into this
            # same function to see if the target exists deeper inside it.
            if has_legacy_mode(value):
                return True  # Propagate 'True' up the chain if found deeper

    # --- Check 2: Is the current data a List? ---
    elif isinstance(data, list):
        # Iterate through every item in the list
        for item in data:
            # RECURSIVE STEP:
            # Lists don't have keys, so we just check if the item inside
            # contains the target by calling the function on the item.
            if has_legacy_mode(item):
                return True  # Propagate 'True' up the chain if found deeper

    # --- Check 3: Stop Condition ---
    # If data is neither a dict nor a list (e.g., an integer or string),
    # or if the loops finish without finding anything, return False.
    return False


# --- Example Usage ---
config = {
    "cluster": "alpha",
    "nodes": [
        {"id": 1, "settings": {"legacy_mode": False}},
        {
            "id": 2,
            "settings": {"advanced": {"legacy_mode": True}},
        },  # Target is hidden here
    ],
}

# print(has_legacy_mode(config)) # Returns True
