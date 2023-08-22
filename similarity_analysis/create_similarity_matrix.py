import random
import os
import json
import ast
import pickle

import js_func as sh
import call_graph_analyze as cga

import concurrent.futures

'''create_sim_mat: create similarity matrix for our system'''
def create_sim_mat(class_folder):

    def similarity(i, j, pcodes1, func_features1, paramType1, callees1, callers1, threshold):
        f2 = open(sample_files[j], 'r')
        db2 = json.load(f2)
        f2.close()
        pcodes2 = ast.literal_eval(db2['pcode'])
        func_features2 = ast.literal_eval(db2['func_features'])
        paramType2 = ast.literal_eval(db2['paramType'])
        callees2 = ast.literal_eval(db2['callees'])
        callers2 = ast.literal_eval(db2['callers'])

        similar_funcs, ambiguous = sh.func_similarity(pcodes1, func_features1, paramType1,
                                                      pcodes2, func_features2, paramType2,
                                                      jaccard_thrshold, similarity_weight,
                                                      p_weight, similarity_score)
        final_sims = cga.call_graph_jaccard(similar_funcs, pcodes1, pcodes2, callers1, callers2, callees1, callees2,
                                            threshold)
        final_sims_ambig, ambigs = cga.call_graph_jacard_ambiguous(ambiguous, pcodes1, pcodes2, callers1, callers2,
                                                                   callees1,
                                                                   callees2, threshold)

        sims_combine = {**final_sims, **final_sims_ambig}

        overlap = len(sims_combine) / max(len(list(pcodes1.keys())), len(list(pcodes2.keys())))
        return overlap, j


    # set from genetic algorithm optmization
    jaccard_thrshold = 0.8
    similarity_score = 0.25
    call_w, calle_w, p_weight, c_weight = 74, 87, 73, 22
    call_graph_threshold = 0.85

    similarity_weight = [call_w, calle_w, p_weight, c_weight]

    get_files = lambda path: (os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files)


    # create class name and collect files to consider

    family_name = []
    sample_files = []
    count = 0
    for name in get_files(class_folder):
        family_name.append(name.split('/')[-2])
        sample_files.append(name)
        count += 1
        if count == 10:
            break

    score_dict = {}

    for i in range(len(sample_files)):
        f1 = open(sample_files[i], 'r')
        db1 = json.load(f1)
        f1.close()
        pcodes1 = ast.literal_eval(db1['pcode'])
        func_features1 = ast.literal_eval(db1['func_features'])
        paramType1 = ast.literal_eval(db1['paramType'])
        callees1 = ast.literal_eval(db1['callees'])
        callers1 = ast.literal_eval(db1['callers'])

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(similarity, i, j, pcodes1, func_features1, paramType1, callees1, callers1,
                                       call_graph_threshold) for j in
                       range(len(sample_files)) if (j, i) not in score_dict.keys()]

            for f in concurrent.futures.as_completed(results):
                overlap, k = f.result()
                score_dict[i, k] = overlap
        if i % 1000 == 0:
            print(i)

    print(f'Writing Result...')
    f = open('test_results/similarity_matrix', 'wb')  # save the matrix file
    pickle.dump((score_dict, family_name), f)
    f.close()

