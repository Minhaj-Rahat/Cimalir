# ghidra import sample and run script for database
import subprocess
import os

os.system('cmd /k "date"')


def import_headless(ghidra_folder,
                    project_folder,
                    projectName, samples,
                    postScript):
    isExist = project_folder
    if not isExist:
        os.mkdir(project_folder)

    subprocess.call(
        [ghidra_folder, project_folder,
         projectName,
         '-import',
         samples, '-recursive', '-postscript',
         postScript])

