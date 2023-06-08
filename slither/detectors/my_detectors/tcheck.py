from collections import defaultdict
from slither.core.variables.local_variable import LocalVariable
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import Binary, Assignment, BinaryType, LibraryCall, Return, InternalCall, Condition, HighLevelCall, Unpack, Phi, EventCall
from slither.slithir.variables import Constant, ReferenceVariable, TemporaryVariable, LocalIRVariable, StateIRVariable, TupleVariable
from slither.core.variables.variable import Variable
from slither.core.variables.state_variable import StateVariable
from slither.core.declarations.function import Function
from slither.core.variables.local_variable import LocalVariable
from slither.core.variables.function_type_variable import FunctionTypeVariable
import linecache

user_type = False
type_file = ""
maxTokens = 10
tempVar = defaultdict(list) #list storing temp variables (refreshed every node call)
strgVar = defaultdict(list) #list storing storage variables (kept through all calls)
currNode = None
errors = []
nErrs = 0
line_no = 1
function_hlc = 0
function_ref = 0
type_hashtable = {}
function_bar = {}
function_check = {}
contract_run = {}

#IMPORTANT: read internal
read_internal = True

#USAGE: adds token pair to type_hashtable
#RETURNS: composite key of the token pair
def add_hash(function_name, var_name, num, den, norm):
    composite_key = function_name + '_' + var_name
    values = (num, den, norm)
    type_hashtable[composite_key] = values
    return composite_key

#USAGE: given a function name and a var name, return the token pair
#RETURNS: tuple holding the token pair
def get_hash(function_name, var_name):
    composite_key = function_name + '_' + var_name
    if composite_key in type_hashtable:
        return type_hashtable[composite_key]
    else:
        print("Variable: " + var_name + " not provided in Function: " + function_name)
        return None

#USAGE: bar a function from being typechecked
#RETURNS: NULL
def bar_function(function_name):
    function_bar[function_name] = True

#USAGE: returns if a function should be typechecked
#RETURNS bool
def check_bar(function_name):
    if(function_name in function_bar):
        print("[x] " + function_name + " barred")
        return True
    return False

#USAGE: selects a  contract to typecheck
#RETURNS: NULL
def run_contract(contract_name):
    contract_run[contract_name] = True

#USAGE: returns if a function should be typechecked
#RETURNS bool
def check_contract(contract_name):
    global user_type
    #if(user_type):
        #return True
    if(contract_name in contract_run):
        print("[*] " + contract_name + " run")
        return True
    print("[x] " + contract_name + " not run")
    return False

def print_token_type(ir):
    print("Num:")
    for n in ir.token_typen:
        print(n)
    print("Den:")
    for d in ir.token_typed:
        print(d)
    print("Norm:")
    print(ir.norm)

#USAGE: prints a param_cache
#RETURNS: nothing
def print_param_cache(param_cache):
    param_no = 0
    for param in param_cache:
        print("Param: " + str(param_no))
        print(f"    num: {param[0]}")
        print(f"    den: {param[1]}")
        param_no+=1

#USAGE: given an ir for a function call, generate a param_cache
#RETURNS: retursn a param_cache
def function_call_param_cache(ir):
    #assumes types have been assigned (any undefined types must be resolved previously)
    param_cache = []
    for param in ir.read:
        num = param.token_typen
        den = param.token_typed
        norm = param.norm
        param_type = [num, den, norm]
        param_cache.append(param_type)
    return param_cache

#USAGE: given a function, generate a param_cache
#RETURNS: returns a param_cache
def function_param_cache(function):
    #assumes types have already been assigned
    param_cache = []
    for param in function.parameters:
        num = param.token_typen
        den = param.token_typed
        norm = param.norm
        param_type = [num, den, norm]
        param_cache.append(param_type)
    return param_cache

#USAGE: given a param_cache, decide whether or not to add it to the parameter_cache
#        of a function
#RETURNS: bool (added or not)
def add_param_cache(function, new_param_cache):
    global maxTokens
    add_param = False
    fpc = function.parameter_cache()
    if(len(fpc) == 0):
        add_param = True
    for a in range(len(fpc)):
        cur_param_cache = fpc[a]
        paramno = 0
        add_cur_param = False
        for cur_param in cur_param_cache:
            #compare cur_param with new_param_cache[paramno]
            seen_n = []
            seen_d = []
            seen_norm = False
            for i in range(maxTokens):
                seen_n.append(0)
                seen_d.append(0)   
            #compare numerators
            for num in cur_param[0]:
                seen_n[num]+=1
            for num in new_param_cache[paramno][0]:
                seen_n[num]-=1
            #compare denominators
            for num in cur_param[1]:
                seen_d[num]+=1
            for num in new_param_cache[paramno][1]:
                seen_d[num]-=1
            #compare norms
            if(new_param_cache[paramno][2] != cur_param[2]):
                seen_norm = True
            for i in range(maxTokens):
                if(seen_norm or seen_n[i] != 0 or seen_d[i] != 0):
                    add_cur_param = True
                    break
            if(add_cur_param):
                break
            paramno+=1
        if(add_cur_param == True):
            add_param = True
            break
    if(add_param):
        function.add_parameter_cache(new_param_cache)
        return True
    return False

#USAGE: parses an input file and fills the type_hashtable
#RETURNS: NULL
#parse formula:
#function_name
#var_name
#num
#den
def parse_type_file(t_file):
    with open (t_file, 'r') as type_file:
        lines = []
        counter = 0
        temp_counter = 0
        for line in type_file:
            #print(line)
            #print(counter)
            if(line.strip() == "[x]bar"):
                temp_counter = counter
                counter = -1
                continue
            if(counter == -1):
                bar_function(line.strip())
                counter = temp_counter
                continue
            if(line.strip() == "[*]run"):
                temp_counter = counter
                counter = -2
                continue
            if(counter == -2):
                run_contract(line.strip())
                counter = temp_counter
                continue
            lines.append(line)
            counter+=1
            if(counter == 5):
                counter = 0
                function_name = lines[0].strip()
                var_name = lines[1].strip()
                try:
                    num = int(lines[2].strip())
                    den = int(lines[3].strip())
                    if(lines[4].strip() == "fill norm"):
                        norm = -101
                    else:
                        norm = int(lines[4].strip())
                    add_hash(function_name, var_name, num, den, norm)
                    print("xcxcxc" + var_name)
                except ValueError:
                    print("Invalid Value read")
                lines.clear()
