import subprocess
import os
import pickle
import glob

import concurrent.futures
'''create_sim_mat_bindiff : create similarity matrix for bindiff
params:
      database: path to the database folder containing json files previously created
      class_folder: path to the ida pro export'''
def create_sim_mat_bindiff(database,class_folder):

    def similarityBin(i, j, f1, f2):
        command = ['bindiff', f1, f2]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        lines = []
        for line in iter(process.stdout.readline, ""):
            lines.append(line)


        return float(lines[-2].split(':')[1].split('%')[0]) / 100, j



    get_files = lambda path: (os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files)


    family_name = []
    sample_files = []

    for name in get_files(class_folder):
        if os.path.exists(database + name.split('/')[-2] + '/' +
                          name.split('/')[-1].split('.')[0] + '.json'):
            family_name.append(name.split('/')[-2])
            sample_files.append(name)

    print(len(sample_files))
    score_dict = {}


    save_dir = "test_results/similarity_matrix_bin"  # the file that will contain the sim matrix

    print(len(sample_files))

    for i in range(len(sample_files)):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = [executor.submit(similarityBin, i, j, sample_files[i], sample_files[j]) for j
                       in range(len(sample_files)) if (j, i) not in score_dict.keys()]

            for f in concurrent.futures.as_completed(results):
                overlap, k = f.result()
                score_dict[i, k] = overlap


        fil = glob.glob("*.BinDiff")
        print(len(fil))
        for file in fil:
            os.remove(file)


    print(f'Writing Result...')
    f = open(save_dir, 'wb')
    pickle.dump((score_dict, family_name), f)
    f.close()