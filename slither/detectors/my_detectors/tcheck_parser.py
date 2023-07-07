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

allowed_contracts = {}
barred_functions = {}
var_type_hash = {}
in_func_ptr_hash = {}
ex_func_type_hash = {}
ref_type_hash = {}
tuple_type_hash = {}
field_type_hash = {}

field_tuple_start = 4

f_type_num = {
    -1: "undef",
    0: "raw balance",
    1: "net balance",
    2: "accrued balance",
    3: "final balance",
    10: "fee ratio (t)",
    11: "transaction fee",
    12: "lp fee",
    20: "simple interest",
    21: "compound interest",
    30: "reserve",
    40: "price/exchange rate",
}

f_type_name = {
    "undef" : -1,
    "raw balance" :0,
    "net balance" :1,
    "accrued balance" :2,
    "final balance" :3,
    "fee ratio (t)" : 10,
    "transaction fee" :11,
    "lp fee" : 12,
    "simple interest" : 20,
    "compound interest" : 21,
    "reserve" : 30,
    "price/exchange rate" : 40,
}

def gen_finance_instances(line):
    _line = line.split(",")
    finance_instances = []
    for param in _line:
        if(param.find("f:")):
            offset = 0
            foundf = False
            for i in range(len(param)):
                if(param[i] == 'f' and i+1 < len(param) and param[i+1] == ':'):
                    foundf = True
                    offset=i+2
                    break
            if(foundf == False):
                continue
            isolated_param = param[offset:].strip()
            print(f"Isolated Param: {isolated_param}")
            f_res = None
            try:
                temp = int(isolated_param)
                f_res = temp
            except ValueError:
                if isolated_param in f_type_name:
                    f_res = f_type_name[isolated_param]
                else:
                    f_res = -1
            if not isinstance(f_res, int):
                print("[x] FINANCE TYPE IS NOT INT")
            finance_instances.append(f_res)
            print(f"F num: {f_res}")
    return finance_instances


def parse_finance_file(f_file):
    #Same structure as token_type parser
    if(f_file == None):
        return
    with open(f_file, 'r') as finance_file:
        for line in finance_file:
            _line = split_line(line)
            #Look for "f: "
            f_params = gen_finance_instances(line)
            if(len(f_params) == 0):
                f_params.append(-1)
            if(_line[0].strip() == "[t]"):
                f_name = _line[1].strip()
                v_name = _line[2].strip()
                norm_tt = get_var_type_tuple(f_name, v_name)
                norm_tt+=(f_params[0], )
                add_var(f_name, v_name, norm_tt)
            elif(_line[0].strip == "[sef]"):
                c_name = _line[1].strip()
                f_name = _line[2].strip()
                ef_tts = get_ex_func_type_tuple(c_name, f_name)
                cur = 0
                new_tts = []
                for tt in ef_tts:
                    tt+=(f_params[cur], )
                    new_tts.append(tt)
                    cur+=1
                add_ex_func(c_name, f_name, new_tts)
            elif(_line[0].strip == "tref"):
                ref_name = _line[1].strip()
                ref_tt = get_ref_type_tuple(ref_name)
                ref_tt += (f_params[0], )
                add_ref(ref_name, ref_tt)
            
            elif(_line[0].strip == "t*"):
                f_name = _line[1].strip()
                p_name = _line[2].strip()
                v_name = _line[3].strip()
                field_tt = get_field(f_name, p_name, v_name)
                field_tt += (f_params[0], )
                add_field(f_name, p_name, v_name, field_tt)

