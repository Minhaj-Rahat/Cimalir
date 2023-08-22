import os
import subprocess

'''export_ida: Export the binaries from IDA Pro using BinExport

Parameters:
    data_dir: path to the dataset
    dest_folder: where we want to save the exports, e.g. export/'''
def export_ida(data_dir, dest_folder):

    ida_exec = "/opt/idapro-8.2/ida64 -A \"-OBinExportAutoAction:BinExportBinary\" "    # path to IDA Pro Executable
    op1 = "\"-OBinExportModule:"
    op2 = "\"-S/home/X/crs_plt_cluster/utils/mybinexport.idc\" "      # this file is in utils folder, put tohe full path name


    files = []

    get_files = lambda path: (os.path.join(root, file) for root, dirs, files in os.walk(path) for file in files)

    for name in get_files(data_dir):
        files.append(name)

    for file in files:
        if not (
        os.path.exists(dest_folder + file.split('/')[-3] + '/' +
                       file.split('/')[-2] + '/')):
            os.makedirs(dest_folder + file.split('/')[-3] + '/' +
                        file.split('/')[-2] + '/')

        if not (os.path.exists(
                dest_folder + file.split('/')[-3] + '/' +
                file.split('/')[
                    -2] + "/" + file.split('/')[-1] + ".BinExport")):
            process = subprocess.call(["/opt/idapro-8.2/ida64", "-B", file])
            command = ida_exec + op1 + dest_folder + file.split('/')[-3] + '/' + file.split('/')[-2] + "\" " + op2 + "\"" + file + ".i64\""
            os.system(command)