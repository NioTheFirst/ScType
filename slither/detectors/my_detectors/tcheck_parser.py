#USAGE: parses the type file for:
#       - [*c], contract_name :contracts to run
#       - [xf], function_name :functions to ignore
#       - [sef], contract_name, function_name, [num_types], [denom_types], expected_normalization :external function summary
#       - [tref], array/map_name :expected type for one instance to be tested for the array/mapping
#       - [t], function_name, variable_name, [num_types], [denom_types], normalization :type information for a specific variable (usually parameters)
#
#
#FUNCTION SUMMARY:
#       -parse_type_file(file_name) :given a type file, check for existence and parses
#       -
#       -get_var_type_tuple(function_name, var_name) :check for existence and returns type tuple for a variable
#       -get_func_type_tuple(contract_name, function_name, [parameters]) :check for existence and returns type tuple for an external function call
#       -get_ref_type_tuple(ref_name) :check for existence and returns type tuple for a reference (arrays or maps)
import address_handler
from address_handler import address_to_label, label_sets
from slither.sctype_cf_pairs import get_cf_pairh, view_all_cf_pairs

#address_to_label = {}
#label_sets = {}
allowed_contracts = {}
barred_functions = {}
var_type_hash = {}   #Exclusively for types/normalizations
var_fin_hash = {}    #Exclusively for finance types
in_func_ptr_hash = {}
ex_func_type_hash = {}
ref_type_hash = {}
address_type_hash = {}
tuple_type_hash = {}
field_type_hash = {}
spex_func_type_hash = {}
MAX_PARAMETERS = 5
contract_name_aliases = {}


read_files = {}
reuse_types = True
reuse_types_var = {}
reuse_addr = True
reuse_addr_types = {}
reuse_fin = True
reuse_fin_types = {}

total_annotations = 0
field_tuple_start = 5
update_start = 100

#Update ratios should be reset every single contract
update_ratios = {10: -1, 
                 12: -1,
                 20: -1,
                 21: -1}

f_type_num = {
    -1: "undef",
    0: "raw balance",
    1: "net balance",
    2: "accrued balance",
    3: "final balance",
    10: "compound fee ratio (t)",
    11: "transaction fee",  
    12: "simple fee ratio",
    13: "transaction fee (n)",
    14: "transaction fee (d)",
    20: "simple interest ratio",
    21: "compound interest ratio",
    22: "simple interest",
    23: "compound interest",
    30: "reserve",
    40: "price/exchange rate",
    50: "debt",
    60: "dividend"
}

f_type_name = {
    "undef" : -1,
    "raw balance" :0,
    "net balance" :1,
    "accrued balance" :2,
    "final balance" :3,
    "compound fee ratio (t)" : 10,
    "transaction fee" :11,
    "simple fee ratio" : 12,
    "transaction fee (n)" : 13,
    "transaction fee (d)" : 14,
    "simple interest ratio" : 20,
    "compound interest ratio" : 21,
    "simple interest": 22,
    "compound interest" : 23,
    "reserve" : 30,
    "price/exchange rate" : 40,
    "debt": 50,
    "dividend": 60
}

def get_total_annotations():
    global total_annotations
    return(total_annotations)

def gen_finance_instances(line):
    _line = line.split(",")
    finance_instances = []
    for param in _line:
        #print(f"Param: {param}")
        offset = 0
        foundf = False
        for i in range(len(param)):
            if(param[i] == 'f' and i+1 < len(param) and param[i+1] == ':'):
                foundf = True
                offset=i+2
                break
        if(foundf == False):
            continue
        isolated_param = param[offset:].replace("}", "").strip()
        #print(f"Isolated Param: {isolated_param}")
        f_res = None
        try:
            temp = int(isolated_param)
            f_res = temp
        except ValueError:
            if isolated_param in f_type_name:
                f_res = f_type_name[isolated_param]
            else:
                f_res = -1
        #if not isinstance(f_res, int):
            #print("[x] FINANCE TYPE IS NOT INT")
        finance_instances.append(f_res)
        #print(f"F num: {f_res}")
    return finance_instances


