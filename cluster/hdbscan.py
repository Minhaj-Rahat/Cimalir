import pickle

import numpy as np


def _load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def _build_similarity_block(similarity_dict, n):
    """Densify `similarity_dict` into an n x n matrix.

    For each (i, j), uses the score under (i, j) if present, otherwise (j, i).
    """
    mat = np.zeros((n, n))
    for (i, j), v in similarity_dict.items():
        if i < n and j < n:
            mat[i, j] = v
            if mat[j, i] == 0:
                mat[j, i] = v
    return mat


def merge_yara_similarity(sim_mat_file, yara_dict_file, sample_length, string_feature_length):
    similarity_dict_combined, _ = _load_pickle(sim_mat_file)
    yara_dict = _load_pickle(yara_dict_file)

    final = np.zeros((sample_length, sample_length + string_feature_length))
    final[:, :sample_length] = _build_similarity_block(similarity_dict_combined, sample_length)
    if string_feature_length:
        for i in range(sample_length):
            final[i, sample_length:sample_length + string_feature_length] = yara_dict[i]
    return final


def merge_yara_similarity2(sim_mat_file, yara_dict_file, sample_length, string_feature_length):
    """Variant that omits the yara block."""
    similarity_dict_combined, _ = _load_pickle(sim_mat_file)
    final = np.zeros((sample_length, sample_length + string_feature_length))
    final[:, :sample_length] = _build_similarity_block(similarity_dict_combined, sample_length)
    return final


def hdbscan_cluster(yara_file, sim_mat, min_cluster_size=45, min_samples=20):
    from collections import Counter
    import hdbscan

    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples,
                                cluster_selection_method='eom', metric='euclidean',
                                gen_min_span_tree=True)

    mat = merge_main(yara_file, sim_mat)
    cl = clusterer.fit(mat)
    labels1 = cl.labels_
    dbcv = cl.relative_validity_

    _, family_name1 = _load_pickle('test_results/similarity_matrix')

    families = ('ddos', 'gafgyt', 'tsunami', 'hajime', 'dofloo', 'mirai')
    family1 = {fam: [] for fam in families}
    for fam, label in zip(family_name1, labels1):
        family1[fam].append(label)

    result_dict1 = {fam: dict(Counter(labels)) for fam, labels in family1.items()}
    print(result_dict1)
    print(f'DVCV Index:{dbcv}')

    family_dict = {'gafgyt': 0, 'tsunami': 1, 'ddos': 2, 'mirai': 3, 'hajime': 4, 'dofloo': 5}
    true_label = [family_dict[name] for name in family_name1]

    cluster_analyze(true_label, labels1, mat)


def hdbscan_optimal(yara_file, sim_mat):
    import hdbscan

    mat = merge_main(yara_file, sim_mat)

    best_score = 0
    best_parameters = None

    for min_cluster_size in (3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80):
        for min_samples in (3, 5, 10, 20, 30, 40, 45, 50, 55, 60, 65, 70, 80, 85):
            for cluster_selection_method in ('eom', 'leaf'):
                for metric in ('euclidean',):
                    hdb = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size,
                                          min_samples=min_samples,
                                          cluster_selection_method=cluster_selection_method,
                                          metric=metric, gen_min_span_tree=True).fit(mat)
                    score = hdb.relative_validity_
                    if score > best_score:
                        best_score = score
                        best_parameters = {'min_cluster_size': min_cluster_size,
                                           ' min_samples': min_samples,
                                           'cluster_selection_method': cluster_selection_method,
                                           'metric': metric}

    print("Best DBCV score: {:.3f}".format(best_score))
    print("Best parameters: {}".format(best_parameters))


def merge_main(yara_file, sim_mat_file):
    return merge_yara_similarity(sim_mat_file, yara_file, sample_length=1000, string_feature_length=11)


def merge_main2(yara_file, sim_mat_file):
    return merge_yara_similarity2(sim_mat_file, yara_file, sample_length=1000, string_feature_length=0)


def cluster_analyze(true_labels, pred_labels, mat):
    from sklearn import metrics

    print(f"Homogeneity: {metrics.homogeneity_score(true_labels, pred_labels):.3f}")
    print(f"Completeness: {metrics.completeness_score(true_labels, pred_labels):.3f}")
    print(f"V-measure: {metrics.v_measure_score(true_labels, pred_labels):.3f}")
    print(f"Adjusted Mutual Information: {metrics.adjusted_mutual_info_score(true_labels, pred_labels):.3f}")
    print(f"Calinski Harabasz Score: {metrics.calinski_harabasz_score(mat, pred_labels):.3f}")
    print(f"Silhouette Score: {metrics.silhouette_score(mat, pred_labels):.3f}")
