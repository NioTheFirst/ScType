func_ptr_hash = {}
cont_ptr_hash = {}

def add_cont_with_state_var(contract_name, contract):
    global cont_ptr_hash
    if(len(_read_state_variables(contract)) == 0):
        return
    else:
        cont_ptr_hash[contract_name] = contract


def get_cont_with_state_var(contract_name):
    global cont_ptr_hash
    if(contract_name in cont_ptr_hash):
        return cont_ptr_hash[contract_name]
    return None

def _read_state_variables(contract):
    ret = []
    for f in contract.all_functions_called + contract.modifiers:
        ret += f.state_variables_read
    return ret

def add_cf_pair(contract_name, function_name, function):
    global func_ptr_hash
    if(contract_name == None or function_name == None or function.entry_point == None):
        return False
    key = contract_name + '_' + function_name
    if(key in func_ptr_hash):
        return False
    func_ptr_hash[key] = function
    return True

def get_cf_pairh(contract_name, function_name):
    global func_ptr_hash
    key = contract_name + '_' + function_name
    #print(key)
    #print(func_ptr_hash)
    if(key in func_ptr_hash):
        #print("Found")
        return func_ptr_hash[key]
    #print("Not found")
    return None

def view_all_cf_pairs():
    print(func_ptr_hash)
