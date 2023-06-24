from collections import defaultdict
from slither.core.variables.local_variable import LocalVariable
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import Binary, Assignment, BinaryType, LibraryCall, Return, InternalCall, Condition, HighLevelCall, Unpack, Phi, EventCall, TypeConversion, Member, Index
from slither.slithir.variables import Constant, ReferenceVariable, TemporaryVariable, LocalIRVariable, StateIRVariable, TupleVariable
from slither.core.variables.variable import Variable
from slither.core.variables.state_variable import StateVariable
from slither.core.declarations.function import Function
from slither.core.variables.local_variable import LocalVariable
from slither.core.variables.function_type_variable import FunctionTypeVariable
import linecache
import os
import sys
script_dir = os.path.dirname( __file__ )
sys.path.append(script_dir)
import tcheck_parser
import tcheck_propagation

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
current_contract_name = "ERR"
type_hashtable = {}
function_bar = {}
function_check = {}
contract_run = {}
contract_function = {}

#IMPORTANT: read internal
read_internal = False

#USAGE: adds token pair to type_hashtable
#RETURNS: composite key of the token pair
def add_hash(function_name, var_name, num, den, norm, lf):
    composite_key = function_name + '_' + var_name
    values = (num, den, norm, lf)
    type_hashtable[composite_key] = values
    return composite_key

#USAGE: adds a contract, function pair
#RETURNS: NULL
def add_cf_pair(contract_name, function_name, function):
    if(contract_name == None or function_name == None):
        return False
    tcheck_parser.add_in_func(contract_name, function_name, function)

#USAGE: returns the ir for a contract, function pair
#RETURNS: the specified ir, if it doesn't exist, None is returned
def get_cf_pair(contract_name, function_name):
    if(contract_name == None or function_name == None):
        return None
    return tcheck_parser.get_in_func_ptr(contract_name, function_name)

#USAGE: adds a tuple to the parser file
#RETURNS: NULL
def add_tuple(tuple_name, type_tuples):
    tcheck_parser.add_tuple(tuple_name, type_tuples)

#USAGE: returns a specific element located at index of a tuple
#RETURNS: above
def get_tuple_index(tuple_name, index):
    temp = tcheck_parser.get_tuple(tuple_name)
    if(temp != None and len(temp) > index):
        return temp[index]
    return None

#USAGE: adds a referecne
#RETURNS: NULL
def add_ref(ref_name, type_tuple):
    if(ref_name != None):
        tcheck_parser.add_ref(ref_name, type_tuple)

#USAGE: gets the type of a reference
#RETURNS:
def get_ref(ref_name):
    return tcheck_parser.get_ref_type_tuple(ref_name)

#USAGE: given a function name and a var name, return the token pair
#RETURNS: tuple holding the token pair
def get_hash(function_name, var_name):
    return tcheck_parser.get_var_type_tuple(function_name, var_name)

#USAGE: bar a function from being typechecked
#RETURNS: NULL
def bar_function(function_name):
    tcheck_parser.bar_function(function_name)

#USAGE: returns if a function should be typechecked
#RETURNS bool
def check_bar(function_name):
    return tcheck_parser.check_function(function_name)

#USAGE: selects a  contract to typecheck
#RETURNS: NULL
def run_contract(contract_name):
    tcheck_parser.allow_contract(contract_name)

#USAGE: returns the type tuple for an external function that has been included
#RETURNS: external function type tuple
def get_external_type_tuple(contract_name, function_name, parameters):
    if(contract_name ==None or function_name == None):
        return None
    for p in parameters:
        convert_ssa(p)
        #print_token_type(p)
    return tcheck_parser.get_ex_func_type_tuple(contract_name, function_name, parameters)


#USAGE: returns if a function should be typechecked
#RETURNS bool
def check_contract(contract_name):
    if(tcheck_parser.check_contract(contract_name)):
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
    if(ir.link_function != None):
        print("Linked function: " + ir.link_function)

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
    return(gen_param_cache(ir.read))

#USAGE: given a function, generate a param_cache
#RETURNS: returns a param_cache
def function_param_cache(function):
    #assumes types have already been assigned
    return(gen_param_cache(function.parameters))