#USAGE: given a variable ir, return the type tuple
#RETURNS: type tuple
def read_type_file(ir):
    function_name = ir.parent_function
    var_name = ir.name
    if(ir.tname != None):
        var_name = ir.tname
    #print("read function name: " + function_name)
    #print("read parent name: " + ir.name)
    return get_hash(function_name, var_name)

#USAAGE: returns the number of the next type from the provided type_file (automated usage)
#RETURNS: the type of the next token
def get_next_token_type(t_file):
    global line_no
    #print(line_no)
    
    try:
        line = linecache.getline(t_file, line_no)
        if line:
            #print(f"Line {line_number}: {line.strip()}")
            line = line.strip()
            try:
                integer_number = int(line)
                line_no+=1
                return integer_number
                # Continue with the code that uses the integer number
            except ValueError:
                print(line)
                line_no+=1
                return get_next_token_type(t_file)
                # Handle the error gracefully or take appropriate action
        else:
            print(f"Line {line_no} not found in the file.")
            return(-1000)
    except FileNotFoundError:
        print("File not found.")
        return(-1000)
        # Handle the error gracefully or take appropriate action

#USAGE: querry the user for a type
#RETURNS: N/A
def querry_type(ir):
    global user_type
    global type_file
    uxname = ir.name
    if(ir.tname != None):
        uxname = ir.tname
    uxname = str(uxname)
    print("Finding type for "+ uxname + "...")
    if not(user_type):
        type_tuple = read_type_file(ir)
        if(type_tuple != None):
            num = type_tuple[0]
            den = type_tuple[1]
            norm = type_tuple[2]
            ir.add_token_typen(num)
            ir.add_token_typed(den)
            if(norm == -101):
                #fill as constant
                ir.norm = get_norm(ir)
            else:
                ir.norm = norm
            print_token_type(ir)
            print("[*]Type fetched successfully")
            return
        print("[x]Failed to fetch type from type file, defaulting to human interface")
    print("Define num type for \"" + uxname + "\": ")
    input_str = input()
    input_int = int(input_str)
    ir.token_type = input_int
    ir.add_token_typen(input_int)
    print("Define den type for \"" + uxname + "\": ")
    input_str = input()
    input_int = int(input_str)
    ir.add_token_typed(input_int)
    print("Define norm for \"" + uxname + "\": ")
    input_str = input()
    input_int = int(input_str)
    ir.norm = input_int
    print(ir.token_type)

def is_referenceVariable(ir):
    if not(is_variable(ir)):
        return False
    print("checking "+ir.name.lower())
    if isinstance(ir, ReferenceVariable):
        print("Refernce variable: " + ir.name.lower())
        return True
    return False

def is_constant(ir):
    if isinstance(ir, Constant):
        print("Constatn varible: "+ir.name.lower())
        return True
    return False
def is_high_level_call(ir):
    if isinstance(ir, HighLevelCall):
        print("High Level Call: " + str(ir.function_name).lower())
        return True
    return False
def is_temporary(ir):
    if isinstance(ir, TemporaryVariable):
        print("Temp variable: "+ir.name.lower())
def is_state(ir):
    if isinstance(ir, StateVariable):
        print("State variable: "+ir.name.lower())
        #if(is_type_undef(ir) or is_type_const(ir)):
        #    querry_type(ir)
def is_space(ir):
    if isinstance(ir, StateIRVariable):
        print("State IR  variable: "+ir.name.lower())
def is_local(ir):
    if isinstance(ir, LocalVariable):
        print("Local variable: "+ir.name.lower())
def is_tuple(ir):
    if isinstance(ir, TupleVariable):
        print("TUple variable: "+ir.name.lower())
def is_function(ir):
    if isinstance(ir, Function):
        print("Function: "+ir.name)
        temp = ir.parameters
def is_condition(ir):
    if isinstance(ir, Condition):
        print("Conidtion: ")
        for x in ir.read:
            print(x)
        print(ir.value)
def is_function_type_variable(ir):
    if isinstance(ir, FunctionTypeVariable):
        print("Function Type Variable: "+ir.name.lower())

def check_exist(ir):
    if(isinstance(ir, Constant)):
        ir.token_type == 0
        return True
    if((tempVar[ir.name] == None and strgVar[ir.name] == None) and ir.token_type == -2):
        return False
    return True

def is_type_undef(ir):
    if not(is_variable(ir)):
        print("not variable")
        return True
    if(len(ir.token_typen) == 0 and len(ir.token_typed) == 0):
        return True
    return False

def is_type_const(ir):
    if(len(ir.token_typen) == 1 and ir.token_typen[0] == -1 and len(ir.token_typed) == 1 and ir.token_typed[0] == -1):
        return True
    return False

#USAGE: assigns an IR to the constant type (-1)
#       ex: 1, 5, 1001
#RETURNS: NULL
def assign_const(ir):
    if(len(ir.token_typen) == 1 and ir.token_typen[0] == -1 and len(ir.token_typed) == 1 and ir.token_typed[0] == -1):
        return    
    ir.token_typen.clear()
    ir.token_typed.clear()
    ir.add_token_typen(-1)
    ir.add_token_typed(-1)

