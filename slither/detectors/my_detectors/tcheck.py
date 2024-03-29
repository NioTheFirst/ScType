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
from slither.core.declarations.solidity_variables import SolidityVariable
from slither.core.solidity_types import UserDefinedType, ArrayType
from slither.core.declarations import Structure, Contract
from slither.core.solidity_types.elementary_type import ElementaryType
from slither.core.declarations.modifier import Modifier
from slither import tcheck_module
from slither.sctype_cf_pairs import get_cont_with_state_var
import copy
import linecache
import os
import sys
import time
script_dir = os.path.dirname( __file__ )
sys.path.append(script_dir)
import tcheck_parser
from tcheck_parser import update_ratios
import tcheck_propagation
import address_handler
from address_handler import global_address_counter, temp_address_counter, num_to_norm, label_sets, label_to_address, address_to_label

seen_contracts = {}
user_type = False
fill_type = False
mark_iteration = False
current_function_marked = False
type_file = ""
write_typefile = True
maxTokens = 10
debug_pow_pc = None
tempVar = defaultdict(list) #list storing temp variables (refreshed every node call)
strgVar = defaultdict(list) #list storing storage variables (kept through all calls)
currNode = None
errors = []
nErrs = 0
line_no = 1
function_hlc = 0
function_ref = 0
function_count = 0
current_contract_name = "ERR"
type_hashtable = {}
function_bar = {}
function_check = {}
contract_run = {}
contract_function = {}
constant_instance = Variable()
constant_instance.name = "Personal Constant Instance"
constant_instance_counter = 1
#BINOP Labels
Add = 1
Sub = 2
Mul = 3
Div = 4
Pow = 5
Cmp = 6

traces = 0 #trace default is -2
trace_to_label = {}
global_var_types = {}
var_assignment_storage = {}
read_global = {}

debug_print = True

ask_user = False
read_library = False

#IMPORTANT: read internal
read_internal = False

#USAGE: resets update ratios
def reset_update_ratios():
    tcheck_parser.reset_update_ratios()

#USAGE: create a 

#USAGE: creates and returns a constant instnace
#RETURNS: a constant instance (default constant)
def create_iconstant():
    global constant_instance_counter
    new_instance = Variable()
    new_instance.name = "PIC_" + str(constant_instance_counter)
    constant_instance_counter+=1
    assign_const(new_instance)
    return new_instance

#USAGE: adds token pair to type_hashtable
#RETURNS: composite key of the token pair
def add_hash(function_name, var_name, num, den, norm, lf):
    composite_key = function_name + '_' + var_name
    values = (num, den, norm, lf)
    type_hashtable[composite_key] = values
    return composite_key

#USAGE: gets the alias of a contract name for included external functions
def get_alias(used_name):
    return tcheck_parser.get_alias(used_name)

#USAGE: adds a contract, function pair
#RETURNS: NULL
def add_cf_pair(contract_name, function_name, function):
    if(contract_name == None or function_name == None or function.entry_point == None):
        return False
    #print(f"Adding function pair: {contract_name}, {function_name}")
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
    if(tuple_name == None or type_tuples == None):
        return None
    tcheck_parser.add_tuple(tuple_name, type_tuples)

#USAGE: returns a specific element located at index of a tuple
#RETURNS: above
def get_tuple_index(tuple_name, index):
    if(tuple_name == None):
        return None
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
    if(ref_name == None):
        return None
    return tcheck_parser.get_ref_type_tuple(ref_name)

#USAGE: views the current address labels
def print_addresses():
    for label, address in address_to_label.items():
        print(f"Address: {address}, Label: {label}")
    for label, addr_label in label_sets.items():
        print(addr_label)

#USAGE: given a function name and a var name, return the token pair
#RETURNS: tuple holding the token pair
def get_hash(function_name, var_name):
    if(function_name == None or var_name == None):
        return None
    return tcheck_parser.get_var_type_tuple(function_name, var_name)

#USAGE: adds a field
#RETURNS: NULL
def add_field(function_name, parent_name, field_name, type_tuple):
    if(function_name == None or parent_name == None or field_name == None):
        return None
    tcheck_parser.add_field(function_name, parent_name, field_name, type_tuple)

#USAGE: gets a field
#RETURNS: NULL
def get_field(function_name, parent_name, field_name):
    if(function_name == None or parent_name == None or field_name == None):
        return None
    #Some names will be off due to ssa version/non-ssa version conflict
    _parent_name = parent_name.rsplit('_', 1)[0]
    temp = tcheck_parser.get_field(function_name, parent_name, field_name)
    if(temp == None):
        temp = tcheck_parser.get_field(function_name, _parent_name, field_name)
    return temp

#USAGE: bar a function from being typechecked
#RETURNS: NULL
def bar_function(function_name):
    tcheck_parser.bar_function(function_name)


#USAGE: new address
def new_address(ir, isGlobal = None):
    #if (not(isinstance(ir, Variable))):
    #    return None
    if(isGlobal or ir.extok.function_name == "global"):
        return address_handler.new_address(ir, True)
    else:
        return address_handler.new_address(ir, False)

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
    if(contract_name == None or function_name == None):
        return None
    return tcheck_parser.get_ex_func_type_tuple_a(contract_name, function_name, parameters)


#USAGE: returns if a function should be typechecked
#RETURNS bool
def check_contract(contract_name):
    if(tcheck_parser.check_contract(contract_name)):
        return True
    return False

def print_token_type(ir):
    if(isinstance(ir, Variable)):
        y = 8008135

#USAGE: passes the finance type
def pass_ftype(dest, left, func, right = None):
    if(tcheck_propagation.pass_ftype(dest, left, func, right)):
        add_errors(dest)

#USAGE: prints a param_cache
#RETURNS: nothing
def print_param_cache(param_cache):
    return
    param_no = 0
    for param in param_cache:
        print("Param: " + str(param_no))
        print(f"    num: {param[0]}")
        print(f"    den: {param[1]}")
        print(f"    norm: {param[2]}")
        print(f"    link: {param[3]}")
        print(f"    fields: {param[4]}")
        print(f"    fintype: {param[5]}")
        param_no+=1

#USAGE: given an ir for a function call, generate a param_cache
#RETURNS: retursn a param_cache
def function_call_param_cache(params):
    #assumes types have been assigned (any undefined types must be resolved previously)
    return(gen_param_cache(params))

#USAGE: given a function, generate a param_cache
#RETURNS: returns a param_cache
def function_param_cache(function):
    #assumes types have already been assigned
    return(gen_param_cache(function.parameters))

#USAGE: propagates all the fields of an ir
def propagate_fields(ir):
    tcheck_propagation.propagate_fields(ir)

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
        if(not isinstance(param, Variable)):
            _param = create_iconstant().extok
        else:
            _param = param.extok
        num = _param.num_token_types
        den = _param.den_token_types
        norm = _param.norm
        link_function = _param.linked_contract
        fields = _param.fields
        finance_type = _param.finance_type
        address = _param.address
        value = _param.value
        param_type = [num, den, norm, link_function, fields, finance_type, address, value]
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
        dif_cur_param = False
        for cur_param in cur_param_cache:
            #compare cur_param with new_param_cache[paramno]
            seen_n = {}
            seen_d = {}
            seen_norm = False
            seen_ftype = False
            seen_address = False
            #compare numerators
            for num in cur_param[0]:
                if(num in seen_n):
                    seen_n[num]+=1
                else:
                    seen_n[num] = 1
            for num in new_param_cache[paramno][0]:
                if(num in seen_n):
                    seen_n[num]-=1
                else:
                    seen_n[num] = -1
            #compare denominators
            for num in cur_param[1]:
                if(num in seen_d):
                    seen_d[num]+=1
                else:
                    seen_d[num] = 1
            for num in new_param_cache[paramno][1]:
                if(num in seen_d):
                    seen_d[num]-=1
                else:
                    seen_d[num] = -1
            #compare norms
            if(new_param_cache[paramno][2] != cur_param[2]):
                seen_norm = True
            #compre finance_type
            if(new_param_cache[paramno][5] != cur_param[5]):
                seen_ftype = True
            #compare address
            if(new_param_cache[paramno][6] != cur_param[6]):
                seen_address = True
            if(seen_ftype or seen_norm or seen_address):
                dif_cur_param = True
                break
            for n in seen_n:
                if(seen_n[n] != 0):
                    dif_cur_param = True
                    break
            for d in seen_d:
                if(seen_d[d] != 0):
                    dif_cur_param = True
                    break
            if(dif_cur_param):
                break
            paramno+=1
        if(dif_cur_param == False):
            add_param = False
            match_param = a
            break
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
def parse_type_file(t_file, f_file = None):
    tcheck_parser.parse_type_file(t_file, f_file)

#USAGE: given a variable ir, return the type tuple
#RETURNS: type tuple
def read_type_file(ir):
    _ir = ir.extok
    function_name = ir.parent_function
    var_name = _ir.name
    if(ir.tname != None):
        var_name = ir.tname
    if(_ir.name == None):
        return None
    ref_tt = get_ref(var_name)
    if(ref_tt):
        return(ref_tt)
    return tcheck_parser.get_var_type_tuple(function_name, var_name)

#USAGE: gets an address from the type file
def get_addr(ir, chk_exists = False):
    _ir = ir.extok
    function_name = ir.parent_function
    var_name = _ir.name
    if(_ir.name == None):
        return None
    return tcheck_parser.get_addr(function_name, var_name, chk_exists)
        

def append_typefile(ir, num = None, den = None, norm = None, lf = None):
    global write_typefile
    global type_file
    if(not(write_typefile)):
        return
    _ir = ir.extok
    function_name = ir.parent_function
    var_name = _ir.name
    newline = "[t], " + function_name + ", " + var_name
    if(num == -1 and den == -1 and norm == 0 and lf == None):
        #do nothing
        y = XXX
    else:
        newline=newline + ", " + str(num) + ", " + str(den) + ", " + str(norm)
        if(lf):
            newline = newline + ", " + str(lf)
    tfile = open(type_file, "a")
    tfile.write(newline+"\n")
    tfile.close()

#USAGE: generate a name for temporary addresses in the form: function:name
def generate_temporary_address_name(ir):
    parent = ir.parent_function
    name = ir.extok.name
    new_name = str(parent)+":"+str(name)
    return(new_name)