#USAGE: given a hlc function, generate a param_cache
#RETURNS: returns a param_cache
def function_hlc_param_cache(function):
    #assumes types have already been assigned
    return(gen_param_cache(function.arguments))

#USAGE: given a list of parameters, return a param_cache (merge function_param_cache, function_call param_cache, and function_hlc_param_cache
#RETURNS: a para_cache
def gen_param_cache(param_list):
    param_cache = []
    for param in param_list:
        num = param.token_typen
        den = param.token_typed
        norm = param.norm
        link_function = param.link_function
        param_type = [num, den, norm, link_function]
        param_cache.append(param_type)
    return param_cache


#USAGE: given a param_cache, decide whether or not to add it to the parameter_cache
#        of a function
#RETURNS: bool (added or not)
def add_param_cache(function, new_param_cache):
    global maxTokens
    add_param = False
    fpc = function.parameter_cache()
    match_param = -100
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
        if(add_cur_param == False):
            add_param = False
            match_param = a
            break
    print(match_param)
    if(add_param):
        function.add_parameter_cache(new_param_cache)
    return match_param

#USAGE: parses an input file and fills the type_hashtable
#RETURNS: NULL
#parse formula:
#function_name
#var_name
#num
#den
def parse_type_file(t_file):
    tcheck_parser.parse_type_file(t_file)

#USAGE: given a variable ir, return the type tuple
#RETURNS: type tuple
def read_type_file(ir):
    function_name = ir.parent_function
    var_name = ir.name
    if(ir.tname != None):
        var_name = ir.tname
    #print("read function name: " + function_name)
    #print("read parent name: " + ir.name)
    return tcheck_parser.get_var_type_tuple(function_name, var_name)

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
            ir.token_typen.clear()
            ir.token_typed.clear()
            num = type_tuple[0]
            den = type_tuple[1]
            norm = type_tuple[2]
            lf = type_tuple[3]
            ir.add_token_typen(num)
            ir.add_token_typed(den)
            if(norm == -101):
                #fill as constant
                ir.norm = get_norm(ir)
            else:
                ir.norm = norm
            if(lf != None):
                ir.link_function = lf
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
    if(str(ir.type) == "address"):
        print("Define Linked Contract Name for \"" + uxname + "\": ")
        input_str = input()
        ir.link_function = input_str
    print(ir.token_type)
    #add to parser file? TODO Priority: Low

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

#USAGE: copies all the types from a type tuple to an ir node
#RETURNS: null
def copy_token_tuple(ir, tt):
    print("Check copy_toekn_tuple")
    print(tt)
    print_token_type(ir)
    print("----")
    ir.token_typen.clear()
    ir.token_typed.clear()
    if(isinstance(tt[0], int)):
        ir.add_token_typen(tt[0])
    else:
        for n in tt[0]:
            ir.add_token_typen(n)
    if(isinstance(tt[1], int)):
        ir.add_token_typed(tt[1])
    else:
        for d in tt[1]:
            ir.add_token_typed(d)
    ir.norm = tt[2]
    ir.link_function = tt[3]
    print_token_type(ir)

#USAGE: copies all token types from the 'src' ir node to the 'dest' ir node
#RETURNS: null
def copy_token_type(src, dest):
    #dest.token_typen.clear()
    #dest.token_typed.clear()
    for n in src.token_typen:
        dest.add_token_typen(n)
    for d in src.token_typed:
        dest.add_token_typed(d)
    if(src.link_function != None):
        dest.link_function = src.link_function

#USAGE: copies inverse token types from the 'src' ir node from the 'dest' ir node
#RETURNS: null
def copy_inv_token_type(src, dest):
    for n in src.token_typen:
        dest.add_token_typed(n)
    for d in src.token_typed:
        dest.add_token_typen(d)
    if(src.link_function != None):
        dest.link_function = src.link_function

#USAGE: copy and replace a token from a param_cache to an ir
#RETURNS: nN/A
def copy_pc_token_type(src, dest):
    dest.token_typen.clear()
    dest.token_typed.clear()
    for n in src[0]:
        dest.add_token_typen(n)
    for d in src[1]:
        dest.add_token_typed(d)
    if(src[3] != None):
        dest.link_function = src[3]