#USAGE: assigns an IR to the error type (-2) this stops infinite lioops
#RETURNS: NULL
def assign_err(ir):
    if(len(ir.token_typen) == 1 and ir.token_typen[0] == -2 and len(ir.token_typed) == 0):
        return
    ir.token_typen.clear()
    ir.token_typed.clear()
    assign_const(ir)
"""
#USAGE: assigns an IR to the non_token type (0)
#       ex: True, False, "hello"
#RETURNS: NULL
def assign_non(ir):
    if(len(ir.token_typen) == 1 and ir.token_typen[0] == 0 and len(ir.token_typed) == 0):
"""

#USAGE: copies all token types from the 'src' ir node to the 'dest' ir node
#RETURNS: null
def copy_token_type(src, dest):
    #dest.token_typen.clear()
    #dest.token_typed.clear()
    for n in src.token_typen:
        dest.add_token_typen(n)
    for d in src.token_typed:
        dest.add_token_typed(d)
    

#USAGE: copies inverse token types from the 'src' ir node from the 'dest' ir node
#RETURNS: null
def copy_inv_token_type(src, dest):
    for n in src.token_typen:
        dest.add_token_typed(n)
    for d in src.token_typed:
        dest.add_token_typen(n)

#USAGE: copy and replace a token from a param_cache to an ir
#RETURNS: nN/A
def copy_pc_token_type(src, dest):
    dest.token_typen.clear()
    dest.token_typed.clear()
    for n in src[0]:
        dest.add_token_typen(n)
    for d in src[1]:
        dest.add_token_typed(d)

def compare_token_type(src, dest):
    seen = []
    for i in range(maxTokens):
        seen.append(0)
    for n in src.token_typen:
        seen[n]+=1
    for n in dest.token_typen:
        seen[n]-=1
    for i in range(maxTokens):
        if(seen[i] != 0):
            return False
        seen[i] = 0
    for d in src.token_typed:
        seen[d]+=1
    for d in dest.token_typed:
        seen[d]-=1
    for i in range(maxTokens):
        if(seen[i] != 0):
            return False
    return True

def add_errors(ir):
    global nErrs
    global errors
    errors.append(ir)
    nErrs+=1
    print("Error with: " + ir.name + " in function " + ir.parent_function)
    assign_err(ir)

#USAGE: Converts the first ssa instance of a variable (ends with _1)
#RETURNS: NULL
def convert_ssa(ir):
    if(not(is_variable(ir))):
        return
    if(is_constant(ir)):
        return
    #if(not(ir.ssa_name)):
    #    return
    non_ssa_ir = ir.non_ssa_version

    #name = ir.ssa_name
    if(not (is_type_undef(non_ssa_ir)) and is_type_undef(ir)):
        copy_token_type(non_ssa_ir, ir)
        print_token_type(ir)


#given and ir, type check
#currently handles assignments and Binary
#returns ir if needs to be added back
def check_type(ir) -> bool:
    addback = False;
    #Assignmnet
    if isinstance(ir, Assignment):
        print("asgn")
        addback = type_asn(ir.lvalue, ir.rvalue)
        asn_norm(ir.lvalue, get_norm(ir.rvalue))
        #print_token_type(ir.lvalue)
    elif isinstance(ir, Binary):
        #Binary
        addback = type_bin(ir)
    elif isinstance(ir, InternalCall):
         #Function call
        print("ic")
        addback = type_fc(ir)
    elif isinstance(ir, HighLevelCall):
        #High level call
        addback = type_hlc(ir)
    elif isinstance(ir, Unpack):
        #Unpack tuple
        addback = type_upk(ir)
    elif isinstance(ir, Phi):
        #Phi (ssa) unpack
        addback = False
        convert_ssa(ir.lvalue)
        print("Phi")
    elif isinstance(ir, EventCall):
        return False
    elif(is_variable(ir.lvalue) and is_referenceVariable(ir.lvalue)):
        #Reference
        addback = type_ref(ir)
        return False
    #DEBUG
    if ir.lvalue and is_variable(ir.lvalue):
        print("[i]Type for "+ir.lvalue.name)
        print_token_type(ir.lvalue)
    print("done.")
    return (addback)

#USAGE: typcehcks an unpack functionality (similar to assign)
#RETURNS: nothing (type is querried from user)
def type_upk(ir) ->bool:
    #query the user for type info
    lval = ir.lvalue
    rtup = ir.tuple
    rind = ir.index
    print("Reading tuple " + str(rtup) + " index " + str(rind))
    #currently just querry the type of the left value
    querry_type(lval)
    return False

#USAGE: typecheck for high-level call (i.e. iERC20(address).balanceof())
#RETURNS: whether or not the high-level call node should be returned (should always return FALSE)
def type_hlc(ir) ->bool:
    #just query the user for the data (beta)
    global function_hlc
    print("High Call: "+str(ir.function_name))
    print("func name:" + ir.function.name)
    param = ir.arguments
    #for p in param:
    #    print(p.name)
    #    print_token_type(p)
    if(not(is_variable(ir.lvalue))):
        return False
    if(ir.function.name == "add"):
        return type_bin_add(ir.lvalue, param[0], param[1])
    elif(ir.function.name == "sub"):
        return type_bin_sub(ir.lvalue, param[0], param[1])
    elif(ir.function.name == "mul"):
        return type_bin_mul(ir.lvalue, param[0], param[1])
    elif(ir.function.name == "div"):
        return type_bin_div(ir.lvalue, param[0], param[1])
    temp = ir.lvalue.name
    print(temp)
    x = "hlc_"+str(function_hlc)
    ir.lvalue.change_name(x)
    print(ir.lvalue.name)
    querry_type(ir.lvalue)
    ir.lvalue.change_name(temp)
    function_hlc+=1
    return False

#USAGE: typechecks for references (i.e. a[0])
#RETURNS: always False
def type_ref(ir)->bool:
    global function_ref
    print("Ref: "+str(ir.lvalue.name))
    temp = ir.lvalue.name
    ir.lvalue.change_name('ref_'+str(function_ref))
    querry_type(ir.lvalue)
    ir.lvalue.change_name(temp)
    function_ref+=1
    return False