def parse_finance_file(f_file):
    global read_files
    global total_annotations
    global reuse_fin
    global reuse_fin_types
    #Same structure as token_type parser
    if(f_file == None):
        return
    with open(f_file, 'r') as finance_file:
        #print("Reading f file...")
        for line in finance_file:
            _line = split_line(line)
            #Look for "f: "
            f_params = gen_finance_instances(line)
            #print(_line)
            if(len(f_params) == 0):
                #No finance parameters, assume all parameters are NULL Type
                for i in range(MAX_PARAMETERS):
                    f_params.append(-1)
            #Regular variables
            if(_line[0].strip() == "[t]"):
                if(not(f_file) in read_files):
                    #print(_line)
                    total_annotations+=1
                f_name = _line[1].strip()
                v_name = _line[2].strip()
                if(reuse_fin and not(v_name in reuse_fin_types)):
                    reuse_fin_types[v_name] = f_params[0]
                norm_tt = get_var_type_tuple(f_name, v_name)
                if(norm_tt == None):
                    #Create new "variable" to be propogated by tcheck.querry_type()
                    add_var(f_name, v_name, (-1, -1, 'u', None, 'u', f_params[0]))
                else:
                    norm_tt+=(f_params[0], )
                    add_var(f_name, v_name, norm_tt)
                
            elif(_line[0].strip() == "[ta]"):
                #addresses
                if(not(f_file) in read_files):
                    total_annotations+=1
                    #print(_line)
                f_name = _line[1].strip()
                v_name = _line[2].strip()
                if(reuse_fin and not(v_name in reuse_fin_types)):
                    reuse_fin_types[v_name] = f_params[0]
                addr_key = f_name + ":" + v_name
                addr = None
                if(addr_key in label_sets):
                    addr = label_sets[addr_key]
                    addr.finance_type = f_params[0]
                else:
                    if(f_name == "global"):
                        addr = address_handler.type_file_new_address(addr_key, True)
                    else:
                        addr = address_handler.type_file_new_address(addr_key, False)
                    addr.finance_type = f_params[0]
                #print(addr)
            elif(_line[0].strip() == "[sefa]"):
                c_name = _line[1].strip()
                f_name = _line[2].strip()
                ef_tts = get_dir_ex_func_type_tuple(c_name, f_name)
                if(ef_tts == None):
                    raise Exception("SEF object not initialized")
                cur = 0
                new_tts = []
                for tt in ef_tts:
                    tt+=(f_params[cur], )
                    new_tts.append(tt)
                    cur+=1
                add_ex_func(c_name, f_name, new_tts)
            #May be deprecated?
            elif(_line[0].strip() == "[tref]"):
                if(not(f_file) in read_files):
                    total_annotations+=1
                ref_name = _line[1].strip()
                ref_tt = get_ref_type_tuple(ref_name)
                ref_tt += (f_params[0], )
                add_ref(ref_name, ref_tt)
            
            elif(_line[0].strip() == "[t*]"):
                if(not(f_file) in read_files):
                    total_annotations+=1
                    #print(_line)
                f_name = _line[1].strip()
                p_name = _line[2].strip()
                v_name = _line[3].strip()
                field_tt = get_field(f_name, p_name, v_name)
                if(reuse_fin and not(v_name in reuse_fin_types)):
                    reuse_fin_types[v_name] = f_params[0]
                if(field_tt == None):
                    add_field(f_name, p_name, v_name, (-1, -1, 'u', 'u', 'u'))
                    field_tt = get_field(f_name, p_name, v_name)
                field_tt += (f_params[0], )
                add_field(f_name, p_name, v_name, field_tt)
    read_files[f_file] = True

