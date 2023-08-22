import json
import pandas as pd


# print(pcode_func_set)
# print(pcode_dict)
# print(pcode_dict['0x00008324'][0].split())
# print(pcode_dict['0x00008324'][0].split()[0][0])

def jaccard_score(A, B):
    if len(A.union(B)) == 0:
        return 0
    else:
        return len(A.intersection(B)) / len(A.union(B))


def pcode_set(pcode_dict):
    #pcode_dict = json.loads(open(file_name, 'r').read())

    func_address = list(pcode_dict.keys())
    pcode_func_set = {}
    for key in func_address:
        pcode_set = set()
        for i in range(len(pcode_dict[key])):
            if pcode_dict[key][i].split()[0][0] == '(':
                pcode_set.add(pcode_dict[key][i].split()[3])
            else:
                pcode_set.add(pcode_dict[key][i].split()[1])

        pcode_func_set[key] = pcode_set

    return pcode_func_set  #, pcode_dict

def pcode_set2(pcode_dict):

    func_address = list(pcode_dict.keys())
    pcode_func_set = {}
    for key in func_address:
        pcode_set = set()
        for i in range(len(pcode_dict[key])):
            if (pcode_dict[key][i].decode('utf-8')).split()[0][0] == '(':
                pcode_set.add(pcode_dict[key][i].decode('utf-8').split()[3])
            else:
                pcode_set.add(pcode_dict[key][i].decode('utf-8').split()[1])

        pcode_func_set[key] = pcode_set

    return pcode_func_set

def pcode_set_shingle(shingkles, func, pcode_dict):

    #pcode_set = set()
    sample_set = set()
    if len(pcode_dict[func]) < shingkles:
        for i in range(len(pcode_dict[func])):
            if pcode_dict[func][i].split()[0][0] == '(':
                #pcode_set.add(binascii.crc32(pcode_dict[func][i].split()[3].encode('ascii')) & 0xffffffff)
                sample_set.add(pcode_dict[func][i].split()[3])
            else:
                #pcode_set.add(binascii.crc32(pcode_dict[func][i].split()[1].encode('ascii')) & 0xffffffff)
                sample_set.add(pcode_dict[func][i].split()[1])
    else:
        for i in range(len(pcode_dict[func]) - shingkles - 1):
            pcode_shingle = ''
            for j in range(shingkles):
                if pcode_dict[func][i + j].split()[0][0] == '(':
                    if j == 0:
                        pcode_shingle += pcode_dict[func][i + j].split()[3]
                    else:
                        pcode_shingle += ' ' + pcode_dict[func][i + j].split()[3]
                else:
                    if j == 0:
                        pcode_shingle += pcode_dict[func][i + j].split()[1]
                    else:
                        pcode_shingle += ' ' + pcode_dict[func][i + j].split()[1]

            #pcode_set.add(binascii.crc32(pcode_shingle.encode('ascii')) & 0xffffffff)
            sample_set.add(pcode_shingle)
    return sample_set


def count_cBranch(pcode_dict):
    func_address = list(pcode_dict.keys())
    cbranch_func_set = {}
    for key in func_address:
        pcode_set = set()
        count = 0
        for i in range(len(pcode_dict[key])):
            if (pcode_dict[key][i].decode('utf-8')).split()[0][0] != '(':
                if (pcode_dict[key][i].decode('utf-8')).split()[1] == 'CBRANCH':
                    count += 1
        cbranch_func_set[key] = count
    return cbranch_func_set


'''
file_name1 = 'sample_pcode/malwarePcode/backdoor1_binpcodes.yaml'
setA, dict1 = pcode_set(file_name1)
file_name2 = 'sample_pcode/malwarePcode/mirai1_binpcodes.yaml'
setB, dict2 = pcode_set(file_name2)
#print(jaccard_score(set1,set2))

l = [i for i in list(dict2.keys())]
ll = ['funcA']+l

df = pd.DataFrame(columns=ll)

count = 0
for i in list(dict1.keys()):
    set1 = setA[i]
    list_func = {}
    for j in list(dict2.keys()):
        list_func[j] = jaccard_score(set1, setB[j])
        #print(f'i: {i} set1: {setA[i]}, j: {j}: {setB[j]}')

    lis_v = [i]+[p for p in list(list_func.values())]
    df.loc[count] = lis_v
    count+=1

#with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #print(df)

#df.to_csv('sample_pcode/malwarePcode/out_b1_m1.csv', index=False)
print(df)
'''