#USAGE: typecheck for function call (pass on types etc)
#RETURNS: whether or not the function call node should be returned
def type_fc(ir) -> bool:
    #check parameters
    for param in ir.read:
        init_var(param)
        if(is_constant(param)):
            assign_const(param)
        elif(is_type_undef(param)):
            #undefined type
            return True
    #generate param cache
    new_param_cache = function_call_param_cache(ir)
    print("Internal cal param_cache")
    print_param_cache(new_param_cache)
    added = add_param_cache(ir.function, new_param_cache)
    if(added):
        print("added")
        addback = _tcheck_function_call(ir.function, new_param_cache)
        #deal with return value (single) TODO
        for x in ir.function.returns_ssa:
            print(x.name)
            print("&&")
        if(len(ir.function.returns_ssa)):
            print(ir.function.returns_ssa[0].name)
            type_asn(ir.lvalue, ir.function.returns_ssa[0])
        if(len(addback) != 0):
            return True
    return False

#USAGE: assigns type from dest to sorc
#RETURNS: 'TRUE' if no variables undefined
def type_asn(dest, sorc) -> bool:
    #dest = ir.lvalue
    #sorc = ir.variable_right
    init_var(sorc)
    #asn_norm(dest, get_norm(sorc))
    if(is_type_undef(sorc)):
        return True
    elif(is_type_const(sorc)):
        if(is_type_undef(dest)):
            copy_token_type(sorc, dest)
        return False
    else:
        if(is_type_undef(dest)):
            copy_token_type(sorc, dest)
        elif(not(compare_token_type(sorc, dest))):
            add_errors(dest)
        else:
            return False
    return False
    
#USAGE: assign type from dest to sorc, but additive
#RETURNS: 'TRUE' if the type assign is successful (maybe not used consider removing TODO)
def type_asna(dest, sorc) -> bool:
    init_var(sorc)
    if(is_type_undef(sorc)):
        return False
    else:
        copy_token_type(sorc, dest)
        return True

#USAGE: assign type from dest to sorc, but additive and inverse
#RETURNS: 'TRUE' if the type assign is successful (maybe not used consider removing TODO)
def type_asnai(dest, sorc)->bool:
    init_var(sorc)
    if(is_type_undef(sorc)):
        return False
    else:
        copy_inv_token_type(sorc, dest)
        return True

#USAGE: initializes a variable for typechecking
#RETURNS: NULL
def init_var(ir):
    if(not(is_variable(ir))):
        return False
    if(is_constant(ir)):
        assign_const(ir)
    else:
        convert_ssa(ir)
    return True
    #print_token_type(ir)
    #print("^^^^")


#%dev returns true if the ir needs to be added back also initializes norms
#false otherwise
def type_bin(ir) -> bool:

    if (ir.type == BinaryType.ADDITION):
        return type_bin_add(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.SUBTRACTION):
        return type_bin_sub(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.MULTIPLICATION):
        return type_bin_mul(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.DIVISION):
        return type_bin_div(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.POWER):
        return type_bin_pow(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.GREATER):
        return type_bin_gt(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.GREATER_EQUAL):
        return type_bin_ge(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.LESS):
        return type_bin_lt(ir.lvalue, ir.variable_left, ir.variable_right)
    elif (ir.type == BinaryType.LESS_EQUAL):
        return type_bin_le(ir.lvalue, ir.variable_left, ir.variable_right)
    return False

#USAGE: typechecks power statements
#RETURNS 'True' if needs to be added back
def type_bin_pow(dest, lir, rir) -> bool:
    if(not (init_var(lir) and init_var(rir))):
        return False
    #don't assign norm yet
    print_token_type(lir)
    print_token_type(rir)
    if(is_type_undef(lir) or is_type_undef(rir)):
        return True
    pow_const = -1
    print_token_type(dest) 
    if(is_constant(rir)):
        pow_const = rir.value
    if(is_type_const(lir)):
        assign_const(dest)
        print("x:" + str(get_norm(dest)))
        print(pow_const)
        if(pow_const != -1):
            asn_norm(dest, pow_const * get_norm(lir))
        else:
            asn_norm(dest, -102)
    else:
        type_asn(dest, lir)
        if(pow_const != -1):
            if(pow_const > 0):
                asn_norm(dest, pow_const * get_norm(lir))
                for i in range (pow_const-1):
                    type_asna(dest, lir)
            else:
                asn_norm(dest, -pow_const * get_norm(rir))
                for i in range(pow_const-1):
                    type_asnai(dest, lir)
        else:
            asn_norm(dest, -102)
    return False
#USAGE: typechecks addition statements
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_add(dest, lir, rir) -> bool:
    #dest = ir.lvalue
    #lir = ir.variable_left
    #rir = ir.variable_right
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    asn_norm(dest, get_norm(rir))
    if(is_type_undef(lir) or  is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir)):
        return type_asn(dest, rir)
    elif(is_type_const(rir)):
        return type_asn(dest, lir)
    elif(not(compare_token_type(rir, lir))):
        #report error, default to left child
        
        add_errors(dest)
        return False
    else:
        return type_asn(dest, lir)

#USAGE: typechecks subtraction statements
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_sub(dest, lir, rir) -> bool:
    #dest = ir.lvalue
    #lir = ir.variable_left
    #rir = ir.variable_right
    #print_token_type(lir)
    #print_token_type(rir)
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    asn_norm(dest, get_norm(rir))
    print_token_type(lir)
    print_token_type(rir)
    if(is_type_undef(lir) or  is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir)):
        return type_asn(dest, rir)
    elif(is_type_const(rir)):
        return type_asn(dest, lir)
    elif(not(compare_token_type(rir, lir))):
        #report error, default to left child
        add_errors(dest)
        return False
    else:
        return type_asn(dest, lir)

