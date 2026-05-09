def jaccard_score(A, B):
    union = A | B
    if not union:
        return 0
    return len(A & B) / len(union)


def _mnemonic(line):
    """Pick the mnemonic token from a P-code line.

    Lines that begin with '(' carry an output varnode prefix and the
    mnemonic is the 4th whitespace-separated token; otherwise it's the 2nd.
    """
    parts = line.split()
    return parts[3] if parts[0][0] == '(' else parts[1]


def pcode_set(pcode_dict):
    return {addr: {_mnemonic(line) for line in lines}
            for addr, lines in pcode_dict.items()}


def pcode_set2(pcode_dict):
    """Same as pcode_set but for bytes-encoded lines."""
    out = {}
    for addr, lines in pcode_dict.items():
        out[addr] = {_mnemonic(line.decode('utf-8')) for line in lines}
    return out


def pcode_set_shingle(shingles, func, pcode_dict):
    lines = pcode_dict[func]
    if len(lines) < shingles:
        return {_mnemonic(line) for line in lines}

    tokens = [_mnemonic(line) for line in lines]
    return {' '.join(tokens[i:i + shingles])
            for i in range(len(lines) - shingles - 1)}


def count_cBranch(pcode_dict):
    counts = {}
    for addr, lines in pcode_dict.items():
        n = 0
        for line in lines:
            parts = line.decode('utf-8').split()
            if parts[0][0] != '(' and parts[1] == 'CBRANCH':
                n += 1
        counts[addr] = n
    return counts