def compare_token_type(src, dest):
    return tcheck_propagation.compare_token_type(src, dest)
    """seen = []
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
    return True"""

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
    if(not (is_type_undef(non_ssa_ir))): # and is_type_undef(ir)):
        ir.token_typen.clear()
        ir.token_typed.clear()
        copy_token_type(non_ssa_ir, ir)
        #print_token_type(ir)
        ir.norm = non_ssa_ir.norm
        ir.link_function = non_ssa_ir.link_function

#USAGE: updates a non_ssa instance of a variable
#RETURNS: NULL
def update_non_ssa(ir):
    if(not(is_variable(ir))):
        return
    if(is_constant(ir)):
        return
    #if(not(ir.ssa_name)):
    #    return
    non_ssa_ir = ir.non_ssa_version
    #name = ir.ssa_name
    if(not (is_type_undef(ir))):
        non_ssa_ir.token_typen.clear()
        non_ssa_ir.token_typed.clear()
        copy_token_type(ir, non_ssa_ir)
        #print_token_type(ir)
        non_ssa_ir.norm = ir.norm
        non_ssa_ir.link_function = ir.link_function

#edit checkdafadjfahjfa

#given and ir, type check
#currently handles assignments and Binary
#returns ir if needs to be added back
def check_type(ir) -> bool:
    addback = False;
    #Assignmnet
    if isinstance(ir, Assignment):
        print("asgn")
        addback = type_asn(ir.lvalue, ir.rvalue)
        print(get_norm(ir.rvalue))
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
    elif isinstance(ir, TypeConversion):
        convert_ssa(ir.lvalue)
        convert_ssa(ir.variable)
        if(str(ir.variable) == "this"):
            #TMPxxx  CONVERT address(this)
            assign_const(ir.lvalue)
            ir.lvalue.norm = 0
            ir.lvalue.link_function = current_contract_name
            #addback = copy_token_tuple(ir.lvalue, ir.variable)
            addback = False
        else:    
            addback = type_asn(ir.lvalue, ir.variable)
            asn_norm(ir.lvalue, get_norm(ir.variable))
            ir.lvalue.link_function = ir.variable.link_function
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
    elif isinstance(ir, Index):
        print("INDEX")
        addback = type_ref(ir)
        return False
    elif isinstance(ir, Member):
        print("MEMBER")
        addback = type_member(ir) 
        return False
    elif isinstance(ir, Return):
        print("RETURN")
        for y in ir.values:
            convert_ssa(y)
            print_token_type(y.non_ssa_version)
            ir.function.add_return_ssa(y)
        return False
    #elif(is_variable(ir.lvalue) and is_referenceVariable(ir.lvalue)):
    #    #Reference
    #    addback = type_ref(ir)
    #    return False
    #DEBUG
    if ir.lvalue and is_variable(ir.lvalue):
        print("[i]Type for "+ir.lvalue.name)
        print_token_type(ir.lvalue)
        update_non_ssa(ir.lvalue)
    print("done.")
    if(addback):
        print("This IR caused addback:")
        print(ir)
        print("XXXXX")
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
    tup_token_type = get_tuple_index(str(rtup), rind)
    if(tup_token_type):
        copy_token_tuple(lval, tup_token_type)
    else:
        querry_type(lval)
    return False

#USAGE: typechecks an included external call
#RETURNS: success of typecheck
def type_included_hlc(ir, dest, function):
    #function is the fentry point
    for param in ir.arguments:
        print(param)
        init_var(param)
        if(is_type_const(param)):
            assign_const(param)
        elif(is_type_undef(param)):
            #undefined type
            return 1
    #generate param cache
    new_param_cache = function_hlc_param_cache(ir)
    print("High level cal param_cache")
    print_param_cache(new_param_cache)
    added = add_param_cache(function, new_param_cache)
    if(added == -100):
        print("added")
        addback = _tcheck_function_call(function, new_param_cache)
        #deal with return value (single) TODO
        tuple_types = []
        for x in ir.function.returns_ssa:
            print(x.name)
            print("&&")
            if(isinstance(ir.lvalue, TupleVariable)):
                tuple_types.append((x.token_typen, x.token_typed, x.norm, x.link_function))
            else:
                type_asn(ir.lvalue, x)
                ir.function.add_parameter_cache_return(x)
        if(len(tuple_types) > 0):
            add_tuple(ir.lvalue.name, tuple_types)
            ir.function.add_parameter_cache_return(tuple_types)
        if(len(addback) != 0):
            return 1
    else:
        ret_obj = ir.function.get_parameter_cache_return(added)
        if isinstance(ir, Variable):
            type_asn(ir.lvalue, x)
        else:
            add_tuple(ir.lvalue.name, ret_obj)

    return 2

