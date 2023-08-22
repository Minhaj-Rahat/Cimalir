# entry to the project  todo need to finish and polish

class MalAnalyzer():

    def __init__(self, ghidra_folder):
        self.ghidra_folder = ghidra_folder # ghidra headless analyzer directory




    '''ghidra_import -- import sample files into ghidra and run postcript for processing and creating JSON database
    params:
    # samples_import--- samples for files to import, example: cube_maliot_labeled1000_2/* 
    # project_folder -- ghidra project folder
    # project_name -- ghidra project name
    # postScript -- post script used to process imported files
    Note: in postScript define the path where the database JSON files will be saved, these will be used later fr similarity analysis
    '''
    def ghidra_import(self, project_folder,project_name,samples_import, postScript='preprocess/fast_feature_dump.py'):
        from preprocess import cube_maliot_headless_import as cbh

        cbh.import_headless(self.ghidra_folder,project_folder, project_name, samples_import,postScript)





    '''Check whether any sample in the datatbase contains P-Code of length 0 (due to Ghidra not able to dump any P-code for the sample)
    Note: remove those with zero P-Code length'''
    def check_pcode_length(self,database_folder):
        import os
        import json
        import ast

        get_files = lambda path: (os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files)

        for files in get_files(database_folder):
            f = open(files, 'r')
            db = json.load(f)
            f.close()
            pcodes = ast.literal_eval(db['pcode'])

            if len(pcodes)==0:
                print(files)





    '''check_upx_packer: function to find packed binaries
    params :
    source_files: files to scan [list]
    move_filePath: move the packed files into this path [filePath]
    dest_filePath: save the unpacked file
    match_string: the string to match inside binary
    '''
    def check_upx_packer(self,source_file,move_filePath,dest_filePath):
        from utils import utils
        utils.find_packed_binaries(source_file,move_filePath,dest_filePath,match_string='upx')





    '''create_similarity_matrix: Create the similarity matrix for clustering
        params:
        databse_folder: path to the database folder
        Note: the optimal params are hard coded here. Use optimize_ga to find the optimal params
            '''
    def create_similarity_matrix(self, database_folder):
        from similarity_analysis import create_similarity_matrix
        create_similarity_matrix.create_sim_mat(database_folder)





    '''optimize_ga: optimiation for the parameters
    Note: Change the parameters inside ga_pymoo for customization
    '''
    def optimize_ga(self):
        # genetic algorithm impementing sum as fitness function
        from optimizer import ga_pymoo
        ga_pymoo.optimize()




    '''ida_export_bindiff: Export the binaries from IDA Pro using BinExport

    Parameters:
       datapath: path to the dataset
       destpath: where we want to save the exports, e.g. export/'''
    def ida_export_bindiff(self, datapath, destpath):
        from preprocess import ida_export

        ida_export.export_ida(datapath, destpath)





    '''similarity_matrix_bindiff : create similarity matrix for bindiff
    params:
      database: path to the database folder containing json files previously created
      class_folder: path to the ida pro export'''
    def similarity_matrix_bindiff(self,database,class_folder):
        from similarity_analysis import create_similarity_matrix_bindiff

        create_similarity_matrix_bindiff.create_sim_mat_bindiff(database,class_folder)




    '''create_yara_dict: Create String Features
    params:
    database_files : list of database json file name
    source_path: path to binaries
    yara_file_path: path to yara rules
    file_name: string feature file name where the features will be saved
    '''
    def create_yara_dict(self,database_files,source_path,yara_file_path,file_name):
        from utils import utils
        yara_string_dict, string_index = utils.create_yara_strings()

        utils.create_yara_dict(database_files, source_path, yara_file_path, yara_string_dict, string_index, file_name)





    '''hdbscan_optimal: find optimal params for hdbscan
    params:
          system: ours = 1 and bindiff = 2
          yara_file: yara dict file previouly created
                   currently we have two yara_files one for our system: 'test_results/yara_dict'
                   and another one for bindiff: 'test_results/yara_dict_bindiff'
          sim_mat: similarity matrix file previously created
          '''
    def hdbscan_optimal(self,system, yara_file, sim_mat):
        if system==1:
            from cluster import hdbscan
            hdbscan.hdbscan_optimal(yara_file,sim_mat)

        elif system==2:
            from cluster import hdbscan_bindiff
            hdbscan_bindiff.hdbscan_optimal(yara_file, sim_mat)





    '''cluster : cluster and analyze cluster performance
        params:
              system: ours = 1 and bindiff = 2
              yara_file: yara dict file previouly created
                       currently we have two yara_files one for our system: 'test_results/yara_dict'
                       and another one for bindiff: 'test_results/yara_dict_bindiff'
            
            sim_mat: similarity matrix file previously created
                       
             min_cluster_size_ours,min_samples_ours: optimal params found for our system
            min_cluster_size_bindiff, min_samples_bindiff: optimal params fund for bindiff
              '''

    def cluster(self,system,yara_file,sim_mat, min_cluster_size_ours,min_samples_ours, min_cluster_size_bindiff, min_samples_bindiff):
        if system==1:
            from cluster import hdbscan
            hdbscan.hdbscan_cluster(yara_file,sim_mat,min_cluster_size_ours,min_samples_ours)

        elif system==2:
            from cluster import hdbscan_bindiff
            hdbscan_bindiff.hdbscan_cluster(sim_mat)