#USAGE: querry the user for a type
#RETURNS: N/A
def querry_type(ir):
    global user_type
    global type_file
    global ask_user
    global mark_iteration
    global write_typefile
    global current_function_marked
    global global_address_counter
    global temp_address_counter
    global num_to_address
    global address_to_num
    _ir = ir.extok
    uxname = _ir.name
    if(ir.tname != None):
        uxname = ir.tname
    uxname = str(uxname)
    #print(f"Finding type for {uxname}({ir.type} ... )")
    if(str(ir.type) == "bool"):
        assign_const(ir)
        return
    if(str(ir.type) == "bytes"):
        return
    if(str(ir.type).startswith("address") or "=> address" in str(ir.type) or get_addr(ir, True) != None):
        #Address array and Mappings resulting in addressess.
        norm = get_addr(ir)
        if(norm == None):
            input_str = input()
            if(input_str != '*'):
                norm = int(input_str)
        label = new_address(ir)
        label.norm = norm
        ir.extok.norm = norm
        return

    #Get type tuple for regular variables
    type_tuple = read_type_file(ir)
    
    propagate_fields(ir)
    if(type_tuple != None):
        _ir.clear_num()
        _ir.clear_den()
        save_addr = _ir.address
        copy_token_tuple(ir, type_tuple)
        if(_ir.address == 'u'):
            _ir.address = save_addr
        #print("[*]Type fetched successfully")
        return
    #print("[x]Failed to fetch type from type file, defaulting to human interface")

    assign_const(ir)
    norm = get_norm(ir)
    #Assign norm to constants
    if(norm != 'u'):
        ir.extok.norm = norm
    return True
    

    #Turned off for artifact, querries users for type
    print("Define num type for \"" + uxname + "\": ")
    input_str = input()
    num = int(input_str)
    _ir.add_num_token_type(num)
    print("Define den type for \"" + uxname + "\": ")
    input_str = input()
    den = int(input_str)
    _ir.add_den_token_type(den)
    print("Define norm for \"" + uxname + "\": ")
    input_str = input()
    norm = int(input_str)
    _ir.norm = norm
    lf = None
    if(str(ir.type) == "address"):
        print("Define Linked Contract Name for \"" + uxname + "\": ")
        lf = input()
        ir.link_function = lf
    append_typefile(ir, num, den, norm, lf)

def is_constant(ir):
    if isinstance(ir, Constant):
        return True
    return False

def is_function(ir):
    if isinstance(ir, Function):
        temp = ir.parameters

def is_condition(ir):
    if isinstance(ir, Condition):
        y = 8008135
def is_function_type_variable(ir):
    if isinstance(ir, FunctionTypeVariable):
        y = 8008135

def is_type_undef(ir):
    if not(is_variable(ir)):
        return True
    _ir = ir.extok
    return _ir.is_undefined()

def is_type_address(ir):
    if not(is_variable(ir)):
        return False
    _ir = ir.extok
    return _ir.is_address()

def is_type_const(ir):
    if not(is_variable(ir)):
        return True
    _ir = ir.extok
    return _ir.is_constant()

#USAGE: assigns an IR to the constant type (-1)
#       ex: 1, 5, 1001
#RETURNS: NULL
def assign_const(ir):
    if(is_type_const(ir)):
        return
    _ir=ir.extok
    _ir.init_constant()
    ir.token_typen.clear()
    ir.token_typed.clear()
    ir.add_token_typen(-1)
    _ir.value = 'u'
    _ir.finance_type = -1
    
    ir.add_token_typed(-1)

#USAGE: assigns an IR to the error type (-2) this stops infinite lioops
#RETURNS: NULL
def assign_err(ir):
    assign_const(ir)

#USAGE: copies all the types from a type tuple to an ir node
#RETURNS: null
def copy_token_tuple(ir, tt):
    tcheck_propagation.copy_token_tuple(ir, tt)



#USAGE: copies all token types from the 'src' ir node to the 'dest' ir node
#RETURNS: null
def copy_token_type(src, dest):
    tcheck_propagation.copy_token_type(dest, src)

#USAGE: copies inverse token types from the 'src' ir node from the 'dest' ir node
#RETURNS: null
def copy_inv_token_type(src, dest):
    tcheck_propagation.copy_inv_token_type(src, dest)

#USAGE: copy and replace a token from a param_cache to an ir
#RETURNS: nN/A
def copy_pc_token_type(src, dest):
    tcheck_propagation.copy_pc_token_type(src, dest)

#USAGE: copies a finance type
def copy_ftype(src, dest):
    tcheck_propagation.copy_ftype(src, dest)

def compare_token_type(src, dest):
    return tcheck_propagation.compare_token_type(src, dest)
    

def add_errors(ir):
    global nErrs
    global errors
    if ir in errors:
        assign_err(ir)
        return
    errors.append(ir)
    nErrs+=1
    _ir = ir.extok
    if(_ir.function_name == None):
        _ir.function_name = "None"
    print(f"Error with {_ir.name} in function {_ir.function_name}")
    print("Error with: " + _ir.name + " in function " + _ir.function_name)
    assign_err(ir)

#USAGE: Directly copies a normalization value (WARNING: SKIPS TYPECHECKING)
def copy_norm(src, dest):
    return tcheck_propagation.copy_norm(src, dest)

#USAGE: Converts the first ssa instance of a variable (ends with _1)
#RETURNS: NULL
def convert_ssa(ir):
    return
    if(not(is_variable(ir))):
        return
    if(is_constant(ir) or ir.name.startswith("PIC") or isinstance(ir, Constant)):
        return
    non_ssa_ir = ir.non_ssa_version
    if(not (is_type_undef(non_ssa_ir))):
        ir.token_typen.clear()
        ir.token_typed.clear()
        _ir = ir.extok
        _ir.token_type_clear()
        copy_token_type(non_ssa_ir, ir)
        copy_norm(non_ssa_ir, ir)
        ir.norm = non_ssa_ir.norm
        if(non_ssa_ir.extok.function_name):
            _ir.function_name = non_ssa_ir.extok.function_name
        ir.link_function = non_ssa_ir.link_function
        _ir.finance_type = non_ssa_ir.extok.finance_type
        _ir.updated = non_ssa_ir.extok.updated
        _ir.address = non_ssa_ir.extok.address

#USAGE: updates a non_ssa instance of a variable
#RETURNS: NULL
def update_non_ssa(ir):
    return
    if(not(is_variable(ir))):
        return
    if(is_constant(ir)):
        return
    non_ssa_ir = ir.non_ssa_version
    if(not (is_type_undef(ir))):
        _non_ssa_ir = non_ssa_ir.extok
        _non_ssa_ir.token_type_clear()
        non_ssa_ir.token_typen.clear()
        non_ssa_ir.token_typed.clear()
        copy_token_type(ir, non_ssa_ir)
        copy_norm(ir, non_ssa_ir)
        non_ssa_ir.norm = ir.norm
        non_ssa_ir.link_function = ir.link_function
        non_ssa_ir.extok.finance_type = ir.extok.finance_type
        non_ssa_ir.updated = ir.extok.updated
        non_ssa_ir.address = ir.extok.address
    else:
        _non_ssa_ir = non_ssa_ir.extok
        _non_ssa_ir.token_type_clear()

#USAGE: type checks an IR
#currently handles assignments and Binary
#returns ir if needs to be added back
def check_type(ir) -> bool:
    global debug_pow_pc
    global global_var_types
    global current_contract_name
    global var_assignment_storage
    addback = False
    #Print the IR (debugging statement)
    #print(ir)
    if isinstance(ir, Assignment):
        addback = type_asn(ir.lvalue, ir.rvalue)
        #Assign value if constant int assignement
        if(is_constant(ir.rvalue)):
            ir.lvalue.extok.value = ir.rvalue.value
        elif(is_variable(ir.rvalue)):
            ir.lvalue.extok.value = ir.rvalue.extok.value
        rnorm = get_norm(ir.rvalue)
        if(ir.lvalue.extok.norm != '*' and not (is_constant(ir.rvalue) and rnorm == 0)):
            asn_norm(ir.lvalue, rnorm)
        pass_ftype(ir.lvalue, ir.rvalue, "assign")
        
    elif isinstance(ir, Binary):
        #Binary
        addback = type_bin(ir)
    elif isinstance(ir, Modifier):
        addback = False
    elif isinstance(ir, InternalCall):
         #Function call
        addback = type_fc(ir)
    elif isinstance(ir, LibraryCall):
        addback = type_library_call(ir)
    elif isinstance(ir, HighLevelCall):
        #High level call
        addback = type_hlc(ir)
    elif isinstance(ir, TypeConversion):
        type_conversion(ir)
    elif isinstance(ir, Unpack):
        #Unpack tuple
        addback = type_upk(ir)
    elif isinstance(ir, Phi):
        #Phi (ssa) unpack
        addback = False
        if(is_type_undef(ir.lvalue)):
            set = False
            temp_rvalues = sorted(ir.rvalues, key=lambda x: str(x), reverse=False)
            for rval in temp_rvalues:
                if(not(is_type_undef(rval) or is_type_const(rval))):
                    type_asn(ir.lvalue, rval)
                    ir.lvalue.extok.norm = rval.extok.norm
                    if(rval.extok.finance_type != -1):
                        ir.lvalue.extok.finance_type = rval.extok.finance_type

                else:
                    continue
                _rval = rval.extok
                for field in _rval.fields:
                    ir.lvalue.extok.add_field(field)
                set = True
                break
            if(set == False):
                for rval in temp_rvalues:
                    if(isinstance(rval.extok.norm, int)):
                        ir.lvalue.extok.norm = rval.extok.norm
                        if(rval.extok.finance_type != -1):
                            ir.lvalue.extok.finance_type = rval.extok.finance_type
                        else:
                            continue
                    _rval = rval.extok
                    for field in _rval.fields:
                        ir.lvalue.extok.add_field(field)
                    set = True
                    break
            if(set == False):
                for rval in temp_rvalues:
                    if(rval.extok.finance_type != -1):
                        ir.lvalue.extok.finance_type = rval.extok.finance_type
                    else:
                        continue
                    _rval = rval.extok
                    for field in _rval.fields:
                        ir.lvalue.extok.add_field(field)

    elif isinstance(ir, EventCall):
        return False
    elif isinstance(ir, Index):
        #print("INDEX")
        addback = type_ref(ir)
    elif isinstance(ir, Member):
        #print("MEMBER")
        addback = type_member(ir) 
        addback =  False
    elif isinstance(ir, Return):
        #print("RETURN")
        ir.function._returns_ssa.clear()
        for y in ir.values:
            if(init_var(y)): 
                ir.function.add_return_ssa(y)
            else:
                ir.function.add_return_ssa(create_iconstant())
        return False
    try:
        if ir.lvalue and is_variable(ir.lvalue):
            #Debugging statement: lhs variable after operatiom
            #print("[i]Type for "+ir.lvalue.name)
            #print(ir.lvalue.extok)
            if(isinstance(ir.lvalue, ReferenceVariable)):
                #Field propogation
                ref = ir.lvalue
                ref_root = ref.extok.ref_root
                ref_field = ref.extok.ref_field
                if(ref_root and ref_field):
                    update_member(ir.lvalue.points_to_origin, ref_field, ir.lvalue)
            update_non_ssa(ir.lvalue)
    except AttributeError:
        #do nothing
        y = XXX
    return (addback)

