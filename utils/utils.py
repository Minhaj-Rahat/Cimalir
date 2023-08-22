'''
find_packed_binaries: function to find packed binaries
params :
source_files: files to scan [list]
move_filePath: move the packed files into this path for backup [filePath]
dest_filePath: save the unpacked file
match_string: the string to match inside binary
'''
def find_packed_binaries(source_files,move_filePath, dest_filePath, match_string='upx'):
    import regex_match_packer as rgm
    import subprocess
    import os
    import shutil



    isExist = os.path.exists(move_filePath)

    if not isExist:
        os.mkdir(move_filePath)

    isExist = os.path.exists(dest_filePath)
    if not isExist:
        os.mkdir(dest_filePath)


    for files in source_files:

        lines = []
        command = ['strings']
        unpack_command = ['upx', '-d', '-o']

        command.append(files)
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        for line in iter(process.stdout.readline, ""):
            lines.append(line)
        for line in iter(process.stderr.readline, ""):
            print(line)
        process.terminate()
        for line in lines:
            # find the matched sring for pack
            if rgm.find_string(match_string,line):

                isExist = os.path.exists(move_filePath+files.split('/')[-3]+files.split('/')[-2])
                if not isExist:
                    os.mkdir(move_filePath+files.split('/')[-3]+files.split('/')[-2])
                if not os.path.exists(move_filePath+files.split('/')[-3]+files.split('/')[-2]+files.split('/')[-1]):
                    shutil.copy(files, move_filePath + files.split('/')[-3]+files.split('/')[-2]+ files.split('/')[-1])



                unpack_command.append(dest_filePath+files.split('/')[-1])
                unpack_command.append(move_filePath+files.split('/')[-1])
                process = subprocess.Popen(unpack_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           text=True)
                for line in iter(process.stderr.readline, ""):
                    print(line)

                process.terminate()
                break


#create dict of yara regex features
def create_yara_dict(cube_db_files,source_path,yara_file_path,yara_string_dict,string_index,file_name):
    import pickle
    import subprocess

    yara_dict = {}



    f = open(cube_db_files, 'rb')
    samples_db = pickle.load(f)
    f.close()

    sample_binaries = []
    for i in samples_db:
        sample_binaries.append(source_path + '/' + i.split('/')[-2] + '/' + i.split('/')[-1].split('.')[0])

    for i in range(len(sample_binaries)):
        feature = [0,0,0,0,0,0,0,0,0,0,0]

        command = ['yara', '-s', yara_file_path, sample_binaries[i]]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        lines = []
        for line in iter(process.stdout.readline, ""):
            lines.append(line)

        # print(lines)
        strings = set()
        if len(lines) > 1:
            for j in range(1, len(lines)):
                strings.add(lines[j].split(':')[-1].split(' ')[1].split('\n')[0])



        for element in strings:
            if element in yara_string_dict:
                feature[string_index[element]] = yara_string_dict[element]

        yara_dict[i] = feature

    print('Writing....')
    f = open(file_name, 'wb')
    pickle.dump(yara_dict, f)
    f.close()

def create_yara_strings():

    yara_string_dict = {'/proc/net/route': 2, 'root': 3, 'NICK': 5, 'PING': 7, 'JOIN': 11, 'USER': 13,
                         'PRIVMSG': 17, '3AES':19,'Hacker':23,'VERSONEX':29,'sockprintf':31}  # string feature integer values 11
    string_index = {'/proc/net/route': 0, 'root': 1, 'NICK': 2, 'PING': 3, 'JOIN': 4, 'USER': 5,
                    'PRIVMSG': 6,'3AES':7,'Hacker':8,'VERSONEX':9,'sockprintf':10}  # index of string features, for keeping sequence

    return yara_string_dict, string_index