#USAGE: connects a high-level call with an internal call (cross contract
#       function call where both contracts are defined)
#RETURNS: whether or not the function is detected (0)
#         whether or not the function has any undef types (1)
#         whether or not the function successfully passes (2)
def querry_fc(ir) -> int:
    print("WIP")
    if(not (isinstance(ir, HighLevelCall))):
        return 0
    dest = ir.destination
    convert_ssa(dest)
    func_name = ir.function.name
    cont_name = dest.link_function
    #TODO
    print_token_type(dest)
    if(str(ir.lvalue.type) == "bool"):
        assign_const(ir.lvalue)
        return 2
    if(cont_name != None and func_name != None):
        print("hlc contract name: " + cont_name + " func_name: "+ func_name)
   
    included_func = get_cf_pair(cont_name, func_name)
    if(included_func != None):
        if(type_included_hlc(ir, dest, included_func) == 1):
            print("INCLUDED HIGH LEVEL CALL HAS SOME UNDEFINED TYPE")
            return 1
        return 2

    written_func_rets = get_external_type_tuple(cont_name, func_name, ir.arguments)
    if(written_func_rets != None):
        print("wfc len: " + str(len(written_func_rets)))
        if(len(written_func_rets) == 0):
            #No return value included, default to constant
            convert_ssa(ir.lvalue)
            assign_const(ir.lvalue)
        elif(len(written_func_rets) == 1):
            written_func_ret = written_func_rets[0]
            convert_ssa(ir.lvalue)
            copy_token_tuple(ir.lvalue, written_func_ret)
        elif(isinstance(ir.lvalue, TupleVariable) and len(written_func_rets) > 1):
            add_tuple(ir.lvalue.name, written_func_rets)
        else:
            print("bad function call")
        print("COPIED")
        return 2
    return 0
        

#USAGE: typecheck for high-level call (i.e. iERC20(address).balanceof())
#RETURNS: whether or not the high-level call node should be returned (should always return FALSE)
def type_hlc(ir) ->bool:
    #just query the user for the data (beta)
    global function_hlc
    print("High Call: "+str(ir.function_name))
    print("func name:" + ir.function.name)
    print("other func name:" + str(ir.function_name))
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
    #typecheck abnormal function calls
    res = querry_fc(ir)
    if(res == 2):
        return False
        
    x = "hlc_"+str(function_hlc)
    ir.lvalue.change_name(x)
    print(ir.lvalue.name)
    querry_type(ir.lvalue)
    ir.lvalue.change_name(temp)
    function_hlc+=1
    return False

#USAGE: typechecks Members (i.e. a.b or a.b())
#RETURNS: the type for a (temporary handling, will fix if any issues)
def type_member(ir)->bool:
    if is_type_undef(ir.variable_left):
        print("UNDEFINED LEFT VARIABLE IN MEMBER")
        return True
    copy_token_type(ir.variable_left, ir.lvalue)
    return False