#USAGE: typechecks a type conversions (USDC vs IERC20)
#While it has its own address (i.e. address usdc corresponds to global address x),
#The underlying contract will still be the ERC20 contract.
#This represents a limitation of the tool: the interface must be of the form I`Implementation` of i `Implementation`
#RETURNS: nothing
def type_conversion(ir):
    global address_to_label
    global label_to_address
    if(str(ir.variable) == "this" or str(ir.variable) == "block.number" or str(ir.variable) == "msg.sender"):
        assign_const(ir.lvalue)
        name_key = "global:" + str(ir.variable)
        if(name_key in address_to_label):
            _addr = address_to_label[name_key]
        else:
            addr = new_address(ir.lvalue, True)
            _addr = addr.head
            label_to_address[addr] = name_key
            address_to_label[name_key] = _addr

        ir.lvalue.extok.address = _addr
        ir.lvalue.norm = 0
        ir.lvalue.link_function = current_contract_name
        addback = False
    else:    
        addback = type_asn(ir.lvalue, ir.variable)
        ir.lvalue.extok.value = ir.variable.extok.value
        if(ir.lvalue.extok.norm != get_norm(ir.variable)):
            asn_norm(ir.lvalue, get_norm(ir.variable))
        copy_ftype(ir.variable, ir.lvalue)
        if(str(ir.variable.type) == "address"):
            #This is a conversion
            instance_name = str(ir.type)
            contract_name = "UNKNOWN"
            pos = 0
            for char in instance_name:
                if(pos+1 > len(instance_name) - 1):
                    contract_name = "UNKNOWN"
                if(instance_name[pos] == 'i' or instance_name[pos] == 'I'):
                    contract_name = instance_name[pos+1:]
                    break
            ir.lvalue.link_function = contract_name
       

#USAGE: typcehcks an unpack functionality (similar to assign)
#RETURNS: nothing (type is querried from user)
def type_upk(ir) ->bool:
    #query the user for type info
    lval = ir.lvalue
    rtup = ir.tuple
    rind = ir.index
    if(lval.type == "bool"):
        assign_const(lval)
        return False
    if(lval.type == "address"):
        new_address(lval, False)
    if(isinstance(lval, UserDefinedType)):
        print("NOT HANDLED CURRENTLY!")
    tup_token_type = get_tuple_index(str(rtup), rind)
    if(tup_token_type):
        copy_token_tuple(lval, tup_token_type)
    else:
        querry_type(lval)
    return False

#USAGE: typechecks an included external call
#RETURNS: success of typecheck
def type_included_hlc(ir, dest, function, contract_name):
    global mark_iteration
    global current_function_marked
    global current_contract_name
    for param in ir.arguments:
        init_var(param)
        if(is_type_const(param)):
            assign_const(param)
        #elif(is_type_undef(param)):
            #undefined type
        #    return 1
    #generate param cache
    new_param_cache = function_hlc_param_cache(ir)
    added = -100
    added = add_param_cache(function, new_param_cache)
    if(added == -100):
        save_contract_name = current_contract_name
        current_contract_name = contract_name
        addback = _tcheck_function_call(function, new_param_cache)
        handle_return(ir.lvalue, function)
        current_contract_name = save_contract_name
        if(len(addback) != 0):
            return 2
    else:
        ret_obj = function.get_parameter_cache_return(added)
        if isinstance(ret_obj, Variable):
            if(isinstance(ret_obj, list)):
                type_asn(ir.lvalue, ret_obj[0])
                copy_ftype(ret_obj[0], ir.lvalue)
            else:
                type_asn(ir.lvalue, ret_obj)
                copy_ftype(ret_obj, ir.lvalue)
        else:
            add_tuple(ir.lvalue.name, ret_obj)


    return 2

#USAGE: connects a high-level call with an internal call (cross contract
#       function call where both contracts are defined)
#RETURNS: whether or not the function is detected (0)
#         whether or not the function has any undef types (1)
#         whether or not the function successfully passes (2)
def querry_fc(ir) -> int:
    global mark_iteration
    global current_function_marked
    global address_to_label
    if(not (isinstance(ir, HighLevelCall))):
        if(handle_balance_functions(ir)):
           return 2
        return 0
    dest = ir.destination
    func_name = ir.function.name
    cont_name = None
    isVar = True
    if(not (isinstance(dest, Variable))):
        cont_name = str(dest)
        isVar = False
    if(str(ir.lvalue.type) == "bool"):
        assign_const(ir.lvalue)
        return 2
    if(isVar):
        #Contingency for undefined contract instances
        cont_name = str(dest.type)

    written_func_rets = get_external_type_tuple(cont_name, func_name, ir.arguments)
    old_cont_name = cont_name
    if(written_func_rets == None):
        cont_name = cont_name[1:]
    written_func_rets = get_external_type_tuple(cont_name, func_name, ir.arguments)
    if(written_func_rets != None):
        if(len(written_func_rets) == 0):
            assign_const(ir.lvalue)
        elif(len(written_func_rets) == 1):
            written_func_ret = written_func_rets[0]
            copy_token_tuple(ir.lvalue, written_func_ret)
        elif(isinstance(ir.lvalue, TupleVariable) and len(written_func_rets) > 1):
            add_tuple(ir.lvalue.name, written_func_rets)
        else:
            y = False
        return 2
    #Use original contract name instead of reduced name for interfaces etc.
    #Special functions:
    if(handle_balance_functions(ir)):
        return 2
    included_func = get_cf_pair(old_cont_name, func_name)
    #print(f"Searching for cfpair: {old_cont_name}, {func_name}")
    final_name = old_cont_name
    if(included_func == None):
        included_func = get_cf_pair(cont_name, func_name)
        final_name = cont_name
    if(included_func == None):
        aliased_cont_name = get_alias(old_cont_name)
        if(aliased_cont_name == None):
            aliased_cont_name = get_alias(cont_name)
        if(aliased_cont_name != None):
            included_func = get_cf_pair(aliased_cont_name, func_name)
        final_name = aliased_cont_name

    if(included_func != None):

        if(type_included_hlc(ir, dest, included_func, final_name) == 1):
            return 2
        return 2
    '''
    #Special functions:
    if(handle_balance_functions(ir)):
        return 2
    '''
    return 0

#USAGE: propogates types etc from a set of balance-related functions. Currently supports the functions with names in `balance_funcs`.
#RETURNS: if the balance-related function was executed
def handle_balance_functions(ir):
    global address_to_num
    global num_to_norm
    #global trace_to_label
    global traces
    func_name = ir.function.name
    dest = ir.destination
    _dest = dest.extok
    token_type = 'u'
    norm = 'u'
    fin_type = -1
    isbfunc = False
    if(_dest.address == 'u'):
        _dest.address = new_address(dest, True).head
    #Use this to check for changes!
    ir.lvalue.extok.token_type_clear()
    if(func_name == "balanceOf"):
        token_type = _dest.address
        if(token_type in label_sets):
            if(label_sets[token_type].head > 0):
                token_type = label_sets[token_type].head
            norm = label_sets[token_type].norm
            fin_type = label_sets[token_type].finance_type
        #balanceOf, no important parameters, assign same type as dest address
        ir.lvalue.extok.add_num_token_type(token_type)
        ir.lvalue.extok.add_den_token_type(-1)
        ir.lvalue.extok.norm = norm
        #Financial type
        if(fin_type == 30):
            ir.lvalue.extok.finance_type = 30
        elif(fin_type == 0):
            ir.lvalue.extok.finance_type = 0
        else:
            ir.lvalue.extok.finance_type = 0
        isbfunc = True
    elif(func_name == "transferFrom" or func_name == "safeTransferFrom"):
        token_type = _dest.address
        if(token_type in label_sets):
            if(label_sets[token_type].head > 0):
                token_type = label_sets[token_type].head
            norm = label_sets[token_type].norm
            fin_type = label_sets[token_type].finance_type
        numargs = ir.nbr_arguments
        args = ir.arguments
        probarg = None
        if(numargs >= 3):
            probarg = args[2]
        if(probarg ==  None):
            return False
        #Test for safe
        if(not(is_type_const(probarg) or is_type_undef(probarg))):
            if(len(probarg.extok.den_token_types) != 0):
                add_error(probarg)
                return False
        probarg.extok.add_num_token_type(token_type)
        ir.lvalue.extok.add_den_token_type(-1)
        ir.lvalue.extok.norm = norm
        #Financial type
        if(fin_type == 30):
            ir.lvalue.extok.finance_type = 30
        elif(fin_type == 0):
            ir.lvalue.extok.finance_type = 0
        else:
            ir.lvalue.extok.finance_type = 0
        isbfunc = True
    elif(func_name == "decimals"):
        token_type = _dest.address
        if(token_type in label_sets):
            if(label_sets[token_type].head > 0):
                token_type = label_sets[token_type].head
            norm = label_sets[token_type].norm
            fin_type = label_sets[token_type].finance_type
        ir.lvalue.extok.value = norm
        isbfunc = True
    if(isbfunc and token_type < 0):
        ir.lvalue.extok.trace = dest
    return isbfunc
        


