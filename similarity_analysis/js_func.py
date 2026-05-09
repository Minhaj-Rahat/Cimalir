import js_pcode as tzp
from collections import Counter
from scipy.spatial import distance


def remove_repeating(sim_func, ambiguous):
    """Strip values that appear more than once from `sim_func` into `ambiguous`.

    Preserves the original characterization: once a value has been moved to
    ambiguous, further occurrences are dropped silently rather than re-added.
    """
    new_dict = {}
    first_key_for = {}
    removed_values = set()
    for key, value in sim_func.items():
        if value in removed_values:
            continue
        if value in first_key_for:
            first_key = first_key_for.pop(value)
            del new_dict[first_key]
            ambiguous[first_key] = value
            ambiguous[key] = value
            removed_values.add(value)
        else:
            new_dict[key] = value
            first_key_for[value] = key
    return new_dict, ambiguous


def func_similarity(pcode1, ff1, pt1, pcode2, ff2, pt2, threshold,
                    similarity_weight, param_datatype_weight, similarity_threshold):
    s1 = tzp.pcode_set(pcode1)
    s2 = tzp.pcode_set(pcode2)

    f1_addr = list(pcode1.keys())
    f2_addr = list(pcode2.keys())

    list__sim_func = {}
    for i in f1_addr:
        set1 = s1[i]
        list__sim_func[i] = [j for j in f2_addr
                             if tzp.jaccard_score(set1, s2[j]) >= threshold]

    ambiguous = {}
    for i in f1_addr:
        if len(list__sim_func[i]) == 1:
            list__sim_func[i] = list__sim_func[i][0]
            continue

        best = float('inf')
        sim_func_pick = None

        for j in list__sim_func[i]:
            f1_feature = list(ff1[i])
            f2_feature = list(ff2[j])

            c1 = Counter(str(p) for p in pt1[i])
            c2 = Counter(str(p) for p in pt2[j])
            all_params = list({**c1, **c2}.keys())
            p1 = [c1.get(k, 0) for k in all_params]
            p2 = [c2.get(k, 0) for k in all_params]

            f1_feature += p1
            f2_feature += p2
            param_weight = [param_datatype_weight] * len(p1)
            weights = similarity_weight + param_weight

            d = distance.euclidean(f1_feature, f2_feature, weights)

            if d < best and d <= similarity_threshold:
                sim_func_pick = j
                best = d
            elif j != sim_func_pick and d == best:
                ambiguous.setdefault(i, [])
                if j not in ambiguous[i]:
                    ambiguous[i].append(j)

        if i in ambiguous:
            ambiguous[i].append(sim_func_pick)
        elif sim_func_pick is not None:
            list__sim_func[i] = sim_func_pick

    for i in list(ambiguous.keys()):
        if i in list__sim_func:
            del list__sim_func[i]

    for i in list(list__sim_func.keys()):
        if isinstance(list__sim_func[i], list):
            ambiguous[i] = list__sim_func.pop(i)

    return remove_repeating(list__sim_func, ambiguous)