#USAGE: typechecks for references (i.e. a[0])
#RETURNS: always False
def type_ref(ir)->bool:
    print_token_type(ir.variable_left)
    #check for boolean
    if(str(ir.lvalue.type) == "bool"):
        print("REFERENCE IS BOOL TYPE")
        assign_const(ir.lvalue)
        return False

    #check if the right value already has a type?
    if not(is_type_undef(ir.variable_left)):
        print("REFERENCE LEFT VALUE PROPAGATION")
        copy_token_type(ir.variable_left, ir.lvalue)
        return False

    #check if the index of the variable has a type that is not a constant
    if not(is_type_undef(ir.variable_right) or is_type_const(ir.variable_right)):
        print("REFERENCE RIGHT VALUE PROPAGATION")
        copy_token_type(ir.variable_right, ir.lvalue)
        
        return False

    #check the parser for a pre-user-defined type
    print(ir.variable_left.name)
    ref_tuple = get_ref(ir.variable_left.non_ssa_version.name)
    if(ref_tuple != None):
        print("REFERENCE TYPE READ")
        copy_token_tuple(ir.lvalue, ref_tuple)
        return False

    #no other options, just querry the user (try not to let this happen)
    querry_type(ir.lvalue)

    """global function_ref
    print("Ref: "+str(ir.lvalue.name))
    temp = ir.lvalue.name
    ir.lvalue.change_name('ref_'+str(function_ref))
    print("points to: "+ir.lvalue.points_to.name)
    #ir is a 'member' class
    if(isinstance(ir, Member)):
        print("left value name: " + str(ir.variable_left.non_ssa_version.name))
        print("right value name: "+str(ir.variable_right))
    
        #test for 'decimal' propagation
        if(str(ir.variable_right) == "decimals"):
            #a = b.decimals
            prop_decimals(ir.lvalue, ir.variable_left)
            return
        elif(str(ir.variable_left.non_ssa_version.name) == "decimals"):
            #a = decimals[b]
            prop_decimals(ir.lvalue, ir.variable_right)        
            return
    querry_type(ir.lvalue)
    ir.lvalue.change_name(temp)
    function_ref+=1
    return False"""

#USAGE: fills the corresponding ir with the target value's types and decimals
#RETURNS: Null
#Example: a = b.decimals;       a = decimals[b]
def prop_decimals(dest, sorc):
    print("Propagting decimals from "+sorc.name + " to " + dest.name)
    if(is_type_undef(sorc)):
        #source is undefined; just querry the type directly
        querry_type(dest)
    else:
        #copy the token type and also the type
        copy_token_type(sorc, dest)
        asn_norm(dest, get_norm(sorc))

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
    if(added == -100):
        print("added")
        addback = _tcheck_function_call(ir.function, new_param_cache)
        #deal with return value (single) TODO
        handle_return(ir, ir.function)
        """tuple_types = []
        print("IC Saving return values for: " + ir.function.name)
        for x in ir.function.return_values_ssa:
            print(x.name)
            print_token_type(x)
            print("___")
        for x in ir.function.returns_ssa:
            print(x.name)
            print("&&")
            if(isinstance(ir.lvalue, TupleVariable)):
                tuple_types.append((x.token_typen, x.token_typed, x.norm, x.link_function))
            else:
                type_asn(ir.lvalue, x)
                ir.function.add_parameter_cache_return(x)
        if(len(tuple_types) > 0):
            add_tuple(ir.lvalue.name, tuple_types)
            ir.function.add_parameter_cache_return(tuple_types)"""
        if(len(addback) != 0):
            return True
        
    else:
        ret_obj = ir.function.get_parameter_cache_return(added)
        if isinstance(ir, Variable):
            type_asn(ir.lvalue, x)
        else:
            add_tuple(ir.lvalue.name, ret_obj)

    return False

#USAGE: given a function, handle the return values
#RETURNS: NULL
def handle_return(ir, function):
    #dest_ir is optional if there is no return destination
    tuple_types = []
    print("IC Saving return values for: " + function.name)
    for x in function.return_values_ssa:
        print(x.name)
        print_token_type(x)
        type_asn(ir.lvalue, x)
        if(isinstance(ir.lvalue, TupleVariable)):
            tuple_types.append((x.token_typen, x.token_typed, x.norm, x.link_function))
        else:
            type_asn(ir.lvalue, x)
            asn_norm(ir.lvalue, get_norm(x))
            ir.function.add_parameter_cache_return(x)
        print("___")
    if(len(tuple_types) > 0):
        add_tuple(ir.lvalue.name, tuple_types)
        function.add_parameter_cache_return(tuple_types)