#USAGE: typecheck for a library call: in this case, we only return special instances, or user-defined calls
#RETURNS: return or not
def type_library_call(ir):
    param = ir.arguments
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
    
    if(querry_fc(ir) == 2):
        return False
    querry_type(ir.lvalue)
    return False

#USAGE: typecheck for high-level call (i.e. iERC20(address).balanceof())
#RETURNS: whether or not the high-level call node should be returned (should always return FALSE)
def type_hlc(ir) ->bool:
    #just query the user for the data 
    global function_hlc
    param = ir.arguments
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
    #typecheck abnormal function calls
    res = querry_fc(ir)
    if(res == 2):
        return False
        
    x = "hlc_"+str(function_hlc)
    ir.lvalue.change_name(x)
    querry_type(ir.lvalue)
    ir.lvalue.change_name(temp)
    function_hlc+=1
    return False


#USAGE: creates/updates a new field
def update_member(member, fieldf, copy_ir):
    if((isinstance(member, SolidityVariable))):
        return
    _member = member.extok

    added = False
    ptfield = None
    for field in _member.fields:
        _field = field.extok
        if(_field.name == fieldf.extok.name):
            added = True
            ptfield = field
            break
    if(added):
        copy_token_type(copy_ir, ptfield)
        asn_norm(ptfield, copy_ir.extok.norm)
        pass_ftype(ptfield, copy_ir, "assign")
        _field = ptfield.extok
    else:
        copy_token_type(copy_ir, fieldf)
        pass_ftype(fieldf, copy_ir, "assign")
        asn_norm(fieldf, copy_ir.extok.norm)
        _member.add_field(fieldf)

        _field = fieldf.extok
    if(not(_field.function_name)):
        _field.function_name = _member.function_name


#USAGE: typechecks Members (i.e. a.b or a.b())
#RETURNS: the type for a (temporary handling, will fix if any issues)
def type_member(ir)->bool:
    #FIELD WORK
    if(isinstance(ir.variable_left, SolidityVariable)):
        return False
    init_var(ir.variable_left)
    init_var(ir.variable_right)
    _lv = ir.variable_left.extok
    _rv = ir.variable_right.extok
    _ir = ir.lvalue.extok
    if(_lv.function_name == None):
        _lv.function_name = ir.lvalue.extok.function_name
    pf_name = _lv.function_name

    #Check for field in typefile first:
    field_type_tuple = get_field(pf_name, _lv.name, _rv.name)
    if(field_type_tuple == None):
        #print("No field found")
        return True

    field_full_name = _lv.name + "." + _rv.name
    _ir.name = field_full_name
    if(not(is_type_undef(ir.lvalue))):
        #Copy backwards from the dest (ir.lvalue) to the field
        fieldSet = False
        for field in _lv.fields:
            _field = field.extok
            if(not(_field.function_name)):
                _field.function_name = _lv.function_name
            if(_field.name == _rv.name):
                if(is_type_undef(_field)):
                    fieldSet = True
                type_asn(field, ir.lvalue)
                break
        return fieldSet

    for field in _lv.fields:
        _field = field.extok
        if(_field.name == _rv.name and not(is_type_undef(field))):
            ir.lvalue.extok.token_type_clear()
            copy_token_type(field, ir.lvalue)
            copy_norm(field, ir.lvalue)
            copy_ftype(field, ir.lvalue)
            return False
    
    ir.lvalue.extok.token_type_clear()
    copy_token_tuple(ir.lvalue, field_type_tuple)
    temp = create_iconstant()
    copy_token_tuple(temp, field_type_tuple)
    temp.name = _rv.name
    _lv.add_field(temp)
    return False
    

#USAGE: typechecks for references (i.e. a[0])
#RETURNS: always False
def type_ref(ir)->bool:
    global mark_iteration
    global current_function_marked
    global label_sets
    if(mark_iteration and not(current_function_marked)):
        assign_const(ir.lvalue)
        return False
    #check for boolean
    _lv = ir.lvalue.extok
    _vl = ir.variable_left.extok
    _lv.name = _vl.name
    _lv.function_name = _vl.function_name
    if(str(ir.lvalue.type) == "bool"):
        assign_const(ir.lvalue)
        return False
    
    ref_tuple = get_ref(ir.variable_left.non_ssa_version.name)
    if(ref_tuple != None):
        ##print("REFERENCE TYPE READ")
        copy_token_tuple(ir.lvalue, ref_tuple)
        return False

    #check if the right value already has a type?
    if not(is_type_undef(ir.variable_left) or is_type_const(ir.variable_left)):
        ir.lvalue.extok.token_type_clear()
        copy_token_type(ir.variable_left, ir.lvalue)
        copy_norm(ir.variable_left, ir.lvalue)
        copy_ftype(ir.variable_left, ir.lvalue)
        return False

    #check if the index of the variable has a type that is not a constant
    if not(is_type_undef(ir.variable_right) or is_type_const(ir.variable_right)):
        if(ir.variable_right.extok.is_address()):
            ir.lvalue.extok.token_type_clear()
            addr = ir.variable_right.extok.address
            head_addr = label_sets[addr].head
            norm = label_sets[addr].norm
            ir.lvalue.extok.add_num_token_type(head_addr)
            ir.lvalue.extok.add_den_token_type(-1)
            ir.lvalue.extok.norm = norm
            #ir.lvalue.extok.address = head_addr
        else:
            ir.lvalue.extok.token_type_clear()
            copy_token_type(ir.variable_right, ir.lvalue)
            copy_norm(ir.variable_right, ir.lvalue)
            copy_ftype(ir.variable_right, ir.lvalue)
        return False

    #check the parser for a pre-user-defined type
    if(str(ir.lvalue.type).startswith("address")):
        ir.lvalue.extok.address = ir.variable_left.extok.address
        return False

    #no other options, assign constant
    assign_const(ir.lvalue)
    return True


#USAGE: typecheck for function call (pass on types etc)
#RETURNS: whether or not the function call node should be returned
def type_fc(ir) -> bool:
    global mark_iteration
    global current_function_marked
    global debug_pow_pc
    #check parameters
    if(mark_iteration and not(current_function_marked)):
        return False
    params = []
    for param in ir.read:
        init_var(param)
        if(is_constant(param)):
            assign_const(param)
        elif(not isinstance(param, Variable)):
            param = create_iconstant()
        params.append(param)
    #generate param cache
    new_param_cache = function_call_param_cache(params)
    added = add_param_cache(ir.function, new_param_cache)
    if(added == -100):
        addback = _tcheck_function_call(ir.function, new_param_cache)
        handle_return(ir.lvalue, ir.function)
        if(len(addback) != 0):
            return True
        
    else:
        if(not(ir.lvalue)):
            return False
        ret_obj = ir.function.get_parameter_cache_return(added)
        if isinstance( ret_obj, Variable):
            if isinstance(ret_obj, list):
                type_asn(ir.lvalue, ret_obj[0])
                ir.lvalue.extok.norm = ret_obj[0].extok.norm
                copy_ftype(ret_obj[0], ir.lvalue)
            else:
                type_asn(ir.lvalue, ret_obj)
                ir.lvalue.extok.norm = ret_obj.extok.norm
                copy_ftype(ret_obj, ir.lvalue)
        else:
            add_tuple(ir.lvalue.name, ret_obj)

    return False

#USAGE: given a function, handle the return values
#RETURNS: NULL
def handle_return(dest_ir, function):
    global mark_iteration
    global current_function_marked
    #dest_ir is optional if there is no return destination
    tuple_types = []
    if(mark_iteration and not(current_function_marked)):
        return
    added = False
    _dest_ir = None
    constant_instance = create_iconstant()
    if(dest_ir):
        _dest_ir = dest_ir.extok
    for _x in function.returns_ssa:
        if(not isinstance(_x, Variable)):
            x = constant_instance
        else:
            x = _x
        __x = x.extok
        #Replace the returns_ssa
        if(len(function.return_values_ssa) > 1):
            #param_type = [num, den, norm, link_function, fields, finance_type, address, value]
            tuple_types.append((__x.num_token_types.copy(), __x.den_token_types.copy(), __x.norm, __x.value, __x.address, __x.finance_type))
        else:
            if(dest_ir != None):
                dest_ir.extok.token_type_clear()
                copy_token_type(x, dest_ir)
                _dest_ir.linked_contract = __x.linked_contract
                asn_norm(dest_ir, get_norm(x))
                copy_ftype(x, dest_ir)
            constant_instance.extok.token_type_clear()
            copy_token_type(x, constant_instance)
            constant_instance.extok.linked_contract = __x.linked_contract
            asn_norm(constant_instance, get_norm(x))
            copy_ftype(x, constant_instance)
            function.add_parameter_cache_return(constant_instance)
            added = True
    if(len(tuple_types) > 0):
        if(isinstance(dest_ir, TupleVariable)):
            add_tuple(dest_ir.name, tuple_types)
        elif(isinstance(dest_ir, Variable)):
            dest_ir.extok.token_type_clear()
            copy_token_tuple(dest_ir, tuple_types[0])
            
        function.add_parameter_cache_return(tuple_types)
        added = True
    if(added == False):
        function.add_parameter_cache_return(constant_instance)



#USAGE: assigns type from dest to sorc
#RETURNS: 'TRUE' if no variables undefined
def type_asn(dest, sorc) -> bool:
    init_var(sorc)
    if(is_type_undef(sorc)):
        return True
    elif(is_type_const(sorc)):
        if(is_type_undef(dest) or is_type_const(dest)):
            copy_token_type(sorc, dest)
        return False
    else:
        if(is_type_undef(dest) or is_type_const(dest)):
            copy_token_type(sorc, dest)
        elif(not(compare_token_type(sorc, dest)) and handle_trace(sorc, dest) == False):
            add_errors(dest)
    return False

