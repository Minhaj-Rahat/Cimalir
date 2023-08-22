#import similarity_helper_debug as sh
#import final_similarityV2 as fs

import similarity_helper_analysis as sh
import final_similarityV2_analysis as fs
import call_graph_hash as cgh
import call_graph_analyze as cga

import json
import ast

def sim_func(jaccard_threshold, similarity_score, similarity_weight , threshold, file1,file2):
    f1 = open(file1, 'r')
    db1 = json.load(f1)
    f1.close()
    pcodes1 = ast.literal_eval(db1['pcode'])
    func_features1 = ast.literal_eval(db1['func_features'])
    paramType1 = ast.literal_eval(db1['paramType'])
    callees1 = ast.literal_eval(db1['callees'])
    callers1 = ast.literal_eval(db1['callers'])

    f2 = open(file2, 'r')
    db2 = json.load(f2)
    f2.close()
    pcodes2 = ast.literal_eval(db2['pcode'])
    func_features2 = ast.literal_eval(db2['func_features'])
    paramType2 = ast.literal_eval(db2['paramType'])
    callees2 = ast.literal_eval(db2['callees'])
    callers2 = ast.literal_eval(db2['callers'])

    #hash_perm =  100
    #print(jaccard_threshold, similarity_weight, similarity_weight[2], similarity_score)
    similar_funcs, ambiguous = sh.func_similarity(pcodes1, func_features1, paramType1,
                                                  pcodes2, func_features2, paramType2,
                                                  jaccard_threshold, similarity_weight,
                                                  similarity_weight[2], similarity_score)

    final_sims = cga.call_graph_jaccard(similar_funcs, pcodes1, pcodes2, callers1, callers2, callees1, callees2,
                                        threshold=threshold)
    final_sims_ambig, ambigs = cga.call_graph_jacard_ambiguous(ambiguous, pcodes1, pcodes2, callers1, callers2,
                                                               callees1,
                                                               callees2, threshold=threshold)

    sims_combine = {**final_sims, **final_sims_ambig}

    sims_combine = cga.remove_repetitive_entry(sims_combine)
    overlap = len(sims_combine) / max(len(list(pcodes1.keys())), len(list(pcodes2.keys())))
    return overlap