#USAGE: given a constant, determine the number of powers of 10 that it includes
#RETURNS: the powers of 10 in the constant, if not, returns -1
def get_norm(ir):
    power = -1
    if(not(is_variable(ir))):
        return 0
    if(not(is_constant(ir))):
        if(-100 == ir.norm):
            return 0
        return ir.norm
    else:
        print("val: " + str(ir.value))
        if(ir.value % 10 != 0):
            return power+1
        power = 0
        copy_val = ir.value
        while (copy_val > 0 and copy_val%10 == 0):
            copy_val = copy_val/10
            power+=1
        print(power)
        return power
            
#USAGE: given a power of 10 (norm), assign it to the dest IR
#       can be toggled to throw an error if there is a previous type
#       can also be toggled to be additive (i.e. increase norm)
#RETURNS: NULL  TODO split and deprecate
def assign_norm(ir, norm, check_equal, additive, assign):
    #initialize
    init = False
    if(not(is_variable(ir))):
        return 
    if(ir.norm == -100 or assign):
        ir.norm = norm
    else:
        init = True
    if(check_equal):
        if(ir.norm != norm):
            add_errors(ir)
        return
    if(additive and (init)):
        temp = ir.norm+norm
        ir.norm = temp
    return
    
#USAGE: if norm uninitialized, initializes norm (0)
#       if initialized, check against norm and throw error
#RETURNS: NULL
def asn_norm(ir, norm):
    if(not(is_variable(ir))):
        return
    if(ir.norm == -100):
        ir.norm = norm
    else:
        if(ir.norm != norm):
            add_errors(ir)

#USAGE: append norm (i.e. for multiplication, division, or power)
#RETURNS: NULL
def add_norm(ir, norm):
    if(not(is_variable(ir))):
        return
    temp = ir.norm
    temp+=norm
    ir.norm = temp
    return


#USAGE: typechecks a multiplication statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_mul(dest, lir, rir) ->bool:
    #typecheck -> 10*A + B
    print("testing mul...")
    if(not (init_var(lir) and init_var(rir))):
        return False
    print("---")
    print_token_type(lir)
    asn_norm(dest, get_norm(lir))
    print("r")
    print_token_type(rir)
    add_norm(dest, get_norm(rir))
    print("***")
    print(is_type_undef(lir))
    print(is_type_undef(rir))
    print(is_type_const(lir))
    print(is_type_const(rir))
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir)):
        return type_asn(dest, rir)
    elif(is_type_const(rir)):
            
        return type_asn(dest, lir)
    else:
        type_asn(dest, lir)
        type_asna(dest, rir)
        if(is_type_undef(dest)):
            assign_const(dest)
        return False

#USAGE: typechecks a division statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_div(dest, lir, rir) ->bool:
    #typecheck -> 10*A + B
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    add_norm(dest, get_norm(rir))
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir)):
        return type_asn(dest, rir)
    elif(is_type_const(rir)):
        return type_asn(dest, lir)
    else:
        type_asn(dest, lir)
        type_asnai(dest, rir)
        if(is_type_undef(dest)):
            assign_const(dest)
        return False

#USAGE: typechecks '>' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_gt(dest, lir, rir) -> bool:
    print("testing gt...")
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    asn_norm(dest, get_norm(rir))
    print_token_type(rir)
    print(is_type_const(rir))
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant (although it should not be used in arithmatic)
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir))):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

#USAGE: typechecks '>=' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_ge(dest, lir, rir) -> bool:
    print("testing gt...")
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    asn_norm(dest, get_norm(rir))
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant (although it should not be used in arithmatic)
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir))):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

#USAGE: typechecks '<' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_lt(dest, lir, rir) -> bool:
    print("testing lt...")
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    asn_norm(dest, get_norm(rir))
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant (although it should not be used in arithmatic)
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir))):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

#USAGE: typechecks '<=' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_le(dest, lir, rir) -> bool:
    print("testing lt...")
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    asn_norm(dest, get_norm(rir))
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant (although it should not be used in arithmatic)
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir))):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

def is_variable(ir):
    if isinstance(ir, Variable):
        #print("This is a variable: "+ir.name.lower())
        #print_token_type(ir)
        return True
    return False

def is_division(ir) -> bool:
    #print("division found")
    if isinstance(ir, Binary):
        if ir.type == BinaryType.DIVISION:
            return True

    if isinstance(ir, LibraryCall):
        if ir.function.name.lower() in [
            "div",
            "safediv",
        ]:
            if len(ir.arguments) == 2:
                if ir.lvalue:
                    return True
    return False

def is_addition(ir) -> bool:
    #print("addition found")
    if isinstance(ir, Binary):
        if ir.type == BinaryType.ADDITION:
            return True
    if isinstance(ir, LibraryCall):
        if ir.function.name.lower() in [
                "add",
                "safeadd",
        ]:
            if len(ir.arguments) == 2:
                if ir.lvalue:
                    return True
    return False

def is_internalcall(ir):
    if isinstance(ir, InternalCall):
        print("Internal call...")

def is_multiplication(ir):
    if isinstance(ir, Binary):
        if ir.type == BinaryType.MULTIPLICATION:
            return True

    if isinstance(ir, LibraryCall):
        if ir.function.name.lower() in [
            "mul",
            "safemul",
        ]:
            if len(ir.arguments) == 2:
                if ir.lvalue:
                    return True
    return False

#def contains_equal(ir):
#    if isinstance(ir, Binary):
#        if ir.type == BinaryType.
def is_assert(node):
    if node.contains_require_or_assert():
        return True
    # Old Solidity code where using an internal 'assert(bool)' function
    # While we dont check that this function is correct, we assume it is
    # To avoid too many FP
    if "assert(bool)" in [c.full_name for c in node.internal_calls]:
        return True
    return False