#USAGE: assigns reverse type from sorc to dest
def type_asni(dest, sorc):
    init_var(sorc)
    if(is_type_undef(sorc)):
        return True
    elif(is_type_const(sorc)):
        if(is_type_undef(dest)):
            copy_inv_token_type(sorc, dest)
        return False
    else:
        tmp = create_iconstant()
        tmp = combine_types(tmp, sorc, "div") 
        if(is_type_undef(dest)):
            copy_inv_token_type(sorc, dest)
        elif(not(compare_token_type(tmp, dest))):
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
    #Special variables
    if(not(is_variable(ir)) and str(ir) != "msg.value"):
        return False
    _ir = ir.extok
    if(_ir.name == None or _ir.function_name == None):
        _ir.name = ir.name
        _ir.function_name = ir.parent_function
    if(is_constant(ir)):
        assign_const(ir)
        _ir.norm = get_norm(ir)
    else:
        convert_ssa(ir)
    return True

#USAGE: test any ir for if it is a special constant instead of a variable
#RETURNS: new ir
def init_special(ir):
    if((is_variable(ir))):
        return ir
    if(str(ir) == "block.timestamp"):
        return create_iconstant() 
    else:
        return ir
        
def get_values(ir):
    if(is_constant(ir)):
        return ir.value
    else:
        return ir.extok.value

#%dev returns true if the ir needs to be added back also initializes norms
#false otherwise
def type_bin(ir) -> bool:
    temp_left = init_special(ir.variable_left)
    temp_right = init_special(ir.variable_right)
    ret = False
    if (ir.type == BinaryType.ADDITION):
        ret = type_bin_add(ir.lvalue, temp_left, temp_right)
        return ret
    elif (ir.type == BinaryType.SUBTRACTION):
        ret = type_bin_sub(ir.lvalue, temp_left, temp_right)
        return ret
    elif (ir.type == BinaryType.MULTIPLICATION):
        ret = type_bin_mul(ir.lvalue, temp_left, temp_right)
        return ret
    elif (ir.type == BinaryType.DIVISION):
        ret = type_bin_div(ir.lvalue, temp_left, temp_right)
        return type_bin_div(ir.lvalue, temp_left, temp_right)
    elif (ir.type == BinaryType.POWER):
        return type_bin_pow(ir.lvalue, temp_left, temp_right)
    elif (ir.type == BinaryType.GREATER):
        return type_bin_gt(ir.lvalue, temp_left, temp_right)
    elif (ir.type == BinaryType.GREATER_EQUAL):
        return type_bin_ge(ir.lvalue, temp_left, temp_right)
    elif (ir.type == BinaryType.LESS):
        return type_bin_lt(ir.lvalue, temp_left, temp_right)
    elif (ir.type == BinaryType.LESS_EQUAL):
        return type_bin_le(ir.lvalue, temp_left, temp_right)
    return False

#USAGE: typechecks power statements
#RETURNS 'True' if needs to be added back
def type_bin_pow(dest, lir, rir) -> bool:
    if(not (init_var(lir) and init_var(rir))):
        return False
    #don't assign norm yet
    _lir = lir.extok
    _rir = rir.extok
    if(is_type_undef(lir) or is_type_undef(rir)):
        return True
    pow_const = -1
    pass_ftype(dest, lir, "pow", rir)
    if(is_constant(rir)):
        pow_const = rir.value
    if(is_type_const(lir)):
        assign_const(dest)
        l_norm = get_norm(lir)
        if(pow_const > 0 and isinstance(l_norm, int)):
            if(l_norm == 0):
                l_norm = 1
            asn_norm(dest, pow_const * (l_norm))
        elif(pow_const == 0):
            asn_norm(dest, pow_const)
        else:
            if(dest.extok.norm != '*'):
                asn_norm(dest, 'u')
    else:
        type_asn(dest, lir)
        l_norm = get_norm(lir)
        if(pow_const != -1 and isinstance(l_norm, int)):
            if(pow_const > 0):
                asn_norm(dest, pow_const*l_norm)
                for i in range (pow_const-1):
                    type_asna(dest, lir)
            else:
                asn_norm(dest, -pow_const * l_norm)
                for i in range(pow_const-1):
                    type_asnai(dest, lir)
        else:
            if(dest.extok.norm != '*'):
                asn_norm(dest, 'u')
    handle_value_binop(dest, lir, rir, Pow)
    return False

#USAGE: gets values of a binary operations and generates the result value
def handle_value_binop(dest, lir, rir, func):
    global Add
    global Sub
    global Mul
    global Div
    global Pow
    lval = get_values(lir)
    rval = get_values(rir)
    fval = 'u'
    if(type(lval) != int or type(rval) != int):
        if(type(lval) == int):
            fval = lval
        if(type(rval) == int):
            fval = rval
    elif(func == Add):
        fval = lval + rval
    elif(func == Sub):
        fval = lval - rval
    elif(func == Mul):
        fval = lval * rval
    elif(func == Div):
        if(rval == 0):
            fval = 0
        else:
            fval = (int)(lval / rval)
    elif(func == Pow):
        fval = lval ** rval
        if(lval == 10):
            dest.extok.norm = rval
    dest.extok.value = fval