#USAGE: assigns type from dest to sorc
#RETURNS: 'TRUE' if no variables undefined
def type_asn(dest, sorc) -> bool:
    #dest = ir.lvalue
    #sorc = ir.variable_right
    init_var(sorc)
    print_token_type(dest)
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
        if(pow_const > 0):
            asn_norm(dest, pow_const * get_norm(lir))
        elif(pow_const == 0):
            asn_norm(dest, pow_const)
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
    print("initlize checks")
    asn_norm(dest, get_norm(lir))
    asn_norm(dest, get_norm(rir))
    print_token_type(lir)
    print_token_type(rir)
    if(is_type_undef(lir) or  is_type_undef(rir)):
        if(is_type_undef(lir)):
            copy_token_type(rir, dest)
        else:
            copy_token_type(lir, dest)
        return True
    elif(is_type_const(lir)):
        return copy_token_type(rir, dest)
    elif(is_type_const(rir)):
        return copy_token_type(lir, dest)
    elif(not(compare_token_type(rir, lir))):
        #report error, default to left child 
        add_errors(dest)
        return False
    else:
        return copy_token_type(tcheck_propagation.greater_abstract(rir, lir), dest)

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
        return type_asn(dest, tcheck_propagation.greater_abstract(rir, lir))

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
        if(power >= 5 or copy_val == 1):
            print(power)
            return power
        return 0
            
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
        type_asna(dest, rir)
        if(is_type_undef(dest)):
            assign_const(dest)
        return False

#USAGE: typechecks a division statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_div(dest, lir, rir) ->bool:
    if(not (init_var(lir) and init_var(rir))):
        return False
    asn_norm(dest, get_norm(lir))
    add_norm(dest, -get_norm(rir))
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
        #print("This is a variable: "+ir.name.lower()+" " + str(ir.type))
        #print_token_type(ir)
        return True
    return False


def is_internalcall(ir):
    if isinstance(ir, InternalCall):
        print("Internal call...")


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
        if isinstance(ir, Return):
            check_type(ir)
            continue
        #is_high_level_call(ir)
        #is_referenceVariable(ir.lvalue)
        #is_constant(ir.lvalue)
        #is_temporary(ir.lvalue)
        #is_space(ir.lvalue)
        #is_state(ir.lvalue)
        #is_local(ir.lvalue)
        #is_tuple(ir.lvalue)
        #is_function_type_variable(ir.lvalue)
        if function_name != None and ir.lvalue != None and is_variable(ir.lvalue):
            ir.lvalue.parent_function = function_name
            print("Function name: "+ ir.lvalue.parent_function)
        addback = check_type(ir)
        #is_variable(ir.lvalue)
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

#USAGE: returns if the ir has a 'lvalue'
#RETURNS: T/F
def has_lvalue(ir):
    if(isinstance(ir, Assignment)):
        return True
    if(isinstance(ir, Binary)):
        return True
    if(isinstance(ir, HighLevelCall)):
        return True
    if(isinstance(ir, LibraryCall)):
        return True
    return False

#USAGE: clears a node
#RETURNS: N/A
def _clear_type_node(node):
    print("clearning node...")
    for ir in node.irs_ssa:
        print("clearing ir...?")
        print(ir)
        if(has_lvalue(ir) and is_variable(ir.lvalue)):
            print("has variable")
            if(isinstance(ir.lvalue, TemporaryVariable) or isinstance(ir.lvalue, LocalIRVariable)):
                #clear the types for temporary and local variables
                ir.lvalue.token_typen.clear()
                ir.lvalue.token_typed.clear()
                ir.lvalue.norm = -100;

                print("[i] " + ir.lvalue.name + " cleared")

#USAGE: searches a function for a RETURN node, if it doesn't exist, do stuff
#RETURNS: return node
def _find_return_function(function):
    fentry = {function.entry_point}
    explored = set()
    print("FIND RETURN")
    print(function.full_name)
    while fentry:
        node = fentry.pop()
        if node in explored: 
            continue
        explored.add(node)
        for ir in node.irs:
            if isinstance(ir, RETURN):
                return node
        
