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

def parse_type_file(t_file):
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
                num = [-1]
                denom = [-1]
                norm = [0]
                lf = None
                if(len(_line) > 3):
                    num = extract_integers(_line[3])
                    denom = extract_integers(_line[4])
                    norm = int(_line[5]).strip()
                    if(len(_line) == 7):
                        lf = _line[6]
                add_ex_func(c_name, f_name, (num, denom, norm, lf))
            #REFERENCE TYPE
            if(_line[0].strip() == "[tref]"):
                ref_name = _line[1].strip()
                num = [-1]
                denom = [-1]
                norm = [0]
                lf = None
                if(len(_line) > 2):
                    num = int(_line[2].strip)
                    denom = int(_line[3].strip)
                    norm = int(_line[4].strip)
                    if(len(_line) == 6):
                        lf = _line[5]
                add_ref(ref_name, (num, denom, norm))

def add_var(function_name, var_name, type_tuple):
    key = function_name + '_' + var_name
    var_type_hash[key] = type_tuple

def get_var_type_tuple(function_name, var_name):
    key = function_name + "_" + var_name
    if(key in var_type_hash):
        return var_type_hash[key]
    return None

def add_ex_func(contract_name, function_name, type_tuple):
    key = contract_name + '_' + function_name
    ex_func_type_hash[key] = type_tuple

def get_ex_func_type_tuple(contract_name, function_name, parameters):
    key = contract_name + '_' + function_name
    if(key in ex_func_type_hash):
        func_tuple = ex_func_type_hash[key]
        num_trans = func_tuple[0]
        den_trans = func_tuple[1]
        norm = func_tuple[2]
        lf = func_tuple[3]
        ret_num = []
        ret_den = []
        for num in num_trans:
            cur_param = param[num-1]
            for n in cur_param.token_typen:
                ret_num.append(n)
            for d in cur_param.token_typed:
                ret_den.append(d)
        for den in den_trans:
            cur_param = param[den-1]
            for n in cur_param.token_typen:
                ret_den.append(n)
            for d in cur_param.token_typed:
                ret_num.append(d)
        ret_type_tuple = (ret_num, ret_den, norm, lf)
        return ret_type_tuple
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

    for char in line:
        if char == '[':
            count_brackets += 1
        elif char == ']':
            count_brackets -= 1

        if char == ',' and count_brackets == 0:
            result.append(buffer.strip())
            buffer = ''
        else:
            buffer += char

    result.append(buffer.strip())
    return result

def extract_integers(input_str):
    # Remove the brackets
    input_str = input_str.strip("[]")

    # Split the string by commas and convert to integers
    integer_list = [int(x) for x in input_str.split(",")]

    return integer_list