def parse_type_file(t_file, f_file = None):
    global label_sets
    global reuse_addr
    global read_files
    global reuse_addr_types
    global total_annotations
    with open (t_file, 'r') as type_file:
        lines = []
        counter = 0
        temp_counter = 0
        for line in type_file:
            _line = split_line(line)
            #NORMAL INPUT
            #_line[0] = [t]
            #_line[1] = container
            #_line[2] = var name
            #_line[3] = numerator type (assume one)
            #_line[4] = denominator type (assume one)
            #_line[5] = normalization amt (power of 10)
            #_line[6] = (Optional) linked function if is address
            #print(line)
            if(_line[0].strip() == "[alias]"):
                #Alias for contract names
                if(not(t_file in read_files)):
                    total_annotations+=1
                used_name = _line[1].strip()
                actual_name = _line[2].strip()
                add_alias(used_name, actual_name)

            if(_line[0].strip() == "[t]"):
                if(not(t_file in read_files)):
                    total_annotations+=1
                    #print(_line)
                f_name = _line[1].strip()
                v_name = _line[2].strip()
                #TODO: Check for previous mentions of v_name
                if(reuse_types):
                    if(v_name in reuse_types_var):
                        add_var(f_name, v_name, get_var_type_tuple(f_name, v_name))

                try:
                    num = -1
                    den = -1
                    norm = 'u'
                    addr = 'u'
                    value = 'u'
                    if(len(_line) >= 6):
                        #Integers (and potentially f-types)
                        num = _line[3].strip()
                        den = _line[4].strip()
                        norm = int(_line[5].strip())
                        if(len(_line) >= 7):
                            try:
                                value = int(_line[6].strip())
                            except ValueError:
                                value = 'u'
                    elif(len(_line) >= 4):
                        #Addresses 
                        addr = _line[3].strip()
                        
                    add_var(f_name, v_name, (num, den, norm, value, addr))
                    if(reuse_types):
                        reuse_types_var[v_name] = True
                except ValueError:
                    print("Invalid Value read")
                continue
            #BAR FUNCTION
            #_line[0] = [xf]
            #_line[1] = function name
            if(_line[0].strip() == "[xf]"):
                f_name = _line[1].strip()
                bar_function(f_name)
                continue
            #ALLOW CONTRACT
            #_line[0] = [*c]
            #_line[1] = contract name
            if(_line[0].strip() == "[*c]"):
                c_name = _line[1].strip()
                allow_contract(c_name)
                continue
            #SUMMARY OF EXTERNAL FUNCTION (ADDRESS VERSION)
            #assuming global address
            #[sefa], contract_name, function_name
            #[sefa], contract_name, function_name, N, ({copy/transfer, isAddress, isField, ...}, ...)       
            #                                         ({copy/transfer, <Num, ...>, <Den, ...>, Norm, Value})
            #                                         ({copy/transfer, T, F, Address})
            #                                         ({}) -> assume basic integer null value
            if(_line[0].strip() == "[sefa]"):
                c_name = _line[1].strip()
                f_name = _line[2].strip()
                ef_types = []
                if(len(_line) <= 3):
                    add_ex_func(c_name, f_name, ef_types)
                    continue
                ret_val = int(_line[3].strip())
                for i in range(ret_val):
                    ret_type_tuple = _line[4+i]
                    ret_info = extract_type_tuple(ret_type_tuple)
                    num = [-1]
                    denom = [-1]
                    norm = 'u'
                    copy = "c"
                    value = 'u'
                    addr = 'u'
                    if(len(ret_info) >= 5):
                        copy = ret_info[0]
                        num = extract_address(ret_info[1])
                        denom = extract_address(ret_info[2])
                        norm = ret_info[3].strip()
                        try:
                            norm = int(norm)
                        except ValueError:
                            norm = norm
                        value = ret_info[4].strip()
                        try:
                            value = int(value)
                        except ValueError:
                            value = value
                    elif(len(ret_info) >= 2):
                        copy = ret_info[0]
                        addr = ret_info[1].strip()  #No longer lf, link_function deprecated. Stores address instead
                        decimals = None
                        if(copy == "c"):
                            #Store the addr as the name_key
                            _addr = address_handler.type_file_new_address(addr, True)
                            if(len(ret_info) >= 3):
                                decimals = int(ret_info[2])
                            addr = _addr.head
                            if(decimals != None):
                                _addr.norm = decimals
                                norm = decimals
                    ef_types.append((copy, num, denom, norm, value, addr))
                add_ex_func(c_name, f_name, ef_types)

            #SPECIAL FUNCTION
            if(_line[0].strip() == "[spexf]"):
                #Derive information about the parameters
                c_name = _line[1].strip()
                f_name = _line[2].strip()
                param_types = []
                #Do not include unless there are parameters in question that are important
                num_params = int(_line[3].strip())
                for param in range (num_params):
                    param_tuple = _line[4+param].strip()
                    tuple_info = extract_type_tuple(param_tuple)
                    num = [-1]
                    denom = [-1]
                    norm = 'u'
                    copy = "c"
                    value = 'u'
                    addr = 'u'
                    if(len(tuple_info) >= 5):
                        copy = tuple_info[0]
                        #num and den are either: concrete addresses (i.e. USDC) or relative parameters (i.e. 1, 2)
                        num = extract_address(tuple_info[1])
                        denom = extract_address(tuple_info[2])
                        #norm is either int, 'u', or 'c'
                        norm = tuple_info[3].strip()
                        try:
                            norm = int(norm)
                        except ValueError:
                            norm = norm
                            #value is just value
                        value = tuple_info[4].strip()
                        try:
                            value = int(value)
                        except ValueError:
                            value = value
                    elif(len(tuple_info) >= 2):
                        #I don't know if this will get used, hopefully not
                        copy = tuple_info[0]
                        addr = tuple_info[1].strip()  #No longer lf, link_function deprecated. Stores address instead
                        decimals = None
                        if(copy == "c"):
                            #Store the addr as the name_key
                            _addr = address_handler.type_file_new_address(addr, True)
                            if(len(tuple_info) >= 3):
                                decimals = int(tuple_info[2])
                            addr = _addr.head
                            if(decimals != None):
                                _addr.norm = decimals
                    param_types.append((copy, num, denom, norm, value, addr))

            #SUMMARY OF EXTERNAL FUNCTION
            if(_line[0].strip() == "[sef]"):
                c_name = _line[1].strip()
                f_name = _line[2].strip()
                ef_types = []
                if(len(_line) <= 3):
                    add_ex_func(c_name, f_name, ef_types)
                    continue
                ret_val = int(_line[3].strip())
                for i in range(ret_val):
                    ret_type_tuple = _line[4+i]
                    ret_info = extract_type_tuple(ret_type_tuple)
                    num = [-1]
                    denom = [-1]
                    norm = 'u'
                    copy = "c"
                    addr = None
                    #print(_line[4+i])
                    #print(ret_info)
                    if(len(ret_info) >= 4):
                        copy = ret_info[0]
                        num = extract_integers(ret_info[1])
                        denom = extract_integers(ret_info[2])
                        norm = int(ret_info[3].strip())
                        if(len(ret_info) >= 5):
                            addr = ret_info[4]  #No longer lf, link_function deprecated. Stores address instead
                    ef_types.append((copy, num, denom, norm, addr))
                add_ex_func(c_name, f_name, ef_types)
            #REFERENCE TYPE
            if(_line[0].strip() == "[tref]"):
                if(not(t_file in read_files)):
                    #print(_line)
                    total_annotations+=1
                ref_name = _line[1].strip()
                num = [-1]
                denom = [-1]
                norm = ['u']
                lf = None
                addr = 'u'
                value = 'u'
                if(len(_line) > 2):
                    num =extract_address(_line[2].strip())
                    denom = extract_address(_line[3].strip())
                    norm = int(_line[4].strip())
                    if(len(_line) >= 6):
                        addr = _line[5]
                    if(len(_line) >= 7):
                        value = _line[6]
                        try:
                            value = int(value)
                        except ValueError:
                            value = value
                add_ref(ref_name, (num, denom, norm , value, addr))
            #ADDRESS TYPE
            #func/global, name, norm
            #i.e. global, USDC, 6       (positive address)
            #i.e. transfer, token, *    (negative address)
            if(_line[0].strip() == "[ta]"):
                if(not(t_file in read_files)):
                    #print(_line)
                    total_annotations+=1
                func_name = _line[1].strip()
                var_name = _line[2].strip()

                #Allow third parameter to be global variable if known? 
                #Automatic propogation...
                _norm = _line[3].strip()
                addr_key = func_name + ":" + var_name
                if(not(addr_key in label_sets)):
                    if(func_name == "global"):
                        addr = address_handler.type_file_new_address(addr_key, True)
                    else:
                        addr = address_handler.type_file_new_address(addr_key, False)
                if(_norm != '*'):
                    norm = int(_line[3].strip())
                else:
                    norm = _norm
                add_addr(func_name, var_name, norm)
                if(reuse_addr):
                    reuse_addr_types[var_name] = norm
            #FIELD TYPE
            if(_line[0].strip() == "[t*]"):
                if(not(t_file in read_files)):
                    #print(_line)
                    total_annotations+=1
                func_name = _line[1].strip()
                parent_name = _line[2].strip()
                field_name = _line[3].strip()
                num = [-1]
                denom = [-1]
                norm = ['u']
                value = 'u'
                addr = 'u'
                if(len(_line) >= 8):
                    num = [_line[4].strip()]
                    denom = [_line[5].strip()]
                    norm = [int(_line[6].strip())]
                    value = _line[7].strip()
                    try:
                        value = int(value)
                    except ValueError:
                        value = value
                elif(len(_line) >= 5):
                    norm = int(_line[5].strip())
                    if(isinstance(addr, int)):
                        addr = _line[4]
                    else:
                        if("global" in _line[4]):
                            addr = address_handler.type_file_new_address(_line[4], True)
                            addr.norm = norm
                        else:
                            addr = address_handler.type_file_new_address(_line[4], False)
                            addr.norm = norm
                        addr = addr.head
                    

                add_field(func_name, parent_name, field_name, (num, denom, norm, value, addr))
    read_files[t_file] = True
    parse_finance_file(f_file)

