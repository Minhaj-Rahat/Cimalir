import json
import os.path


def get_high_function(func,monitor,ifc):

    res = ifc.decompileFunction(func, 60, monitor)
    high = res.getHighFunction()
    return high

def create_pcode_dict(high_func):
    optList = []
    opiter = high_func.getPcodeOps()
    while opiter.hasNext():
        op = opiter.next()
        optList.append(op.toString().encode('ascii', 'ignore'))
    return optList

def getAddress(offset, currentProgram):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)

def extract_pcode(currentProgram,monitor,ifc):
    listing = currentProgram.getListing()
    m = currentProgram.getFunctionManager()
    funcs = m.getFunctions(True)
    function_list = ['0x' + str(func.getEntryPoint()) for func in funcs]


    pcode_dict = {}
    for i in function_list:
        func = listing.getFunctionContaining(getAddress(i, currentProgram))
        hf = get_high_function(func,monitor,ifc)
        pcode_dict[i] = create_pcode_dict(hf)

    return pcode_dict

def jaccard_score(A, B):
    if len(A.union(B)) == 0:
        return 0
    else:
        return len(A.intersection(B)) / len(A.union(B))


def pcode_set(file_name):
    pcode_dict = json.loads(open(file_name, 'r').read())

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

    return pcode_func_set, pcode_dict

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

def func_feature(monitor, currentProgram, ifc):

    # function features dictionary
    func_features = {}

    # paramType dictionary
    paramType = {}

    # callers and callee dictionary
    callees = {}
    callers = {}



    func_address = list(pcodeDict.keys())

    func_manager = currentProgram.getFunctionManager()





    # cbracnh for all functions
    cbranch_dict = count_cBranch(pcodeDict)



    for address in func_address:
        features = []
        addr = toAddr(address)
        fn = func_manager.getFunctionContaining(addr)
        callers_l = list(fn.getCalledFunctions(monitor)) #function it is calling
        callees_l = list(fn.getCallingFunctions(monitor)) #functions calling it
        #print(f'Functions:{fn}')
        #print(f'callees:{callees_l}')
        callees_l = ['0x'+str(i.getEntryPoint()) for i in callees_l]
        #print(f'callees:{callees_l}')
        callers_l = ['0x' + str(i.getEntryPoint()) for i in callers_l]

        callees[address] = callees_l
        callers[address] = callers_l

        features.append(len(callees_l))
        features.append(len(callers_l))

        res = ifc.decompileFunction(fn, 60, monitor)
        high = res.getHighFunction()
        lsm = high.getLocalSymbolMap()
        symbols = lsm.getSymbols()

        paramCount = 0

        paramtype = []
        for i, s in enumerate(symbols):
            # if 'param' in s.name:

            if s.parameter:
                paramtype.append(str(s.dataType))
                paramCount += 1

        features.append(paramCount)
        features.append(cbranch_dict[address])

        func_features[address] = features
        paramType[address] = paramtype

    return func_features, paramType, callees, callers




from ghidra.util.task import ConsoleTaskMonitor
from ghidra.app.decompiler import DecompileOptions
from ghidra.app.decompiler import DecompInterface

program = getCurrentProgram()
options = DecompileOptions()
monitor = ConsoleTaskMonitor()
ifc = DecompInterface()
ifc.setOptions(options)
ifc.openProgram(program)

# extract pcodes
pcodeDict = extract_pcode(program,monitor,ifc)
func_features, paramType, callees, callers = func_feature(monitor, currentProgram, ifc)
#dump db
db={}
db['func_features'] = str(func_features)
db['paramType'] = str(paramType)
db['callees'] = str(callees)
db['callers'] = str(callers)
db['pcode'] = str(pcodeDict)

pathSave = '/home/usr/crs_plt_cluster/unpackedTuneDB/' # define the path, change the usr name [unpackedTuneDB]
isExist = os.path.exists(pathSave)
if not isExist:
    os.makedirs(pathSave)
f = open(pathSave+getProgramFile().getName().split('/')[-1] + '.json', 'w')
json.dump(db, f)
f.close()