#USAGE: typecheck a function call
#       given a param_cache for the input data
#       check return values:
#RETURNS: list of nodes with undefined types
def _tcheck_function_call(function, param_cache) -> []:
    global function_hlc
    global function_ref
    print("xyz")
    function_hlc = 0
    function_ref = 0
    explored = set()
    addback_nodes = []
    #if(check_bar(function.name)):
    #    return addback_nodes
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
    #find return and tack it onto the end
    #typecheck function
    return_node = None
    fentry = {function.entry_point}
    while fentry:
        node = fentry.pop()
        if node in explored:
            continue
        explored.add(node)
        _clear_type_node(node)
        addback = _tcheck_node(node, function.name)
        if(len(addback) > 0):
            addback_nodes.append(node)
        for son in node.sons:
            temp = True
            if return_node == None:
                for irs in son.irs:
                    if(isinstance(irs, Return)):
                        temp = False
                        return_node = son
                        break
            if(temp):
                fentry.add(son)
    if(return_node):
        _tcheck_node(return_node, function.name)
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
    print("Function Visibility (test): "+function.visibility)
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
        _clear_type_node(node)
        addback = _tcheck_node(node, function.name)
        if(len(addback) > 0):
            addback_nodes.append(node)
        for son in node.sons:
            fentry.add(son)

    #Save return value
    tuple_types = []
    print("Saving return value for " + function.name)
    for x in function.returns_ssa:
        print(x.name)
        print("&&")
        if(len(function.returns_ssa) > 0):
            tuple_types.append((x.token_typen, x.token_typed, x.norm, x.link_function))
        else:
            # type_asn(ir.lvalue, x)
            function.add_parameter_cache_return(x)
    if(len(tuple_types) > 0):
        #add_tuple(ir.lvalue.name, tuple_types)
        function.add_parameter_cache_return(tuple_types)

    return addback_nodes


#USAGE: typechecks state (global) variables given a contract
#RETURNS: whether or not the state variable need to be added back.
#         the result is always 'FALSE' (querried)
def _tcheck_contract_state_var(contract):
    for state_var in _read_state_variables(contract):
        print("State_var: "+state_var.name)
        state_var.parent_function = "global"
        if(is_type_undef(state_var)):
            querry_type(state_var)
            if(isinstance(state_var, ReferenceVariable)):
                add_ref(state_var.name, (state_var.token_typen, state_var.token_typed, state_var.norm, state_var.link_function))

#USAGE: labels which contracts that should be read (contains binary operations) also adds contract-function pairs
#RTURNS: NULL
def _mark_functions(contract):
    for function in contract.functions_declared:
        print("Checking... " + function.name)
        if(not (function.entry_point and (read_internal or function.visibility == "external" or function.visibility == "public"))):
            function_check[function.name] = False
            print("[x] Not visible ")
            continue
        fentry = {function.entry_point}
        #add contract-function pair
        add_cf_pair(contract.name, function.name, function)
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
    global current_contract_name
    current_contract_name = contract.name
    all_addback_nodes = []
    #_mark_functions(contract)
    #_tcheck_contract_state_var(contract)
    for function in contract.functions_declared:
        print("Reading Function: " + function.name)
        if not(function_check[function.name]):
            print("Function " + function.name + " not marked")
            continue
        if not function.entry_point:
            continue
        #SKIP
        #print("[*i*]External Function: " + function.name)
        #continue
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
        u_provide_type = {}
        global user_type
        global type_file
        global line_no
        for contract in self.slither.contracts:
            print(contract.name)
        for contract in self.contracts:
            #TODO: implement x contract function calls and interate through global variables first
            #create hashtable with function name and contract name
            print("contract name: "+contract.name)
            print("WARNING!!!!")
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
                    u_provide_type[contract.name] = False
                    #print("oooo")
            except FileNotFoundError:
                print("Type File not found.")
                # Handle the error gracefully or take appropriate action
                u_provide_type[contract.name] = False
                user_type = True
            if(not (check_contract(contract.name))):
                continue
            #mark functions
            _mark_functions(contract)
            #resolve global variables
            _tcheck_contract_state_var(contract)

        for contract in self.contracts:
            if(not (check_contract(contract.name))):
                continue
            user_type = u_provide_type[contract.name]
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