def add_var(function_name, var_name, type_tuple):
    key = function_name + '_' + var_name
    #(f"Adding {key}: {type_tuple}")
    var_type_hash[key] = type_tuple

def get_var_type_tuple(function_name, var_name):
    global reuse_fin
    global reuse_fin_types
    key = function_name + "_" + var_name
    if(key in var_type_hash):
        #cast num and den
        temp = list(var_type_hash[key])
        #print(f"List: {temp}")
        temp[0] = stringToType(temp[0])
        temp[1] = stringToType(temp[1])
        #cast addr
        if(temp[4] != 'u'):
            temp[4] = stringToType(temp[4])
        if(len(temp) < 6 and reuse_fin and var_name in reuse_fin_types):
            temp.append(reuse_fin_types[var_name])
        return tuple(temp)
    return None

def add_alias(used_name, actual_name):
    contract_name_aliases[used_name] = actual_name

def get_alias(used_name):
    if(used_name in contract_name_aliases):
        return contract_name_aliases[used_name]
    else:
        return None

def add_addr(function_name, var_name, norm):
    key = function_name + "_" + var_name
    #print(f"Addr:{key} : {norm}")
    address_type_hash[key] = norm

def get_addr(function_name, var_name, chk_exists = False):
    global reuse_addr
    global reuse_addr_types
    key = function_name + "_" + var_name
    if(key in address_type_hash):
        return address_type_hash[key]
    else:
        if(chk_exists):
            return None
        if(reuse_addr and var_name in reuse_addr_types):
            add_addr(function_name, var_name, reuse_addr_types[var_name])
        else:
            #Add null address (automatic)
            add_addr(function_name, var_name, 0)
        return address_type_hash[key]
    #Deprecated
    return None