#USAGE: typechecks addition statements
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_add(dest, lir, rir) -> bool:
    global Add
    if(not (init_var(lir) and init_var(rir))):
        return False
    #Handle errors
    if(not(is_type_undef(lir) or is_type_undef(rir) or is_type_const(lir) or is_type_const(rir) or is_type_address(lir) or is_type_address(rir))):
        if(not(compare_token_type(rir, lir)) and handle_trace(rir, lir) == False):
            #report error, default to left child 
            add_errors(dest)
            return False
    bin_norm(dest, lir, rir)
    pass_ftype(dest, lir, "add", rir)
    if(is_type_undef(lir) or  is_type_undef(rir) or is_type_address(lir) or is_type_address(rir)):
        if(is_type_undef(lir) or is_type_address(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        handle_value_binop(dest, lir, rir, Add)
        return True
    elif(is_type_const(lir)):
        temp = type_asn(dest, rir)
        handle_value_binop(dest, lir, rir, Add)
        return temp
    elif(is_type_const(rir)):
        temp = type_asn(dest, lir)
        handle_value_binop(dest, lir, rir, Add)
        return temp
    
    else:
        temp = type_asn(dest, tcheck_propagation.greater_abstract(rir, lir))
        handle_value_binop(dest, lir, rir, Add)
        return temp

#USAGE: typechecks subtraction statements
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_sub(dest, lir, rir) -> bool:
    global Sub
    if(not (init_var(lir) and init_var(rir))):
        return False
    #Handle errors
    if(not(is_type_undef(lir) or is_type_undef(rir) or is_type_const(lir) or is_type_const(rir) or is_type_address(lir) or is_type_address(rir))):
        if(not(compare_token_type(rir, lir)) and handle_trace(rir, lir) == False):
            #report error, default to left child 
            
            add_errors(dest)
            return False
    bin_norm(dest, lir, rir)
    pass_ftype(dest, lir, "sub", rir)
    if(is_type_undef(lir) or  is_type_undef(rir) or is_type_address(lir) or is_type_address(rir)):
        if(is_type_undef(lir) or is_type_address(lir)):
            type_asn(dest, rir)
        else:
            type_asn(dest, lir)
        handle_value_binop(dest, lir, rir, Sub)
        return True
    elif(is_type_const(lir)):
        temp = type_asn(dest, rir)
        handle_value_binop(dest, lir, rir, Sub)
        return temp
    elif(is_type_const(rir)):
        temp = type_asn(dest, rir)
        handle_value_binop(dest, lir, rir, Sub)
        return temp
    else:
        temp = type_asn(dest, tcheck_propagation.greater_abstract(rir, lir))
        handle_value_binop(dest, lir, rir, Sub)
        return temp

#USAGE: handles traces -> takes the difference in token types and handles traces, placed in the comparison failure branch in type...add and type...sub
#RETURNS: successful handling or not
def handle_trace(rir, lir):
    global label_sets
    #Save token types
    _rir = rir.extok
    _lir = lir.extok
    rntt = _rir.num_token_types.copy()
    rdtt = _rir.den_token_types.copy()
    lntt = _lir.num_token_types.copy()
    ldtt = _lir.den_token_types.copy()
    #Reduce numerators
    n_dict = {}
    for rn in rntt:
        if(rn == -1):
            continue
        if(rn < -1):
            if(rn in label_sets):
                rn = label_sets[rn].head
        if(rn in n_dict):
            n_dict[rn]+=1
        else:
            n_dict[rn] = 1
    for ln in lntt:
        if(ln == -1):
            continue
        if(ln < -1):
            if(ln in label_sets):
                ln = label_sets[ln].head
        if(ln in n_dict):
            n_dict[ln]-=1
        else:
            n_dict[ln] = -1
    #Reduce denominators
    d_dict = {}
    for rd in rdtt:
        if(rd == -1):
            continue
        if(rd < -1):
            if(rd in label_sets):
                rd = label_sets[rd].head
        if(rd in d_dict):
            d_dict[rd]+=1
        else:
            d_dict[rd] = 1
    for ld in ldtt:
        if(ld == -1):
            continue
        if(ld < -1):
            if(ld in label_sets):
                ld = label_sets[ld].head
        if(ld in d_dict):
            d_dict[ld]-=1
        else:
            d_dict[ld] = -1
    #Generate matchings, or generalize set
    all_zeros = True
    for n in n_dict:
        if (n != 0):
            all_zeros = False
            break
    for d in d_dict:
        if(d!= 0 and all_zeros):
            all_zeros = False
            break
    if(all_zeros):
        return True
    pot_trace = generate_label_trace(n_dict, d_dict)
    if(pot_trace == None):
        return False
    #Just take the first one for now
    first_trace = pot_trace[0]
    for key,value in first_trace.items():
        unioned = label_sets[key].union(label_sets[value])
        if(unioned):
            continue
        return False
    _rir.resolve_labels(label_sets)
    _lir.resolve_labels(label_sets)
    return True

#USAGE: given two dictionaries with x amounts of value y, generate all possible orderings of trace to label
#RETURNS: set of all possible orderings
def generate_label_trace(dictA, dictB):
    pot_ordering = []
    #Generate for dictA
    pos_dict = {}
    sum = 0
    neg_dict = {}
    for i in dictA:
        if(i > 0):
            pos_dict[i] = dictA[i]
            sum+=1
        else:
            neg_dict[i] = dictA[i]
            sum-=1
    if(sum > 0):
        return None
    #Begin matching (dp algorithm)
    dp = [[]]  #int, ([ordering], [pos_dict])
    curn = 0
    for n in neg_dict:
        dp.append([]) 
        if (curn == 0):
            for p in pos_dict:
                _pos_dict = copy.deepcopy(pos_dict)
                _neg_dict = copy.deepcopy(neg_dict)
                _pos_dict[p] += neg_dict[n]
                _ordering = {}
                _ordering[n] = p
                dp[curn].append([_pos_dict, _neg_dict, _ordering])
            for n2 in neg_dict:
                if(n2 == n):
                    continue
                _pos_dict = copy.deepcopy(pos_dict)
                _neg_dict = copy.deepcopy(neg_dict)
                _neg_dict[n2] += neg_dict[n]
                _ordering = {}
                _ordering[n] = n2
                dp[curn].append([_pos_dict, _neg_dict, _ordering]) 
        else:
            for tuple in dp[curn-1]:
                _pos_dict = tuple[0]
                _neg_dict = tuple[1]
                _ordering = tuple[2]
                for p in _pos_dict:
                    _2pos_dict = copy.deepcopy(_pos_dict)
                    _2pos_dict[p] += _neg_dict[n]
                    _2ordering = _ordering.copy()
                    _2ordering[n] = p
                    dp[curn].append([_2pos_dict, _neg_dict, _2ordering])
                for n2 in _neg_dict:
                    if(n2 == n):
                        continue
                    _2neg_dict = copy.deepcopy(_neg_dict)
                    _2neg_dict[n2] += _neg_dict[n]
                    _2ordering = _ordering.copy()
                    _2ordering[n] = n2
                    dp[curn].append([_pos_dict, _2neg_dict, _2ordering])
        curn+=1
    if(curn == 0):
        return None
    for orderings in dp[curn-1]:
        if(check_ordering(orderings[2], dictA) and check_ordering(orderings[2], dictB)):
            pot_ordering.append(orderings[2])
    if(len(pot_ordering) == 0):
        return None
    return pot_ordering


    
#USAGE: checks ordering
#RETURNS: ordering succeeds or not
def check_ordering(order, _dict):
    dict = copy.deepcopy(_dict)
    return True
    for d in dict:
        if(d < 0):
            dict[order[d]]-=dict[d]
            if(dict[order[d]]) < 0:
                return False
    for d in dict:
        if(dict[d] != 0):
            return False


#USAGE: given a constant, determine the number of powers of 10 that it includes
#RETURNS: the powers of 10 in the constant, if not, returns -1
def get_norm(ir):
    power = -1
    if(not(is_variable(ir))):
        return 'u'
    _ir = ir.extok
    if(type(_ir.norm) != int and type(_ir.value) == int):
        if(_ir.value % 10 != 0):
            return power+1
        power = 0
        copy_val = _ir.value
        while (copy_val > 0 and copy_val%10 == 0):
            copy_val = copy_val/10
            power+=1
        if(power >= 5 or copy_val == 1):
            return power

    #ir is a constant or undefined
    if(not(isinstance(ir, Constant)) or (not(isinstance(ir.value, int)))):
        return _ir.norm
    else:
        if(ir.value % 10 != 0):
            return power+1
        power = 0
        copy_val = ir.value
        while (copy_val > 0 and copy_val%10 == 0):
            copy_val = copy_val/10
            power+=1
        if(power >= 5 or copy_val == 1):
            ##print(power)
            return power
        return 0
            
#USAGE: if norm uninitialized, initializes norm (0)
#       if initialized, check against norm and throw error
#RETURNS: NULL
def asn_norm(ir, norm):
    if(not(is_variable(ir)) or norm == 'u'):
        return
    _ir = ir.extok
    if(_ir.norm == 'u'):
        _ir.norm = norm
    elif (_ir.norm != norm and norm == '*'):
       _ir.norm = '*'
    else:
        if(_ir.norm != norm or (_ir.norm == norm and norm == '*')):
            if(_ir.norm == 0 and norm != '*'):
                _ir.norm = norm
                return
            add_errors(ir)
            _ir.norm = 'u'

#USAGE: compares norm values of two variables and throws errors if they are not equal
def compare_norm(lv, varA, varB, func = None):
    global mark_iteration
    global current_function_marked
    if(mark_iteration and not(current_function_marked)):
        return True
    if(not(isinstance(varA, Variable) and isinstance(varB, Variable))):
        return True
    _varA = varA.extok
    _varB = varB.extok
    A_norm = _varA.norm
    B_norm = _varB.norm
    if(not(func) and (isinstance(varA, Constant) or isinstance(varB, Constant))):
        if(isinstance(varA, Constant) and varA.value == 1 and not(_varA.is_undefined() or _varA.is_constant())):
            add_errors(lv)
            return True
        if(isinstance(varB, Constant) and varB.value == 1 and not(_varB.is_undefined() or _varB.is_constant())):
            add_errors(lv)
            return True
        return False

    if(A_norm == 'u' or B_norm == 'u'):
        return False
    elif(A_norm == '*' or B_norm == '*'):
        if(A_norm == B_norm or func == "mul" or func == "div"):
            add_errors(lv)
            return True
    else:
        if((not(func)) and (A_norm != B_norm)):
            add_errors(lv)
            return True
    return False


#USAGE: append norm (i.e. for multiplication, division, or power)
#RETURNS: NULL
def add_norm(ir, norm):
    if(not(is_variable(ir))):
        return
    _ir = ir.extok
    temp = _ir.norm
    if(isinstance(temp, int) and isinstance(norm, int)):
        temp+=norm
        _ir.norm = temp
    elif(temp == 'u'):
        _ir.norm = norm
    elif(temp == '*'):
        if(isinstance(norm, str)):
            if(norm == '*'):
                add_errors(ir)
                return(True)
            else:
                y = False
        else:
            _ir.norm = '*'
    return False

#USAGE: subtract norm (i.e. for multiplication, division, or power)
#RETURNS: NULL
def sub_norm(ir, norm):
    if(not(is_variable(ir))):
        return
    _ir = ir.extok
    temp = _ir.norm
    if(isinstance(temp, int) and isinstance(norm, int)):
        temp-=norm
        _ir.norm = temp
    elif(temp == 'u'):
        _ir.norm = norm
    elif(temp == '*'):
        if(isinstance(norm, str)):
            if(norm == '*'):
                add_errors(ir)
                return True
            else:
                y = False
        else:
            _ir.norm = '*'
    return False


def bin_norm(dest, lir, rir, func = None):
    err = compare_norm(dest, lir, rir, func)
    lnorm = get_norm(lir)
    rnorm = get_norm(rir)
    if(err):
        asn_norm(dest, 'u')
        return
    if(func == "compare"):
        return
    if(lnorm == 'u'):
        if(func == "div" and isinstance(rnorm, int)):
            asn_norm(dest, -rnorm)
        else:
            asn_norm(dest, rnorm)
    elif(rnorm == 'u'):
        asn_norm(dest, lnorm)
    elif(lnorm == '*' or rnorm == '*' or not(isinstance(lnorm, int)) or not(isinstance(rnorm, int))):
           
        if(dest.extok.norm != '*'):
            asn_norm(dest, '*')
    else:
        #doesn't matter which
        if(func == "mul"):
            asn_norm(dest, lnorm + rnorm)
        elif(func == "div"):
            asn_norm(dest, lnorm - rnorm)
        else:
            asn_norm(dest, lnorm)

def combine_types(lir, rir, func = None):
    tmp = create_iconstant()
    _tmp = tmp.extok
    _lir = lir.extok
    _rir = rir.extok
    if(func == "mul"):
        copy_token_type(lir, tmp)
        copy_token_type(rir, tmp)
    elif(func == "div"):
        copy_token_type(lir, tmp)
        copy_inv_token_type(rir, tmp)
    return tmp


#USAGE: typechecks a multiplication statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_mul(dest, lir, rir) ->bool:
    global Mul
    if(not (init_var(lir) and init_var(rir))):
        return False
    bin_norm(dest, lir, rir, "mul")
    pass_ftype(dest, lir, "mul", rir)
    if(is_type_undef(lir) or is_type_undef(rir) or is_type_address(lir) or is_type_address(rir)):
        if(is_type_undef(dest)):
            if(is_type_undef(lir) or is_type_address(lir)):
                type_asn(dest, rir)
            else:
                type_asn(dest, lir)
        else:
            return(generate_ratios(dest, lir, rir, Mul))
        handle_value_binop(dest, lir, rir, Mul)
        return True
    elif(is_type_const(lir)):
        temp = type_asn(dest, rir)
        handle_value_binop(dest, lir, rir, Mul)
        return temp
    elif(is_type_const(rir)):
        temp = type_asn(dest, lir)
        handle_value_binop(dest, lir, rir, Mul)
        return temp
    else:
        tmp = combine_types(lir, rir, "mul")
        type_asn(dest, tmp)
        handle_value_binop(dest, lir, rir, Mul)
        if(is_type_undef(dest)):
            assign_const(dest)
        return False

#USAGE: typechecks a division statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_div(dest, lir, rir) ->bool:
    global Div
    if(not (init_var(lir) and init_var(rir))):
        return False
    bin_norm(dest, lir, rir, "div")
    pass_ftype(dest, lir, "div", rir)
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(dest)):
            if(is_type_undef(lir)):
                type_asni(dest, rir)
            else:
                type_asn(dest, lir)
        else:
            return(generate_ratios(dest, lir, rir, Div))
        handle_value_binop(dest, lir, rir, Div)
        return True
    elif(is_type_const(lir)):
        temp = type_asni(dest, rir)
        handle_value_binop(dest, lir, rir, Div)
        return temp
    elif(is_type_const(rir)):
        temp = type_asn(dest, lir)
        handle_value_binop(dest, lir, rir, Div)
        return temp
    else:
        tmp = combine_types(lir, rir, "div")
        type_asn(dest, tmp)
        handle_value_binop(dest, lir, rir, Div)
        if(is_type_undef(dest)):
            assign_const(dest)
        return False

#USAGE: generate price ratios i.e. USDC/WETH
def generate_ratios(dest, lir, rir, func):
    #Currently ignored
    return False
    global Mul
    global Div
    _dest = dest.extok
    _lir = lir.extok
    _rir = rir.extok
    if(not(is_type_undef(lir)) and not(is_type_undef(rir))):
        return False
    if(is_type_undef(dest)):
        return False
    else:
        if(func == Mul):
            if(is_type_undef(lir)):
                copy_token_type(dest, lir)
                copy_inv_token_type(rir, lir)
                handle_value_binop(lir, dest, rir, Div)
            else:
                copy_token_type(dest, rir)
                copy_inv_token_type(lir, rir)
                handle_value_binop(rir, dest, lir, Div)
        else:
            if(is_type_undef(lir)):
                copy_token_type(dest, lir)
                copy_token_type(rir, lir)
                handle_value_binop(lir, dest, rir, Mul)
            else:
                copy_token_type(lir, rir)
                copy_inv_token_type(dest, rir)
                handle_value_binop(rir, lir, dest, Div)
        return True




#USAGE: typechecks '>' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_gt(dest, lir, rir) -> bool:
    if(not (init_var(lir) and init_var(rir))):
        return False
    bin_norm(dest, lir, rir, "compare")
    pass_ftype(dest, lir, "compare", rir)
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(lir, rir)
            type_asn(dest, rir)
        else:
            type_asn(rir, lir)
            type_asn(dest, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant 
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir)) and handle_trace(lir, rir) == False):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

