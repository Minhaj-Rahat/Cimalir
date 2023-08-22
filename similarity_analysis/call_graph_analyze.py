import js_pcode as tzp


def call_graph_jaccard(similar_funcs, pcode_dict1, pcode_dict2, caller1, caller2, callee1, callee2,  threshold):

    sim_func = {}
    p1 = {}
    p2 = {}
    for key in similar_funcs.keys():
        p1[key] = pcode_dict1[key]
    for key in similar_funcs.values():
        p2[key] = pcode_dict2[key]

    pcode_set1 = tzp.pcode_set(pcode_dict1)
    pcode_set2 = tzp.pcode_set(pcode_dict2)

    for f1, f2 in similar_funcs.items():
        f1_set = pcode_set1[f1]
        f2_set = pcode_set2[f2]

        for callers in caller1[f1]:
            try:
                f1_set.union(pcode_set1[callers])
            except:
                continue

        for callers in caller2[f2]:
            try:
                f2_set.union(pcode_set2[callers])
            except:
                continue
        for callees in callee1[f1]:
            try:
                f1_set.union(pcode_set1[callees])
            except:
                continue
        for callees in callee2[f2]:
            try:
                f2_set.union(pcode_set2[callees])
            except:
                continue

        if tzp.jaccard_score(f1_set,f2_set) > threshold:
            sim_func[f1] = f2



    return sim_func


def call_graph_jacard_ambiguous(similar_funcs, pcode_dict1, pcode_dict2, caller1, caller2, callee1, callee2,
                              threshold):
    sim_func = {}
    ambigs = {}
    for key in similar_funcs.keys():
        p1 = {}

        p1[key] = pcode_dict1[key]
        pcode_set1 = tzp.pcode_set(p1)


        f1_set = pcode_set1[key]
        for callers in caller1[key]:
            try:
                f1_set.union(pcode_set1[callers])
            except:
                continue
        for callees in callee1[key]:
            try:
                f1_set.append(pcode_set1[callees])
            except:
                continue


        keys2 = similar_funcs[key]
        # print(keys2)
        if len(keys2) == 0:
            continue
        if not type(keys2) == list:
            p2 = {}

            p2[keys2] = pcode_dict2[keys2]

            pcode_set2 = tzp.pcode_set(p2)


            f2_set = pcode_set2[keys2]

            for callers in caller2[keys2]:
                try:
                    f2_set.union(pcode_set2[callers])
                except:
                    continue

            for callees in callee2[keys2]:
                try:
                    f2_set.union(pcode_set2[callees])
                except:
                    continue




            if tzp.jaccard_score(f1_set, f2_set) > threshold:
                sim_func[key] = keys2

        else:
            for key2 in keys2:

                p2 = {}
                sim_list = []

                p2[key2] = pcode_dict2[key2]


                pcode_set2 = tzp.pcode_set(p2)

                f2_set = pcode_set2[key2]

                for callers in caller2[key2]:
                    try:
                        f2_set.union(pcode_set2[callers])
                    except:
                        continue

                for callees in callee2[key2]:
                    try:
                        f2_set.union(pcode_set2[callees])
                    except:
                        continue

                if tzp.jaccard_score(f1_set, f2_set) > threshold:
                    sim_list.append(key2)



            if len(sim_list) == 1:
                sim_func[key] = sim_list[0]
            else:
                ambigs[key] = sim_list

    return sim_func, ambigs