def add_tuple(tuple_name, type_tuples):
    key = tuple_name
    tuple_type_hash[key] = type_tuples

def stringToType(string):
    global address_to_label
    type = -1
    if(string == None):
        return None
    try:
        type = int(string)
    except ValueError:
        #search address
        _string = str(string)
        gstring = "global:"+str(string)
        #(address_to_label)
        if gstring in address_to_label:
            type = address_to_label[gstring]
        elif _string in address_to_label:
            type = address_to_label[_string]
        else:
            #Create new address
            type = address_handler.type_file_new_address(gstring, True).head
    return type

def get_tuple(tuple_name):
    key = tuple_name
    if key in tuple_type_hash:
        return tuple_type_hash[key]
    return None

def add_field(function_name, parent_name, field_name, type_tuples):
    key = function_name+'_'+parent_name+'_'+field_name
    #print(f"IN KEY: {key}")
    field_type_hash[key] = type_tuples

def get_field(function_name, full_parent_name, field_name):
    key = function_name + '_' + full_parent_name + '_' + field_name
    #print(f"OUT KEY: {key}")
    if key in field_type_hash:
        temp = list(field_type_hash[key])
        #print(f"List: {temp}")
        if(isinstance(temp[0], list)):
            temp[0][0] = stringToType(temp[0][0])
        else:
            temp[0] = stringToType(temp[0])
        if(isinstance(temp[1], list)):
            temp[1][0] = stringToType(temp[1][0])
        else:
            temp[1] = stringToType(temp[1])
        return tuple(temp)
    return None


