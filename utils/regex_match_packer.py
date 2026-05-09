import re


def find_string(search_string, input_string):
    """Whole-word, case-insensitive search for `search_string` in `input_string`."""
    pattern = r"\b" + re.escape(search_string) + r"\b"
    return re.search(pattern, input_string, flags=re.IGNORECASE) is not None
