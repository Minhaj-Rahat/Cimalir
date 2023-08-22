import numpy as np
import pickle


# merge yara dict and similarity matrix
def merge_yara_similarity(sim_mat_file,yara_dict_file, sample_length, string_feature_length):
    f_combine = open(sim_mat_file, 'rb')
    similarity_dict_combined, _ = pickle.load(f_combine)   # the file contains similartiy dict and family name
    f_combine.close()

    f_yara = open(yara_dict_file, 'rb')
    yara_dict = pickle.load(f_yara)
    f_yara.close()

    #final_feature_mat = np.zeros((sample_length+string_feature_length,sample_length+string_feature_length))
    final_feature_mat = np.zeros((sample_length , sample_length + string_feature_length))
    for i in range(sample_length):
        for j in range(sample_length):
            if (i,j) in similarity_dict_combined.keys():
                final_feature_mat[i, j] = similarity_dict_combined[(i, j)] #* 100
            else:
                final_feature_mat[i, j] = similarity_dict_combined[(j, i)] #* 100


    for i in range(sample_length):
        final_feature_mat[i, sample_length:sample_length+string_feature_length] = yara_dict[i]


    return final_feature_mat

def merge_yara_similarity2(sim_mat_file,yara_dict_file, sample_length, string_feature_length):
    f_combine = open(sim_mat_file, 'rb')
    similarity_dict_combined, _ = pickle.load(f_combine)   # the file contains similartiy dict and family name
    f_combine.close()

    f_yara = open(yara_dict_file, 'rb')
    yara_dict = pickle.load(f_yara)
    f_yara.close()

    final_feature_mat = np.zeros((sample_length,sample_length+string_feature_length))

    for i in range(sample_length):
        for j in range(sample_length):
            if (i,j) in similarity_dict_combined.keys():
                final_feature_mat[i, j] = similarity_dict_combined[(i, j)] #* 100
            else:
                final_feature_mat[i, j] = similarity_dict_combined[(j, i)] #* 100


    #for i in range(sample_length):
        #final_feature_mat[i, sample_length:sample_length+string_feature_length] = yara_dict[i]


    return final_feature_mat



def hdbscan_cluster(yara_file,sim_mat, min_cluster_size=45,min_samples=20):
    from collections import Counter
    import hdbscan

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, cluster_selection_method='eom', metric='euclidean',gen_min_span_tree=True) # current paper

    mat = merge_main(yara_file,sim_mat) # current paper
    #mat = merge_main2(yara_file) # without call, without strings

    #mat = merge_main2(yara_file) # without strings

    cl = clusterer.fit(mat)

    labels1 = cl.labels_
    dbcv = cl.relative_validity_


    result_file1 = 'test_results/similarity_matrix'  # similarity matrix file

    # loading scores
    f1 = open(result_file1, 'rb')
    _, family_name1 = pickle.load(f1)


    family1 = {}

    family1['ddos'] = []
    family1['gafgyt'] = []
    family1['tsunami'] = []
    family1['hajime'] = []
    family1['dofloo'] = []
    family1['mirai'] = []


    result_dict1 = {}


    for i in range(len(family_name1)):
        family1[family_name1[i]].append(labels1[i])



    for key in list(family1.keys()):
        result_dict1[key] = dict(Counter(family1[key]))
    print(result_dict1)

    print(f'DVCV Index:{dbcv}')



    family_dict = {'gafgyt':0,'tsunami':1,'ddos':2,'mirai':3,'hajime':4,'dofloo':5}

    true_label = []

    for i in range(len(family_name1)):
        true_label.append(family_dict[family_name1[i]])

    cluster_analyze(true_label, labels1, mat)



def hdbscan_optimal(yara_file, sim_mat):
    import hdbscan


    mat = merge_main(yara_file,sim_mat) # ours, current

    #mat = merge_main2(yara_file) # without string features and without call


    best_score = 0

    for min_cluster_size in [3, 5,10, 15, 20, 25, 30, 35, 40, 45,50, 55, 60, 65, 70, 75, 80]:
        for min_samples in [3,5,10,20,30, 40, 45, 50, 55, 60,65,70,80,85]:
            for cluster_selection_method in ['eom', 'leaf']:
                for metric in ['euclidean']:
                    # for each combination of parameters of hdbscan
                    hdb = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples,
                                          cluster_selection_method=cluster_selection_method, metric=metric,
                                          gen_min_span_tree=True).fit(mat)
                    # DBCV score
                    score = hdb.relative_validity_
                    # if we got a better DBCV, store it and the parameters
                    if score > best_score:
                        best_score = score
                        best_parameters = {'min_cluster_size': min_cluster_size,
                                           ' min_samples': min_samples,
                                           'cluster_selection_method': cluster_selection_method,
                                           'metric': metric}

    print("Best DBCV score: {:.3f}".format(best_score))
    print("Best parameters: {}".format(best_parameters))


def merge_main(yara_file, sim_mat_file):

    # sim_mat_file = 'test_results/similarity_matrix' # current paper


    yara_dict_file = yara_file
    sample_length = 1000
    string_length = 11

    s = merge_yara_similarity(sim_mat_file, yara_dict_file, sample_length, string_length)
    return s

# without string features and without call
def merge_main2(yara_file,sim_mat_file):


    #sim_mat_file = 'test_results/similarity_matrix' # current system 1000 samples



    yara_dict_file = yara_file #current system 1000 samples
    sample_length = 1000
    string_length = 0

    s = merge_yara_similarity2(sim_mat_file, yara_dict_file, sample_length, string_length)
    return s


def cluster_analyze(true_labels, pred_labels, mat):
    from sklearn import metrics

    print(f"Homogeneity: {metrics.homogeneity_score(true_labels, pred_labels):.3f}")
    print(f"Completeness: {metrics.completeness_score(true_labels, pred_labels):.3f}")
    print(f"V-measure: {metrics.v_measure_score(true_labels, pred_labels):.3f}")
    print(
        "Adjusted Mutual Information:"
        f" {metrics.adjusted_mutual_info_score(true_labels, pred_labels):.3f}"
    )


    print("Calinski Harabasz Score:"
          f" {metrics.calinski_harabasz_score(mat, pred_labels):.3f}")

    print("Silhouette Score:"
          f" {metrics.silhouette_score(mat, pred_labels):.3f}")


# Best DBCV score: 0.748
# Best parameters: {'min_cluster_size': 45, ' min_samples': 20, 'cluster_selection_method': 'eom', 'metric': 'euclidean'} main system
# Best parameters: {'min_cluster_size': 35, ' min_samples': 10, 'cluster_selection_method': 'eom', 'metric': 'euclidean'}  without strings, with call
# Best parameters: {'min_cluster_size': 3, ' min_samples': 3, 'cluster_selection_method': 'eom', 'metric': 'euclidean'} without call