def add_ex_func(contract_name, function_name, type_tuple):
    key = contract_name + '_' + function_name
    ex_func_type_hash[key] = type_tuple

def get_dir_ex_func_type_tuple(contract_name, function_name):
    key = contract_name + '_' + function_name
    if(key in ex_func_type_hash):
        return(ex_func_type_hash[key])
    return None

#Extended Function Tuple Unpacking etc in the Address version
def get_ex_func_type_tuple_a(contract_name, function_name, parameters):
    key = contract_name + '_' + function_name
    if(key in ex_func_type_hash):
        func_tuple = ex_func_type_hash[key]
        ret_type_tuples = []
        pos = -1
        for ret_var in func_tuple:
            #print(f"Retvar: {ret_var}")
            pos+=1
            copy = ret_var[0]
            num_trans = ret_var[1]
            den_trans = ret_var[2]
            norm = ret_var[3]
            value = ret_var[4]
            addr = ret_var[5]
            ftype = -1
            if(len(ret_var) >= 7):
                ftype = ret_var[6]
            ret_num = []
            ret_den = []
            param = parameters
            #for p in parameters:
                #print(p.name)
            propogate_ftype = False
            if(ftype == 1000):
                propogate_ftype = True
                ftype = -1
            if(len(param) == 0 or copy == "c"):
                #No parameters, assume that the parameters are directly the types
                _num_trans = []
                _den_trans = []
                for _addr in num_trans:
                    #May translate from global addresses
                    _addr = stringToType(_addr)
                    _num_trans.append(_addr)
                for _addr in den_trans:
                    #May translate from global addresses
                    _addr = stringToType(_addr)
                    _den_trans.append(_addr)
                ret_type_tuple = (_num_trans, _den_trans, norm , value, addr, ftype)
                ret_type_tuples.append(ret_type_tuple)
                continue

            for num in num_trans:
                #Guarantee to be integers, as it represents the index parameter
                num = num #int(num.strip())
                if(isinstance(num, str)):
                    num = int(num.strip())
                if(num == -1):
                    ret_num.append(-1)
                    continue
                cur_param = param[num-1].extok
                for n in cur_param.num_token_types:
                    ret_num.append(n)
                for d in cur_param.den_token_types:
                    ret_den.append(d)
                if(cur_param.address != 'u'):
                    ret_num.append(cur_param.address)
                if(propogate_ftype):
                    ftype = tcheck_propagation.pass_ftype_no_ir(ftype, cur_param.finance_type, "mul")
            for den in den_trans:
                den = den #int(den.strip())
                if(isinstance(den, str)):
                    den = int(den.strip())
                if(den == -1):
                    ret_den.append(-1)
                    continue
                cur_param = param[den-1].extok
                for n in cur_param.num_token_types:
                    ret_den.append(n)
                for d in cur_param.den_token_types:
                    ret_num.append(d)
                if(cur_param.address != 'u'):
                    ret_den.append(cur_param.address)
                if(propogate_ftype):
                    ftype = tcheck_propagation.pass_ftype_no_ir(ftype, cur_param.finance_type, "div")
            if(isinstance(norm, int) and norm > 0):
                norm = param[norm-1].extok.norm
                #print(f"hers norm: {norm}")
            if(isinstance(addr, int) and lc > 0):
                addr = param[lc-1].extok.address
            ret_type_tuple = (ret_num, ret_den, norm, value, addr, ftype)
            ret_type_tuples.append(ret_type_tuple)
        return ret_type_tuples
    return None