def parse_type_file(t_file, f_file = None):
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
            print(line)
            if(_line[0].strip() == "[t]"):
                f_name = _line[1].strip()
                v_name = _line[2].strip()
                try:
                    num = -1
                    den = -1
                    norm = 'u'
                    if(len(_line) > 3):
                        num = int(_line[3].strip())
                        den = int(_line[4].strip())
                        norm = int(_line[5].strip())
                    l_name = None
                    if(len(_line) == 7):
                        l_name = _line[6].strip()
                    add_var(f_name, v_name, (num, den, norm, l_name))
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
                    lf = None
                    print(_line[4+i])
                    print(ret_info)
                    if(len(ret_info) >= 4):
                        copy = ret_info[0]
                        num = extract_integers(ret_info[1])
                        denom = extract_integers(ret_info[2])
                        norm = int(ret_info[3].strip())
                        if(len(ret_info) == 5):
                            lf = ret_info[4]
                    ef_types.append((copy, num, denom, norm, lf))
                add_ex_func(c_name, f_name, ef_types)
            #REFERENCE TYPE
            if(_line[0].strip() == "[tref]"):
                ref_name = _line[1].strip()
                num = [-1]
                denom = [-1]
                norm = ['u']
                lf = None
                if(len(_line) > 2):
                    num =[ int(_line[2].strip())]
                    denom = [int(_line[3].strip())]
                    norm = int(_line[4].strip())
                    if(len(_line) == 6):
                        lf = _line[5]
                add_ref(ref_name, (num, denom, norm, lf))
            #FIELD TYPE
            if(_line[0].strip() == "[t*]"):
                func_name = _line[1].strip()
                parent_name = _line[2].strip()
                field_name = _line[3].strip()
                num = [-1]
                denom = [-1]
                norm = ['u']
                lf = None
                if(len(_line) > 4):
                    num = [ int(_line[4].strip())]
                    denom = [int(_line[5].strip())]
                    norm = [int(_line[6].strip())]
                    if(len(_line) == 8):
                        lf = _line[7]

                add_field(func_name, parent_name, field_name, (num, denom, norm, lf))
    parse_finance_file(f_file)

def add_var(function_name, var_name, type_tuple):
    key = function_name + '_' + var_name
    var_type_hash[key] = type_tuple

def get_var_type_tuple(function_name, var_name):
    key = function_name + "_" + var_name
    if(key in var_type_hash):
        return var_type_hash[key]
    return None


def add_tuple(tuple_name, type_tuples):
    key = tuple_name
    tuple_type_hash[key] = type_tuples

def get_tuple(tuple_name):
    key = tuple_name
    if key in tuple_type_hash:
        return tuple_type_hash[key]
    return None

def add_field(function_name, parent_name, field_name, type_tuples):
    key = function_name+'_'+parent_name+'_'+field_name
    field_type_hash[key] = type_tuples

def get_field(function_name, full_parent_name, field_name):
    key = function_name + '_' + full_parent_name + '_' + field_name
    if key in field_type_hash:
        return field_type_hash[key]
    return None


def add_ex_func(contract_name, function_name, type_tuple):
    key = contract_name + '_' + function_name
    ex_func_type_hash[key] = type_tuple

def get_ex_func_type_tuple(contract_name, function_name, parameters):
    key = contract_name + '_' + function_name
    if(key in ex_func_type_hash):
        func_tuple = ex_func_type_hash[key]
        ret_type_tuples = []
        for ret_var in func_tuple:
            print(ret_var)
            copy = ret_var[0]
            num_trans = ret_var[1]
            den_trans = ret_var[2]
            norm = ret_var[3]
            lf = ret_var[4]
            ret_num = []
            ret_den = []
            param = parameters
            for p in parameters:
                print(p.name)
            if(len(param) == 0 or copy == "c"):
                #No parameters, assume that the parameters are directly the types
                ret_type_tuple = (num_trans, den_trans, norm , lf)
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
            if(norm > 0):
                norm = param[norm-1].extok.norm
            if(isinstance(lf, int) and lf > 0):
                lf = param[lf-1].extok.norm
            ret_type_tuple = (ret_num, ret_den, norm, lf)
            ret_type_tuples.append(ret_type_tuple)
        return ret_type_tuples
    return None

def add_ref(ref_name, type_tuple):
    key = ref_name
    ref_type_hash[key] = type_tuple

def get_ref_type_tuple(ref_name):
    key = ref_name
    if(key in ref_type_hash):
        return ref_type_hash[key]
    return None

def add_in_func(contract_name, function_name, in_func):
    key = contract_name + '_' + function_name
    in_func_ptr_hash[key] = in_func

def get_in_func_ptr(contract_name, function_name):
    key = contract_name + '_' + function_name
    if(key in in_func_ptr_hash):
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