# _exploreNon also checks from rounding + 1
def _exploreNon(to_explore, rurd, roundup, additions, add_constants):  # pylint: disable=too-many-branches
    explored = set()
    divisions = defaultdict(list)
    print("TCHECK RUNNING=================================")
    while to_explore:  # pylint: disable=too-many-nested-blocks
        node = to_explore.pop()
        if node in explored:
            continue
        explored.add(node)
        equality_found = False
        last_var = None
        # List of nodes related to one bug instance
        for ir in node.irs:
            #print(ir)
            #is_referenceVariable(ir)
            #is_constant(ir)
            if isinstance(ir, Assignment):
                last_var = ir.lvalue
                if add_constants[last_var] == None:
                    add_constants[last_var] = []
            if is_addition(ir):
                if(not isinstance(ir.lvalue, TemporaryVariable)):
                    last_var = ir.lvalue
                    if add_constants[last_var] == None:
                        add_constants[last_var] = []
                    #print(last_var)
            if is_division(ir):
                if(not isinstance(ir.lvalue, TemporaryVariable)):
                    last_var = ir.lvalue
                    if add_constants[last_var] == None:
                        add_constants[last_var] = []
                    if divisions[last_var] == None:
                        divisions[last_var] = []
                    divisions[last_var]+=[ir.lvalue]
                        
        for ir in node.irs:
            # check for Constant, has its not hashable (TODO: make Constant hashable)
            if isinstance(ir, Assignment) and not isinstance(ir.rvalue, Constant):
                if ir.rvalue in additions:
                    # Avoid dupplicate. We dont use set so we keep the order of the nodes
                    if node not in additions[ir.rvalue]:
                        additions[ir.lvalue] = additions[ir.rvalue] + [node]
                    else:
                        additions[ir.lvalue] = additions[ir.rvalue]
            if is_addition(ir) and divisions[last_var] != None:
                add_arguments = ir.read if isinstance(ir, Binary) else ir.arguments
                for r in add_arguments:
                    if(r == 1):
                        rurd.append([node])
                        break
            if is_division(ir) and last_var != None:
                #print(additions)
                add_arguments = ir.read if isinstance(ir, Binary) else ir.arguments
                nodes = []
                div_l = ir.lvalue
                div_r = ir.variable_right
                flag = True
                nodes = []
                for r in add_arguments:
                    #if not isinstance(r, Constant) and (r in additions):
                    if (r in additions):
                        for c in add_constants[r]:
                            print(c.value)
                            if(c.value>div_r.value/2 and c.value<=div_r.value):
                                # Dont add node already present to avoid dupplicate
                                # We dont use set to keep the order of the nodes
                                #print("in additions??: "+ r)
                                flag = False
                                break
                        if not flag:
                            break
                if flag:
                    print("RURD: ", (last_var.name))
                    print(rurd)
                    print(roundup)
                if flag and [last_var.name] in roundup and not isinstance(last_var, LocalVariable):
                    #if not last_var.name in rurd:
                    #    rurd+=[last_var.name]
                    #    print("Roundup round down detected: " , (last_var))
                    #rurd+=[node]
                    #if node in additions[r]:
                    #    nodes += [n for n in additions[r] if n not in nodes]
                    #else:
                    #    nodes += [n for n in additions[r] + [node] if n not in nodes]
                    print(node)
                    rurd.append([node])
        for son in node.sons:
            to_explore.add(son)

#USAGE: given a list of irs, typecheck
#RETURNS: a list of irs that have undefined types
def _tcheck_ir(irs, function_name) -> []:
    #irs is the list of irs
    newirs = []
    for ir in irs:
        # irs are expressions in the form of a = b op c
        print(ir)
        is_function(ir)
        if isinstance(ir, Function):
            print("Function...")
            continue
        if isinstance(ir, Return):
            print("Return...")
            print(ir.function.name)
            for x in ir.function.returns_ssa:
                print(x)
            ir.function.clear_returns_ssa()
            for y in ir.values:
                ir.function.add_return_ssa(y)
            for x in ir.function.returns_ssa:
                print(x)
            continue
        if isinstance(ir, Condition):
            print("Condition...")
            is_condition(ir)
            continue
        if isinstance(ir, EventCall):
            continue
        if isinstance(ir, InternalCall):
            print("Internal call...")
            print(ir.function)
            for param in ir.read:
                print(param.name)
            is_function(ir.function)
            check_type(ir)
            continue
        is_high_level_call(ir)
        is_referenceVariable(ir.lvalue)
        is_constant(ir.lvalue)
        is_temporary(ir.lvalue)
        is_space(ir.lvalue)
        is_state(ir.lvalue)
        is_local(ir.lvalue)
        is_tuple(ir.lvalue)
        is_function_type_variable(ir.lvalue)
        if function_name != None and ir.lvalue != None and is_variable(ir.lvalue):
            ir.lvalue.parent_function = function_name
            print("Function name: "+ ir.lvalue.parent_function)
        addback = check_type(ir)
        is_variable(ir.lvalue)
        if(addback):
            newirs.append(ir)
    return newirs

#USAGE: typecheck a node
#RETURNS: list of IR with undefined types
def _tcheck_node(node, function_name) -> []:
    print("typecheckig node...")
    irs = []
    for ir in node.irs_ssa:
        irs.append(ir)
    newirs = _tcheck_ir(irs, function_name)
    if(len(newirs) > 0):
        print("[x]node added back")
    return newirs

