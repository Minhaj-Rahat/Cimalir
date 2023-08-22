import js_pcode as tzp  # Jaccard similarity and cbranch count
from scipy.spatial import distance  # calculate Euclidean distance



# method to remove repeating addresses in sym_func
def remove_repeating(sim_func, ambiguous):
    new_dict = {}
    seen_values = set()
    removed_values = set()
    for key, value in sim_func.items():
        if value not in seen_values:
            new_dict[key] = value
            seen_values.add(value)
        else:
            if value not in removed_values:
                to_remove = []
                for k, v in new_dict.items():
                    if v == value:
                        to_remove.append(k)
                for k in to_remove:
                    ambiguous[k] = new_dict.pop(k)
                ambiguous[key] = value
                removed_values.add(value)
    return new_dict, ambiguous


def func_similarity(pcode1, ff1, pt1, pcode2, ff2, pt2, threshold, similarity_weight, param_datatype_weight,
                    similarity_threshold):
    s1 = tzp.pcode_set(pcode1)
    s2 = tzp.pcode_set(pcode2)


    f1_addr = list(pcode1.keys())
    f2_addr = list(pcode2.keys())

    list__sim_func = {}

    for i in f1_addr:
        set1 = s1[i]
        sim_func = []
        for j in f2_addr:

            if tzp.jaccard_score(set1, s2[j]) >= threshold:
                sim_func.append(j)
        list__sim_func[i] = sim_func


    ambiguous = {}
    for i in f1_addr:
        # if in the previous step only one function is found in the similarity list, do not have to consider later steps
        if len(list__sim_func[i]) == 1:
            list__sim_func[i] = list__sim_func[i][0]
            continue

        similarity = 1000000

        for j in range(len(list__sim_func[i])):
            f1_feature = ff1[i].copy()
            f2_feature = ff2[list__sim_func[i][j]].copy()

            param_dict = {}
            for params in pt1[i]:
                param_dict[str(params)] = 0
            for params in pt2[list__sim_func[i][j]]:
                param_dict[str(params)] = 0

            for params in pt1[i]:
                param_dict[str(params)] += 1

            p1 = list(param_dict.values())

            param_dict = dict.fromkeys(param_dict, 0)
            for params in pt2[list__sim_func[i][j]]:
                param_dict[str(params)] += 1

            p2 = list(param_dict.values())


            f1_feature += p1

            f2_feature += p2

            param_weight = [param_datatype_weight] * len(p1)
            # check whether the similarity score is the smallest and below the threshold
            if distance.euclidean(f1_feature, f2_feature,
                                  similarity_weight + param_weight) < similarity and distance.euclidean(f1_feature,
                                                                                                        f2_feature,
                                                                                                        similarity_weight + param_weight) <= similarity_threshold:
                sim_func = list__sim_func[i][j]
                similarity = distance.euclidean(f1_feature, f2_feature, similarity_weight + param_weight)


            # if similarity score is same for more than two samples they are ambiguous
            if list__sim_func[i][j] != sim_func and distance.euclidean(f1_feature, f2_feature,
                                                                       similarity_weight + param_weight) == similarity:
                if i not in list(ambiguous.keys()):
                    ambiguous[i] = []

                if list__sim_func[i][j] not in ambiguous[i]:
                    ambiguous[i].append(list__sim_func[i][j])

        if i in list(ambiguous.keys()):
            ambiguous[i].append(sim_func)
        elif sim_func != None:
            list__sim_func[i] = sim_func
        sim_func = None

    # if list__sim_func[i] has more than one sim func it is ambiguous, delete that, because that should be in the ambiguous match
    for i in list(ambiguous.keys()):
        del list__sim_func[i]

    for i in list(list__sim_func.keys()):

        if type(list__sim_func[i]) == list:
            ambiguous[i] = list__sim_func[i]
            del list__sim_func[i]

    # do a final check for ambiguity in sim_funcs
    list__sim_func, ambiguous = remove_repeating(list__sim_func, ambiguous)
    return list__sim_func, ambiguous
