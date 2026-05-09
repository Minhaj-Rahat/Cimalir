'''
find_packed_binaries: function to find packed binaries
params :
source_files: files to scan [list]
move_filePath: move the packed files into this path for backup [filePath]
dest_filePath: save the unpacked file
match_string: the string to match inside binary
'''
import os
import pickle
import shutil
import subprocess

import regex_match_packer as rgm


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _strings_output(file_path):
    """Capture text output of `strings <file_path>`."""
    proc = subprocess.run(['strings', file_path], capture_output=True, text=True)
    if proc.stderr:
        print(proc.stderr, end='')
    return proc.stdout.splitlines()


def find_packed_binaries(source_files, move_filePath, dest_filePath, match_string='upx'):
    """Move packed binaries to backup, then unpack to `dest_filePath`."""
    _ensure_dir(move_filePath)
    _ensure_dir(dest_filePath)

    for src in source_files:
        parts = src.split('/')
        bucket = parts[-3] + parts[-2]
        name = parts[-1]

        for line in _strings_output(src):
            if not rgm.find_string(match_string, line):
                continue

            backup_dir = move_filePath + bucket
            _ensure_dir(backup_dir)
            backup_path = backup_dir + name
            if not os.path.exists(backup_path):
                shutil.copy(src, move_filePath + bucket + name)

            unpack_command = ['upx', '-d', '-o',
                              dest_filePath + name,
                              move_filePath + name]
            proc = subprocess.run(unpack_command, capture_output=True, text=True)
            if proc.stderr:
                print(proc.stderr, end='')
            break


def create_yara_dict(cube_db_files, source_path, yara_file_path,
                     yara_string_dict, string_index, file_name):
    with open(cube_db_files, 'rb') as f:
        samples_db = pickle.load(f)

    sample_binaries = [
        source_path + '/' + i.split('/')[-2] + '/' + i.split('/')[-1].split('.')[0]
        for i in samples_db
    ]

    feature_size = len(string_index)
    yara_dict = {}
    for i, binary in enumerate(sample_binaries):
        feature = [0] * feature_size

        proc = subprocess.run(['yara', '-s', yara_file_path, binary],
                              capture_output=True, text=True)
        lines = proc.stdout.splitlines()

        strings = set()
        for line in lines[1:]:
            try:
                strings.add(line.split(':')[-1].split(' ')[1])
            except IndexError:
                continue

        for element in strings:
            if element in yara_string_dict:
                feature[string_index[element]] = yara_string_dict[element]

        yara_dict[i] = feature

    print('Writing....')
    with open(file_name, 'wb') as f:
        pickle.dump(yara_dict, f)


def create_yara_strings():
    yara_string_dict = {'/proc/net/route': 2, 'root': 3, 'NICK': 5, 'PING': 7,
                        'JOIN': 11, 'USER': 13, 'PRIVMSG': 17, '3AES': 19,
                        'Hacker': 23, 'VERSONEX': 29, 'sockprintf': 31}
    string_index = {key: i for i, key in enumerate(yara_string_dict)}
    return yara_string_dict, string_index
