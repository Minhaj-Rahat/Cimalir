import re
#from Pkg.UPXUnpacker.Unpack import unpack

"""
search_string --- the string to march
input_string -- given input string
"""


def find_string(search_string, input_string):

    search_word = r"\b" + search_string + r"\b"

    output = re.search(search_word, input_string, flags=re.IGNORECASE)

    no_match = (output is None)
    if no_match:
        return False
    else:
        return True