#USAGE: typecheck a function call
#       given a param_cache for the input data
#       check return values:
#RETURNS: list of nodes with undefined types
def _tcheck_function_call(function, param_cache) -> []:
    global function_hlc
    global function_ref
    function_hlc = 0
    function_ref = 0
    explored = set()
    addback_nodes = []
    if(check_bar(function.name)):
        return addback_nodes
    print("Function name: "+function.name)
    print("Function Visibility: "+function.visibility)
    #load parameters
    paramno = 0
    for param in function.parameters:
        #clear previous types
        #copy new types
        copy_pc_token_type(param_cache[paramno], param)
        is_variable(param)
        #param.parent_function = function.name
        paramno+=1
    #typecheck function
    fentry = {function.entry_point}
    while fentry:
        node = fentry.pop()
        if node in explored:
            continue
        explored.add(node)
        addback = _tcheck_node(node, function.name)
        if(len(addback) > 0):
            addback_nodes.append(node)
        for son in node.sons:
            fentry.add(son)

    #check return value
    print("Checking return value" + function.name)
    freturns = function.returns_ssa
    #for retval in freturns:
        #print(retval.ssa_name)
        #is_variable(retval)
    return addback_nodes

#USAGE: typecheck a function
#       if external or public function, prompt user for types (local variable parameters)
#       no need to care about the function return values here (these check from external calls)
#RETURNS: list of nodes with undefined types
def _tcheck_function(function) -> []:
    global function_hlc
    global function_ref
    function_hlc = 0
    function_ref = 0
    explored = set()
    addback_nodes = []
    if(check_bar(function.name)):
        print("wooo")
        return addback_nodes
    print("Function name: "+function.name)
    print("Function Visibility: "+function.visibility)
    fvisibl = function.visibility
    if(fvisibl == 'public' or fvisibl == 'external' or read_internal):
        for fparam in function.parameters:
            print(fparam.name)
            fparam.parent_function = function.name
            querry_type(fparam)
        #generate param_cache
        new_param_cache = function_param_cache(function)
        added = add_param_cache(function, new_param_cache)
        print_param_cache(new_param_cache)
    else:
        #do not care about internal functions in initial iteration
        return addback_nodes
    fentry = {function.entry_point}
    while fentry:
        node = fentry.pop()
        if node in explored:
            continue
        explored.add(node)
        addback = _tcheck_node(node, function.name)
        if(len(addback) > 0):
            addback_nodes.append(node)
        for son in node.sons:
            fentry.add(son)
    return addback_nodes

def _explore(to_explore, f_results, v_results,  additions, add_constants):  # pylint: disable=too-many-branches
    explored = set()
    while to_explore:  # pylint: disable=too-many-nested-blocks
        node = to_explore.pop()

        if node in explored:
            continue
        explored.add(node)

        equality_found = False
        # List of nodes related to one bug instance
        node_results = []
        var_results = []
        last_var = None
        print("node changexxxx")
        for ir in node.irs:
            # irs are expressions in the form of a = b op c
            print(ir)
            is_function(ir)
            if isinstance(ir, Function):
                print("Function...")
                continue
            if isinstance(ir, Return):
                print("Return...")
                continue
            if isinstance(ir, InternalCall):
                print("Internal call...")
                print(ir.function)
                #print(ir.read)
                for param in ir.read:
                    print(param.name)
                    #print(param.token_type)
                is_function(ir.function)
                continue
            addback = check_type(ir)
            is_referenceVariable(ir.lvalue)
            is_constant(ir.lvalue)
            is_temporary(ir.lvalue)
            is_space(ir.lvalue)
            is_state(ir.lvalue)
            is_local(ir.lvalue)
            is_tuple(ir.lvalue)
            is_variable(ir.lvalue)
            #check_type(ir)
            if is_addition(ir):
                print("ADDITION")
            if isinstance(ir, Assignment):
                #print("assignment found")
                last_var = ir.lvalue
                if add_constants[last_var] == None:
                    add_constants[last_var] = []
                #print(last_var)
            if is_addition(ir):
                if(isinstance(ir.lvalue, ReferenceVariable)):
                    print("ir is reference")
                if(not isinstance(ir.lvalue, TemporaryVariable)):
                    #print("ir is not temporary")
                    last_var = ir.lvalue
                    if add_constants[last_var] == None:
                        add_constants[last_var] = []
                if is_division(ir) and last_var != None:
                    if(not isinstance(ir.lvalue, TemporaryVariable)):
                        last_var = ir.lvalue
                        if add_constants[last_var] == None:
                            add_constants[last_var] = []
        print("MRA: ", (last_var))
        for ir in node.irs:
            # check for Constant, has its not hashable (TODO: make Constant hashable)
            if isinstance(ir, Assignment) and not isinstance(ir.rvalue, Constant):
                if ir.rvalue in additions:
                    # Avoid dupplicate. We dont use set so we keep the order of the nodes
                    if node not in additions[ir.rvalue]:
                        additions[ir.lvalue] = additions[ir.rvalue] + [node]
                    else:
                        additions[ir.lvalue] = additions[ir.rvalue]
                    
            if is_addition(ir):
                additions[ir.lvalue] = [node]
                if isinstance(ir.variable_left, Constant):
                    add_constants[last_var]+=[ir.variable_left]
                if isinstance(ir.variable_right, Constant):
                    #print("right var aded")
                    add_constants[last_var]+=[ir.variable_right]
            if is_division(ir):
                #print(additions)
                
                add_arguments = ir.read if isinstance(ir, Binary) else ir.arguments
                nodes = []
                div_l = ir.lvalue
                div_r = ir.variable_right
                for r in add_arguments:
                    print ("args",  r)
                    #print("-----")
                    #print (add_constants[r])
                    #if not isinstance(r, Constant) and (r in additions):
                    if (r in additions):
                        for c in add_constants[r]:
                            print(c.value)
                            if(c.value>div_r.value/2 and c.value<=div_r.value):
                                # Dont add node already present to avoid dupplicate
                                # We dont use set to keep the order of the nodes
                                #print("in additions??: "+ r)
                                if not last_var in var_results:
                                    print("Round up var added:", (last_var))
                                    var_results+=[last_var.name]
                                if node in additions[r]:
                                    nodes += [n for n in additions[r] if n not in nodes]
                                else:
                                    nodes += [n for n in additions[r] + [node] if n not in nodes]
                                break
                if nodes:
                    node_results = nodes

            if isinstance(ir, Binary) and ir.type == BinaryType.EQUAL:
                equality_found = True

        if node_results:
            # We do not track the case where the multiplication is done in a require() or assert()
            # Which also contains a ==, to prevent FP due to the form
            # assert(a == b * c + a % b)
            if not (is_assert(node) and equality_found):
                f_results.append(node_results)
        if var_results:
            v_results.append(var_results)
        for son in node.sons:
            to_explore.add(son)