#USAGE: typechecks '>=' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_ge(dest, lir, rir) -> bool:
    if(not (init_var(lir) and init_var(rir))):
        return False
    bin_norm(dest, lir, rir, "compare")
    pass_ftype(dest, lir, "compare", rir)
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
            type_asn(lir, rir)
        else:
            type_asn(dest, lir)
            type_asn(rir, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant 
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir)) and handle_trace(lir, rir) == False):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

#USAGE: typechecks '<' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_lt(dest, lir, rir) -> bool:
    if(not (init_var(lir) and init_var(rir))):
        return False
    bin_norm(dest, lir, rir, "compare")
    pass_ftype(dest, lir, "compare", rir)
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
            type_asn(lir, rir)
        else:
            type_asn(dest, lir)
            type_asn(rir, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant (although it should not be used in arithmatic)
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir)) and handle_trace(lir, rir) == False):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

#USAGE: typechecks '<=' statement
#RETURNS: 'TRUE' if the node needs to be added back to the worklist
def type_bin_le(dest, lir, rir) -> bool:
    if(not (init_var(lir) and init_var(rir))):
        return False
    bin_norm(dest, lir, rir)
    pass_ftype(dest, lir, "compare", rir)
    if(is_type_undef(lir) or is_type_undef(rir)):
        if(is_type_undef(lir)):
            type_asn(dest, rir)
            type_asn(lir, rir)
        else:
            type_asn(dest, lir)
            type_asn(rir, lir)
        return True
    elif(is_type_const(lir) or is_type_const(rir)):
       #assign dest as a constant (although it should not be used in arithmatic)
       assign_const(dest)
       return False
    elif(not(compare_token_type(lir, rir)) and handle_trace(lir, rir) == False):
       add_errors(dest)
       return False
    assign_const(dest)
    return False

def is_variable(ir):
    if isinstance(ir, Variable):
        return True
    return False


def is_internalcall(ir):
    if isinstance(ir, InternalCall):
        y = False

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
    newirs = []
    for ir in irs:
        is_function(ir)
        if has_lvalue(ir):
             if function_name != None and ir.lvalue != None and is_variable(ir.lvalue):
                _ir = ir.lvalue.extok
                _ir.name = ir.lvalue.name
                _ir.function_name = function_name
                if(ir.lvalue.parent_function and ir.lvalue.parent_function == "global"):
                    _ir.function_name = "global"
                else:
                    ir.lvalue.parent_function = function_name
        if isinstance(ir, Function):
            continue
        if isinstance(ir, Condition):
            is_condition(ir)
            continue
        if isinstance(ir, EventCall):
            continue
        if isinstance(ir, InternalCall):
            is_function(ir.function)
            check_type(ir)
            continue
        if isinstance(ir, Return):
            check_type(ir)
            continue
        
        addback = check_type(ir)
        if(addback):
            newirs.append(ir)
    return newirs

#USAGE: propogates a local variables with a parameter
def propogate_parameter(lv, function, clear_initial_parameters = False):
    if("_1" in lv.ssa_name and (lv.extok.is_undefined() or clear_initial_parameters)):
            pos = -1
            for i in range(len(lv.ssa_name)-1):
                revpos = len(lv.ssa_name)-i-1
                if(lv.ssa_name[revpos:revpos+2] == '_1'):
                    pos = revpos
                    break
            lv_subname = lv.ssa_name[:pos]
            for p in function.parameters:
                if(p.name == lv_subname):
                    lv.extok.token_type_clear()
                    lv.extok.name = lv.ssa_name
                    lv.extok.function_name = function.name
                    copy_token_type(p, lv)
                    
                    lv.extok.norm = p.extok.norm
                    copy_ftype(p, lv)
                    return True
    return False
#USSAGE: propogates a local variable with a global stored assignment
def propogate_global(lv):
    global global_var_types
    global current_contract_name
    if(lv.extok.is_undefined()):
        pos = -1
        ssa_name_info = convert_ssa_name(lv.ssa_name)
        _name = ssa_name_info[0]
        #print(f"global name: {_name}, current_contract_name: {current_contract_name}")
        #print(global_var_types)
        if((_name, current_contract_name) in global_var_types):
            stored_state = global_var_types[(_name, current_contract_name)]
            copy_token_type(stored_state, lv)
            copy_ftype(stored_state, lv)
            lv.extok.norm = stored_state.extok.norm


#USAGE: gets the name and the number of an ssa_name
def convert_ssa_name(name):
    _name = None
    num = None
    for i in range(len(name)-1):
            revpos = len(name)-i-1
            if(name[revpos] == '_'):
                pos = revpos
                break
    _name = name[:pos]
    num = (name[pos+1:])
    return [_name, num]

#USAGE: typecheck a node
#RETURNS: list of IR with undefined types
def _tcheck_node(node, function) -> []:
    global errors
    global current_contract_name
    global global_address_counter
    function_name = function.name
    irs = []
    #local vars read
    for lv in node.ssa_local_variables_read:
        propogate_parameter(lv, function)
        propogate_global(lv)
    for lv in node.ssa_state_variables_read:
        propogate_parameter(lv, function)
        propogate_global(lv)
    for lv in node.ssa_variables_read:
        propogate_parameter(lv, function)
        propogate_global(lv)
    for lv in node.ssa_variables_written:
        propogate_parameter(lv, function)
        propogate_global(lv)   
        
    for ir in node.irs_ssa:
        #DEFINE REFERENCE RELATIONS
        ir.dnode = node

        
        if isinstance(ir, Phi):
            lv = ir.lvalue
            propogate_parameter(lv, function)
            propogate_global(lv)
        if isinstance(ir, Member):
            if isinstance(ir.lvalue, ReferenceVariable):
                ir.lvalue.extok.ref([ir.variable_left, ir.variable_right])
        irs.append(ir)
    newirs = _tcheck_ir(irs, function_name)

    #Handle Constructor Varialbes (need to be propagated)
    for var in node.ssa_variables_written:
        
        if((var.extok.name, current_contract_name) in global_var_types):
            temp = global_var_types[(var.extok.name, current_contract_name)]
            if(str(var.type) == "address"):
                continue
            temp.extok.name = var.extok.name
            temp.extok.function_name = function.name #"constructor"
            temp.extok.token_type_clear()
            copy_token_type(var, temp)
            if(temp.extok.finance_type == -1):
                copy_ftype(var, temp)
            temp.extok.norm = var.extok.norm
            global_var_types[(var.extok.name, current_contract_name)] = temp
            if(var.extok.address != 'u'):
                #Only global addresses
                global_address_counter+=1

    for error in errors:
        if(error.dnode == None):
            error.dnode = node
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
    if(isinstance(ir, Member)):
        return True
    if(isinstance(ir, Index)):
        return True
    if(isinstance(ir, Unpack)):
        return True
    if(isinstance(ir, Phi)):
        return True
    if(isinstance(ir, TypeConversion)):
        return True
    if(isinstance(ir, InternalCall)):
        return True
    return False

#USAGE: clears a node
#RETURNS: N/A
def _clear_type_node(node):
    global debug_pow_pc
    for ir in node.irs_ssa:
        #Clear lvalue
        if(has_lvalue(ir) and is_variable(ir.lvalue)):
            if(isinstance(ir.lvalue, TemporaryVariable) or isinstance(ir.lvalue, LocalIRVariable) or isinstance(ir.lvalue, Variable)):
                #clear the types for temporary and local variables
                _ir = ir.lvalue.extok
                _ir.token_type_clear()
                _ir.norm = 'u'
                _ir.finance_type = -1
                for field in _ir.fields:
                    field.extok.token_type_clear()
    #Clear variables


#USAGE: searches a function for a RETURN node, if it doesn't exist, do stuff
#RETURNS: return node
def remap_return(function):
    fentry = {function.entry_point}
    explored = set()
    return_ssa_mapping = {}
    for ir_ssa in function.returns_ssa:
        try:
            return_ssa_mapping[ir_ssa.ssa_name] = None
        except AttributeError:
            a = 2
    fentry = {function.entry_point}
    explored = set()
    while(fentry):
        node = fentry.pop()
        if(node in explored):
            continue
        explored.add(node)
        for written_ir in node.ssa_variables_written:
            if(written_ir.ssa_name in return_ssa_mapping):
                return_ssa_mapping[written_ir.ssa_name] = written_ir
        for son in node.sons:
            fentry.add(son)
    for ir_ssa in function.returns_ssa:
        try:
            if(not return_ssa_mapping[ir_ssa.ssa_name] == None ):
                ir_ssa = return_ssa_mapping[ir_ssa.ssa_name]
        except AttributeError:
            a = 2

#USAGE: propogates all of the parameters in a function to their first reference in the SSA.
#       uses "propogate_parameter"
def _propogate_all_parameters(function):
    explored = set()
    fentry = {function.entry_point}
    while fentry:
        node = fentry.pop()
        if node in explored:
            continue
        explored.add(node)
        for var in node.ssa_local_variables_read:
            propogate_parameter(var, function, True)
        for son in node.sons:
            fentry.add(son)
        