def get_ex_func_type_tuple(contract_name, function_name, parameters):
    key = contract_name + '_' + function_name
    if(key in ex_func_type_hash):
        func_tuple = ex_func_type_hash[key]
        ret_type_tuples = []
        pos = -1
        for ret_var in func_tuple:
            #print(ret_var)
            pos+=1
            copy = ret_var[0]
            num_trans = ret_var[1]
            den_trans = ret_var[2]
            norm = ret_var[3]
            lc = ret_var[4]
            ftype = -1
            if(len(ret_var) >= 6):
                ftype = ret_var[5]
            ret_num = []
            ret_den = []
            param = parameters
            #for p in parameters:
            #    print(p.name)
            
            if(len(param) == 0 or copy == "c"):
                #No parameters, assume that the parameters are directly the types
                ret_type_tuple = (num_trans, den_trans, norm , lc, ftype)
                ret_type_tuples.append(ret_type_tuple)
                continue
            for num in num_trans:
                if(num == -1):
                    ret_num.append(-1)
                    continue
                cur_param = param[num-1].extok
                for n in cur_param.num_token_types:
                    ret_num.append(n)
                for d in cur_param.den_token_types:
                    ret_den.append(d)
            for den in den_trans:
                if(den == -1):
                    ret_den.append(-1)
                    continue
                cur_param = param[den-1].extok
                for n in cur_param.num_token_types:
                    ret_den.append(n)
                for d in cur_param.den_token_types:
                    ret_num.append(d)
            if(isinstance(norm, int) and norm > 0):
                norm = param[norm-1].extok.norm
            if(isinstance(lc, int) and lc > 0):
                lc = param[lc-1].extok.linked_contract
            ret_type_tuple = (ret_num, ret_den, norm, lc, ftype)
            ret_type_tuples.append(ret_type_tuple)
        return ret_type_tuples
    return None

def add_ref(ref_name, type_tuple):
    key = ref_name
    ref_type_hash[key] = type_tuple

def get_ref_type_tuple(ref_name):
    key = ref_name
    if(key in ref_type_hash):
        temp = list(ref_type_hash[key])
        #print(temp)
        for n in range(len(temp[0])):
            #print(temp[0][n])
            temp[0][n] = stringToType(temp[0][n])
        #temp[0] = stringToType(temp[0])
        for d in range(len(temp[1])):
            temp[1][n] = stringToType(temp[1][d])
        #temp[1] = stringToType(temp[1])
        temp[4] = stringToType(temp[4])
        return tuple(temp)
    return None

def add_in_func(contract_name, function_name, in_func):
    #deprecated
    return
    key = contract_name + '_' + function_name
    if(key in in_func_ptr_hash):
        #Do not modify thing already in hash.
        return
    in_func_ptr_hash[key] = in_func

def get_in_func_ptr(contract_name, function_name):
    key = contract_name + '_' + function_name
    #view_all_cf_pairs()
    return get_cf_pairh(contract_name, function_name)
    return None
    #deprecated
    if(key in in_func_ptr_hash):
        funcptr = in_func_ptr_hash[key]
        if(funcptr.entry_point == None):
            return None
        return in_func_ptr_hash[key]
    return None

def allow_contract(contract_name):
    allowed_contracts[contract_name] = True

def check_contract(contract_name):
    if(contract_name in allowed_contracts):
        return True
    return False

def bar_function(function_name):
    barred_functions[function_name] = True

def check_function(function_name):
    if(function_name in barred_functions):
        return True
    return False

def reset_update_ratios():
    #redo update ratios: seems like there may be some issues
    global update_ratios
    update_ratios = {10: -1, 
                 12: -1,
                 20: -1,
                 21: -1}

def split_line(line):
    result = []
    buffer = ''
    count_brackets = 0
    count_parenthesis = 0
    for char in line:
        if char == '[':
            count_brackets += 1
        elif char == ']':
            count_brackets -= 1
        
        if char == '{':
            count_parenthesis += 1
        elif char == '}':
            count_parenthesis -=1

        if char == ',' and count_brackets == 0 and count_parenthesis == 0:
            result.append(buffer.strip())
            buffer = ''
        else:
            buffer += char

    result.append(buffer.strip())
    return result

def extract_type_tuple(input_str):
    # Remove the parenthesis
    input_str = input_str.strip("{}")
    
    info_list = [str(x) for x in split_line(input_str)]

    return info_list

def extract_integers(input_str):
    # Remove the brackets
    input_str = input_str.strip("[]")
    
    # Split the string by commas and convert to integers
    integer_list = [int(x) for x in input_str.split(",")]

    return integer_list

def extract_address(input_str):
    # Remove the brackets
    input_str = input_str.strip("[]")
    
    # Split the string by commas and convert to integers
    list = [x for x in input_str.split(",")]

    return list