#USAGE: typechecks state (global) variables given a contract
#RETURNS: whether or not the state variable need to be added back.
#         the result is always 'FALSE' (querried)
def _tcheck_contract_state_var(contract):
    for state_var in _read_state_variables(contract):
        print("State_var: "+state_var.name)
        state_var.parent_function = "global"
        if(is_type_undef(state_var)):
            querry_type(state_var)

#USAGE: labels which contracts that should be read (contains binary operations)
#RTURNS: NULL
def _mark_functions(contract):
    for function in contract.functions_declared:
        print("Checking... " + function.name)
        if(not (function.entry_point and (read_internal or function.visibility == "external" or function.visibility == "public"))):
            print("[x] Not visible ")
            continue
        fentry = {function.entry_point}
        contains_bin = False
        while fentry:
            node = fentry.pop()
            for ir in node.irs_ssa:
                if(isinstance(ir, Binary)):
                    contains_bin = True
                    break
                if(ir.function and (ir.function.name == "add" or ir.function.name == "sub" or ir.function.name == "mul" or ir.function.name == "div")):
                    contains_bin = True
                    break
                if(isinstance(ir, InternalCall)):
                    if(function_check.get(ir.function.name)):
                        containus_bin = True
                        break
            if contains_bin:
                break
            for son in node.sons:
                fentry.add(son)
        function_check[function.name] = contains_bin
        if contains_bin:
            print("[o] Marked")
        else:
            print("[x] No Binary")


#TODO--------------------------------------------------------
# USAGE: typechecks an entire contract given the contract
#        generates a list of nodes that need to be added back
# RETURNS: returns a list of errors(if any)
def _tcheck_contract(contract):
    #contract is the contract passed in by Slither
    global errors
    all_addback_nodes = []
    _mark_functions(contract)
    _tcheck_contract_state_var(contract)
    for function in contract.functions_declared:
        print("Reading Function: " + function.name)
        if not function_check[function.name]:
            print("Function " + function.name + " not marked")
            continue
        if not function.entry_point:
            continue
        addback_nodes = _tcheck_function(function)
        if(len(addback_nodes) > 0):
            all_addback_nodes+=(addback_nodes)
    cur = 0    
    while all_addback_nodes:
        print("------")
        cur_node = all_addback_nodes.pop()
        addback = _tcheck_node(cur_node, None)
        if(len(addback) > 0):
            all_addback_nodes.append(cur_node)
        if(cur == 5):
            break
        cur+=1
    return errors

#USAGE: returns the state variables of a contract
#RETURNS: the state variables of a contract
def _read_state_variables(contract):
    ret = []
    for f in contract.all_functions_called + contract.modifiers:
        ret += f.state_variables_read
    return ret

def detect_add_b4_div(contract):
    results = []
    v_results = []
    rurd = []
    for function in contract.functions_declared:
        print("NEW FUNCTION @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@: " + function.name)
        if not function.entry_point:
            continue
        f_results = []
        #v_results = []
        additions = defaultdict(list)
        add_constants = defaultdict(list)
        _explore({function.entry_point}, f_results, v_results, additions, add_constants)
        #print("V_RESULTS:______________________________")
        #for v in v_results:
        #    print(v)
        #_exploreNon({function.entry_point}, rurd, v_results, additions, add_constants)
        for f_result in rurd:
            
            results.append((function, f_result))
    return results
class tcheck(AbstractDetector):
    """
    Detects round up round down functions
    """

    ARGUMENT = 'tcheck' # slither will launch the detector with slither.py --detect mydetector
    HELP = 'Help printed by slither'
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = 'Initialized i guess?'

    WIKI_TITLE = 'woops'
    WIKI_DESCRIPTION = 'i am initializing'
    WIKI_EXPLOIT_SCENARIO = 'finding external'
    WIKI_RECOMMENDATION = 'i will do something later'

    def _detect(self):
        results = []
        global user_type
        global type_file
        global line_no
        for contract in self.contracts:
            #TODO
            print("contract name: "+contract.name)
            type_info_name = contract.name+"_types.txt"
            print(type_info_name)
            #get type information from file (if there is one)
            try:
                with open(type_info_name, "r") as t_file:
                    # File processing code goes here
                    print("\"" + type_info_name +"\" opened successfully.")
                    user_type = False
                    type_file = type_info_name
                    parse_type_file(type_file)
                    #print("oooo")
            except FileNotFoundError:
                print("Type File not found.")
                # Handle the error gracefully or take appropriate action
                user_type = True
            if(not (check_contract(contract.name))):
                continue
            errors = _tcheck_contract(contract)
            #print("xxxxxx")
            if errors:
                for ir in errors:
                    name = ir.name
                    func = ir.parent_function
                    info = [" typecheck error: " ]
                    info+=("Var name: " + name + " " + "Func name: " + func + "\n")
                    res = self.generate_result(info)
                    results.append(res)
            #add_b4_div = detect_add_b4_div(contract)
            #if add_b4_div:
            #    for (func, nodes) in add_b4_div:
            #        info = [
            #                func,
            #                " typechecking for smart contracts"         
            #        ]
            #        nodes.sort(key = lambda x:x.node_id)
            #        for node in nodes:
            #            info += ["\t= ", node, "\n"]
            #        res = self.generate_result(info)
            #        results.append(res)

        return results