#USAGE: typecheck a function call
#       given a param_cache for the input data
#       check return values:
#RETURNS: list of nodes with undefined types
def _tcheck_function_call(function, param_cache) -> []:
    global function_hlc
    global function_ref
    global function_count
    global temp_address_counter
    function_hlc = 0
    function_ref = 0
    explored = set()
    addback_nodes = []
    #load parameters
    paramno = 0
    #Append to function count
    function_count+=1
    #print(f"function: {function.name}, function count: {function_count}")
    for param in function.parameters:
        if(paramno == len(param_cache)):
            break
        copy_pc_token_type(param_cache[paramno], param)
        paramno+=1
    #find return and tack it onto the end
    remap_return(function)

    #Propogate parameters
    _propogate_all_parameters(function)


    #WORKLIST ALGORITHM
    prevlen = -1
    curlen = -1
    wl_iter = 0
    while((curlen < prevlen and prevlen != -1) or prevlen == -1):
        addback_nodes = []
        explored = set()
        return_node = None
        fentry = {function.entry_point}
        #load in parameters
        paramno = 0
        for param in function.parameters:
            if(paramno == len(param_cache)):
                break
            copy_pc_token_type(param_cache[paramno], param)
            paramno+=1
        while fentry:
            node = fentry.pop()
            if node in explored:
                continue
            explored.add(node)
            #clear previous nodes
            if(prevlen == -1):
                _clear_type_node(node)
            addback = _tcheck_node(node, function)
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
            _clear_type_node(return_node)
            _tcheck_node(return_node, function)
        prevlen = curlen
        curlen = len(addback_nodes)
        wl_iter+=1
    return addback_nodes

#USAGE: typecheck a function
#       if external or public function, prompt user for types (local variable parameters)
#       no need to care about the function return values here (these check from external calls)
#RETURNS: list of nodes with undefined types
def _tcheck_function(function) -> []:
    global function_hlc
    global function_ref
    global function_count
    global mark_iteration
    global current_function_marked
    global temp_address_counter
    function_hlc = 0
    function_ref = 0
    explored = set()
    addback_nodes = []
    #print()
    #print()
    #print()
    #print(function.name)

    if(check_bar(function.name)):
        return addback_nodes
    #print("Function name: "+function.name)
    fvisibl = function.visibility
    new_param_cache = None
    if(True): 
        for fparam in function.parameters:
            fparam.parent_function = function.name
            querry_type(fparam)
        #generate param_cache
        new_param_cache = function_param_cache(function)
        if(not(mark_iteration) or current_function_marked):
            added = add_param_cache(function, new_param_cache)
    else:
        return addback_nodes
    remap_return(function)
    #Append to function count
    function_count+=1
    #print(f"function: {function.name}, function count: {function_count}")
    #Propogate parameters

    #WORKLIST ALGORITHM
    prevlen = -1
    curlen = -1
    wl_iter = 0
    while((prevlen > curlen and prevlen != -1) or prevlen == -1):
        addback_nodes = []
        fentry = {function.entry_point}
        viewfentry = {function.entry_point}
        view_ir(viewfentry)
        explored = set()
        paramno = 0
        for param in function.parameters:
            copy_pc_token_type(new_param_cache[paramno], param)
            paramno+=1
        while fentry:
            node = fentry.pop()
            if node in explored:
                continue
            explored.add(node)
            if(prevlen == -1):
                _clear_type_node(node)
            addback = _tcheck_node(node, function)
            if(len(addback) > 0):
                addback_nodes.append(node)
            for son in node.sons:
                fentry.add(son)
        prevlen = curlen
        curlen = len(addback_nodes)
        wl_iter+=1
    #Save return value
    handle_return(None, function)
    return addback_nodes

def view_ir(fentry):
    return
    explored = set()
    while fentry:
        node = fentry.pop()
        if node in explored:
            continue
        explored.add(node)
        for ir in node.irs_ssa:
            print (ir)
        for son in node.sons:
            fentry.add(son)
    print()
    print()
#USAGE: typechecks state (global) variables given a contract
#RETURNS: whether or not the state variable need to be added back.
#         the result is always 'FALSE' (querried)
def _tcheck_contract_state_var(contract):
    global user_type
    global fill_type
    global read_global
    global global_var_types
    global address_to_num
    global num_to_address
    type_info_name = None
    if(user_type and fill_type):
        type_info_name = contract.name+"_types.txt"
        new_tfile = open(type_info_name, "a")
        new_tfile.write(f"[*c], {contract.name}\n")
        new_tfile.close()
    seen = {}
    for state_var in _read_state_variables(contract):
        if(state_var.name in seen):
            continue
        seen[state_var.name] = True
        state_var.parent_function = "global"
        if(user_type and fill_type):
            new_tfile = open(type_info_name, "a")
            new_tfile.write(f"[t], global, {state_var.name}\n")
            new_tfile.close()
            assign_const(state_var)
            continue
        if(True):
            if(not(contract.name in read_global) or not((state_var.extok.name, contract.name) in global_var_types)):
                querry_type(state_var)
                new_constant = create_iconstant()
                copy_token_type(state_var, new_constant)
                copy_ftype(state_var, new_constant)
                new_constant.extok.norm = state_var.extok.norm
                global_var_types[(state_var.extok.name, contract.name)] = new_constant
            else:
                stored_state = global_var_types[(state_var.extok.name, contract.name)]
                copy_token_type(stored_state, state_var)
                copy_ftype(stored_state, state_var)
                state_var.extok.norm = stored_state.extok.norm
            if(isinstance(state_var, ReferenceVariable)):
                add_ref(state_var.name, (state_var.token_typen, state_var.token_typed, state_var.norm, state_var.link_function))
    read_global[contract.name] = True
    
#USAGE: labels which contracts that should be read (contains binary operations) also adds contract-function pairs
#RTURNS: NULL
def _mark_functions(contract):
    #Check for any external. If none, check internal (TODO add a feature to allow internal function type checking)
    hasExternal = read_internal
    for function in contract.functions_declared:
        if(function.visibility == "external" or function.visibility == "public"):
            hasExternal = True

    for function in contract.functions_declared:
        fentry = {function.entry_point}
        #add contract-function pair
        add_cf_pair(contract.name, function.name, function)
        if(not (function.entry_point and (not(hasExternal) or function.visibility == "external" or function.visibility == "public"))):
            function_check[function.name] = False
            continue
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
        continue
        if contains_bin:
            print("[*]Marked")
        else:
            print("[X]No Binary")



# USAGE: typechecks an entire contract given the contract
#        generates a list of nodes that need to be added back
# RETURNS: returns a list of errors(if any)
def _tcheck_contract(contract):
    #contract is the contract passed in by Slither
    global errors
    global current_contract_name
    global mark_iteration
    global current_function_marked
    global global_var_types
    global global_address_counter
    global address_to_num
    global num_to_address
    current_contract_name = contract.name
    all_addback_nodes = []
    #_mark_functions(contract)
    #_tcheck_contract_state_var(contract)
    #Reset update ratios
    reset_update_ratios()
    for function in contract.functions_declared:
        if not(function_check[function.name]):
            if(mark_iteration):
                current_function_marked = False
            else:
                continue
        else:
            current_function_marked = True
        if not function.entry_point:
            continue
        addback_nodes = _tcheck_function(function)
        #Override state variables only for the constructor
        current_function_marked = True
        if(function.name != "constructor"):
            y = None
        else:
            continue
        
        if(len(addback_nodes) > 0):
            all_addback_nodes+=(addback_nodes)
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

    WIKI = 'ScType'

    WIKI_TITLE = 'None'
    WIKI_DESCRIPTION = 'Static analysis tool for accounting errors'
    WIKI_EXPLOIT_SCENARIO = 'See paper'
    WIKI_RECOMMENDATION = 'None'

    def _detect(self):
        results = []
        u_provide_type = {}
        global user_type
        global type_file
        global line_no
        global constant_instance
        global seen_contracts
        global function_count
        global address_to_label
        global label_sets
        assign_const(constant_instance)
        total_compilations = tcheck_module.get_total_compilations()
        start_time = time.time()
        for contract in self.contracts:
            #print(f"Contracts handled: {contract.name}, compilations: {total_compilations}")
            #create hashtable with function name and contract name
            type_info_name = contract.name+"_types.txt"
            finance_info_name = contract.name+"_ftypes.txt"
            #get finance type info
            f_file = None
            try:
                with open(finance_info_name, "r") as _f_file:
                    f_file = finance_info_name
            except FileNotFoundError:
                f_file = None

            #get type information from file (if there is one)
            try:
                with open(type_info_name, "r") as t_file:
                    # File processing code goes here
                    user_type = False
                    type_file = type_info_name
                    parse_type_file(type_file, f_file)
                    u_provide_type[contract.name] = False
                    #print(f"opened type file for {contract.name}")
            except FileNotFoundError:
                # Handle the error gracefully or take appropriate action
                u_provide_type[contract.name] = False
                user_type = True

            if(not (check_contract(contract.name))):
                continue
            
            #mark functions
            used_contract = get_cont_with_state_var(contract.name)
            if(used_contract == None):
                used_contract = contract
            _mark_functions(used_contract)
            #resolve global variables
            _tcheck_contract_state_var(used_contract)

  
        for contract in self.contracts:
            if(contract.name in seen_contracts):
                continue
            seen_contracts[contract.name] = True
            user_type = u_provide_type[contract.name]
            if(not (check_contract(contract.name)) or (user_type and fill_type)):
                continue
            used_contract = get_cont_with_state_var(contract.name)
            if(used_contract == None):
                used_contract = contract
            errorsx = _tcheck_contract(used_contract)
                
            for ir in errorsx:
                _ir = ir.extok
                name = _ir.name
                func = _ir.function_name
                dnode = ir.dnode
                if(name == None):
                    name = "UNKNOWN"
                if(func == None):
                    func = "UNKNOWN"
                info = [" typecheck error: " ]
                info+=("Var name: " + name + " " + "Func name: " + func + " in " + str(dnode) + "\n")
                res = self.generate_result(info)
                results.append(res)
        end_time = time.time()
        print(f"Annotation count: {tcheck_parser.get_total_annotations()}")
        print(f"Function count: {function_count}")
        return results
