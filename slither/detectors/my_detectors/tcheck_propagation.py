from slither.core.solidity_types import UserDefinedType, ArrayType, MappingType
from slither.core.declarations import Structure, Contract
from slither.core.variables.variable import Variable
import copy
import tcheck_parser
import tcheck
from tcheck import errors
#USAGE: library for functions that help propagate types
#       these functions contain handling for ABSTRACT types as well (any type > abs_buf is an ABSTRACT type)
#       ABSTRACT types take priority over CONCRETE types (temporary handling for if statements)
#       ABSTRACT type comparison to CONCRETE type comparison always holds true 
from tcheck_parser import field_tuple_start, f_type_name, f_type_num, update_ratios


f_type_add = {
    (0, 0): 0,  #raw balance + raw balance = raw blaance
    #(0, 11): 1, #raw balance - fee = net balance 
    (1, 1): 1,  #net balance + net balance = net balance
    (2, 2): 2,  #accrud balance + accrued balance = accrued balance
    (0, 23): 1, #compound interest + balance = net balance
    (23, 0): 1,
    (1, 23) : 3, #compound interest + net balance = final balance
    (23, 1) : 3,
    (10, 10) : 10, #c. fee ratio + c. fee ratio = c.fee ratio
    (12, 12) : 12, #s. fee ratio + s. fee ratio = s.fee ratio
    (13, 13) : 13, #trans fee + trans fee
    (30, 0): 30,#reserve - any balance
    (30, 1): 30,
    (30, 2): 30,
    (30, 3): 30,
    (50, 0): 50, #debt + any balance
    (0, 50): 50,
    (50, 1): 50,
    (1, 50): 50,
    (50, 2): 50,
    (2, 50): 50,
    (50, 3): 50,
    (3, 50): 50
}

f_type_sub = {
    (0, 0): 0,  #raw balance - raw balance = raw blaance
    (1, 1): 1,  #net balance - net balance = net balance
    (2, 2): 2,  #accrud balance - accrued balance = accrued balance
    (0, 11): 1, #raw balance - t. fee = net balance 
    (0, 13): 1, #raw balance - t. fee (n) = net balance
    (0,14) : 1, #raw balance - t. fee (d) = net balance
    (10, 10) : 10, #c. fee ratio - c. fee ratio = c.fee ratio
    (12, 12) : 12, #s. fee ratio - s. fee ratio = s.fee ratio
    #(0, 23): 2, #compound interest + balance = accrued balance
    #(23, 0): 2,
    #(1, 23) : 3, #compound interest + net balance = final balance
    #(23, 1) : 3,
    (30, 0): 30,#reserve - any balance
    (30, 1): 30,
    (30, 2): 30,
    (30, 3): 30,
    (50, 0): 50, #debt - any balance
    (50, 1): 50,
    (50, 2): 50,
    (50, 3): 50,
}

f_type_mul = {
    (0, 0): 0,
    (1, 1): 1, #net bal / net bal (?)
    (0, 10) : 13, #raw balance * compound fee ratio (t)= transaction fee (n)
    (10, 0) : 13,
    (2, 10) : 13, #accrued balance * compound fee ratio (t) = transaction fee (n)
    (10, 2) : 13,
    (14, 10):11, #transaction fee (d) * compound fee ratio = transaction fee
    (10, 14):11,
    (0, 12):1, #raw balance * simple fee ratio = net balance
    (0, 12):1,
    (0, 20):2, #simple interest ratio * raw balance = accrued balance
    (20, 0):2,
    (1, 20):3, #net balance * simple interest ratio = final balance
    (20, 1):3,
    (0, 21):23, #compound interest ratio * raw balance = compound interest
    (21, 0):23,
    (22, 20):22, #simple intrest * simple interest ratio = simple interest
    (20, 22):22,
    (23, 21):23, #compound interest * compound interest ratio = compound interest
    (21, 23): 23, 
    (40, 0) : 0, #price/exchange rate * any balance = corresponding balance
    (0, 40) : 0,
    (40, 1) : 1,
    (1, 40) : 1,
    (40, 2) : 2,
    (1, 40) : 2,
    (40, 3) : 3,
    (3, 40) : 3,    
}

f_type_div = {
    (0, 0) : 0,
    (1, 1): 1, #net bal / net bal (?)
    (0, 10) : 14, #raw balance / c. fee ratio (t)= transaction fee (d)
    (2, 10) : 14, #accrued balance / c. fee ratio (t) = transaction fee (d)
    (13, 10): 11, #t. fee (n) / fee ratio = t. fee
    (0, 12):1, #raw balance / simple fee ratio = net balance
    (0, 20):2, #simple interest ratio * raw balance = accrued balance
    (20, 0):2,
    (1, 20):3, #net balance * simple interest ratio = final balance
    (20, 1):3,
    (0, 21):23, #compound interest ratio * raw balance = compound interest
    (21, 0):23,
    (22, 20):22, #simple intrest * simple interest ratio = simple interest
    (20, 22):22,
    (23, 21):23, #compound interest * compound interest ratio = compound interest
    (21, 23): 23, 
    (40, 0) : 0, #price/exchange rate * any balance = corresponding balance
    (0, 40) : 0,
    (40, 1) : 1,
    (1, 40) : 1,
    (40, 2) : 2,
    (1, 40) : 2,
    (40, 3) : 3,
    (3, 40) : 3,    
}

abs_buf = 10    

#USAGE: copies the token types from src variable to dest variable
def copy_token_type(dest, src):
    #Does not clear the variables
    _dest = dest.extok
    _src = src.extok
    for n in _src.num_token_types:
        _dest.add_num_token_type(n)
    for d in _src.den_token_types:
        _dest.add_den_token_type(d)
    if _src.linked_contract:
        _dest.linked_contract = _src.linked_contract
    _dest.value = _src.value
    _dest.address = _src.address
    for field in _src.fields:
        _dest.add_field(field)
    #_dest.finance_type = _src.finance_type

#USAGE: copies inverse token types from the 'src' ir node from the 'dest' ir node
def copy_inv_token_type(src, dest):
    _dest = dest.extok
    _src = src.extok
    for n in _src.num_token_types:
        _dest.add_den_token_type(n)
    for d in _src.den_token_types:
        _dest.add_num_token_type(d)
    if _src.linked_contract:
        _dest.linked_contract = _src.linked_contract
    

    #_dest.finance_type = _src.finance_type

#USAGE: copy and replace a token from a param_cache to an ir
#RETURNS: nN/A
def copy_pc_token_type(_src, dest):
    #src = copy.deepcopy(_src)
    #print(_src.extok)
    src = _src
    _dest = dest.extok
    _dest.token_type_clear()
    for n in src[0]:
        _dest.add_num_token_type(n)
    for d in src[1]:
        _dest.add_den_token_type(d)
    if(src[3] != None):
        _dest.linked_contract = src[3]
    if(src[4] != None):
        temp = tcheck.create_iconstant()
        #copy_token_type(field, temp)
        #temp.extok.name = field.extok.name
        #temp.extok.function_name = field.extok
        for field in src[4]:
            _dest.add_field(field)
    _dest.finance_type = src[5]
    _dest.address = src[6]
    _dest.value = src[7]


#USAGE: copies a finance type
def copy_ftype(src, dest):
    if(not(isinstance(src, Variable) and isinstance(dest, Variable))):
        return
    _src = src.extok
    _dest = dest.extok
    _dest.finance_type = _src.finance_type

#USAGE: assigns a finance type
def assign_ftype(ftype, dest):
    dest.extok.finance_type = ftype

#USAGE: deals with updates
def pass_update(dest, rsrcl, func, rsrcr = None):
    global update_ratios
    #Assign updates where dest is a ratio (and rsrcr exists)
    _dest = dest.extok
    dest_in_ratio = (_dest.finance_type in update_ratios)
    #print(f"Dest type: {_dest.finance_type}, Update_ratios: {update_ratios}")
    _rl = rsrcl.extok
    _rlf = _rl.finance_type
    _rlfp = _rl.pure_type
    l_in_ratio = (_rlfp in update_ratios)
    _rr = None
    _rrf = -1
    _rrfp = -1
    r_in_ratio = False
    if(rsrcr):
        _rr = rsrcr.extok
        _rrf = _rr.finance_type
        _rrfp = _rr.pure_type
        r_in_ratio = (_rrfp in update_ratios)
        if(dest_in_ratio):
            #print(f"Dest updated")
            _dest.updated = True
            update_ratios[_dest.finance_type] = True
    #print(f"Right type: {_rrf}, Left type: {_rlf}")
    #Checks for unupdated usage
    if(not(dest_in_ratio) and (r_in_ratio or l_in_ratio)):
        checked_ratio = -1
        updated = False
        if(r_in_ratio):
            checked_ratio = _rrfp
            updated = _rr.updated
            #print(f"Left side: {_rlfp}, Right side: {_rrfp}, Checked Ratio: {checked_ratio}")
            #print(updated)
        elif(l_in_ratio):
            checked_ratio = _rlfp
            updated = _rl.updated
            #print(f"Left side: {_rlfp}, Right side: {_rrfp}, Checked Ratio: {checked_ratio}")
        if(update_ratios[checked_ratio] == -1):
            #Set update ratio
            update_ratios[checked_ratio] = updated
        elif(update_ratios[checked_ratio] != updated):
            #print(f"Inconsistent updating of {checked_ratio} by {_rlf} and {_rrf}")
            return True

    #Propogate updated usage
    #if(_rl.updated or (_rr != None and _rr.updated)):
    #    _dest.updated = True

    #print(f"Final dest type: {_dest.finance_type}")



    

    

#USAGE: finance type propogation
def pass_ftype(dest, rsrcl, func, rsrcr = None):
    #dest is the finance destination
    #rsrcl is the left-most rhand side variable
    #rsrcr is the (optional) right-most rhand-side variable
    #func is the name of the function
    if(not(isinstance(rsrcl, Variable) and (rsrcr == None or isinstance(rsrcr, Variable)))):
        return False
    _rl = rsrcl.extok
    _rlf = _rl.finance_type
    _rlfp = _rl.pure_type
    _rr = None
    _rrf = -1
    _rrfp = -1
    if(rsrcr):
        _rr = rsrcr.extok
        _rrf = _rr.finance_type
        _rrfp = _rr.pure_type
        if(_rrf == -1):
            assign_ftype(_rlf, dest)
            pass_update(dest, rsrcl, func, rsrcr)
            return False
        if(_rlf == -1):
            assign_ftype(_rrf, dest)
            pass_update(dest, rsrcl, func, rsrcr)
            return False
    key = (_rlfp, _rrfp)
    print(f"Finance type key: {key}")
    if(func == "add"):
        if key in f_type_add:
            assign_ftype(f_type_add[key], dest)
        else:
            assign_ftype(-1, dest)
            return True
    if(func == "sub"):
        if key in f_type_sub:
            assign_ftype(f_type_sub[key], dest)
        else:
            assign_ftype(-1, dest)
            return True
    elif(func == "mul"):
        if key in f_type_mul:
            assign_ftype(f_type_mul[key], dest)
        else:
            assign_ftype(-1, dest)
            return True
    elif(func == "div"):
        if key in f_type_div:
            assign_ftype(f_type_div[key], dest)
        else:
            assign_ftype(-1, dest)
            return True
    elif(func == "compare"):
        if(_rlf != _rrf):
            return True
        assign_ftype(-1, dest)
    elif(func == "assign"):
        assign_ftype(_rlf, dest)
    elif(func == "pow"):
        assign_ftype(_rlf, dest)
    #print(f"Func: {func}")
    return(pass_update(dest, rsrcl, func, rsrcr))

        

#USAGE: directly copies a norm value. WARNING: skips typechecks associated with normalization
def copy_norm(src, dest):
    _src = src.extok
    _dest = dest.extok
    _dest.norm = _src.norm

#USAGE: copies all the types from a type tuple to an ir node
#RETURNS: null
def copy_token_tuple(ir, tt):
    #print("Check copy_toekn_tuple")
    print(tt)
    _ir = ir.extok
    #print("----")
    _ir.token_type_clear()
    if(isinstance(tt[0], int)):
        _ir.add_num_token_type(tt[0])
    else:
        for n in tt[0]:
            _ir.add_num_token_type(n)
    if(isinstance(tt[1], int)):
        _ir.add_den_token_type(tt[1])
    else:
        for d in tt[1]:
            _ir.add_den_token_type(d)
    if(isinstance(tt[2], int)):
        if(tt[2] == -404):
            _ir.norm = '*'
        else:
            _ir.norm = tt[2]
    elif(isinstance(tt[2], str)):
        _ir.norm = tt[2]
    else:
        _ir.norm = tt[2][0]
    _ir.address = tt[4]
    _ir.value = tt[3]
    if(len(tt) > field_tuple_start):
        _ir.finance_type = tt[5]
    propagate_fields(ir)
#[DEPRECATED] comapres the token types of two variables. Includes support for checking ABSTRACT types
"""def compare_token_type(varA, varB):
    A_num_types = copy_and_sort(varA.token_typen)
    A_den_types = copy_and_sort(varA.token_typed)
    B_num_types = copy_and_sort(varB.token_typen)
    B_den_types = copy_and_sort(varB.token_typed)
    if(_compare_token_type(A_num_types, B_num_types)):
        return _compare_token_type(A_den_types, B_den_types)
    return False
"""
#USAGE: comapres the extended types of two variables. Includes support for checking ABSTRACT types
def compare_token_type(varA, varB):
    _varA = varA.extok
    _varB = varB.extok
    A_num_types = copy_and_sort(_varA.num_token_types)
    A_den_types = copy_and_sort(_varA.den_token_types)
    B_num_types = copy_and_sort(_varB.num_token_types)
    B_den_types = copy_and_sort(_varB.den_token_types)
    if(_compare_token_type(A_num_types, B_num_types)):
        return _compare_token_type(A_den_types, B_den_types)
    return False

#USAGE: helper function for compare_token_type
def _compare_token_type(A_types, B_types):
    if(len(A_types) != len(B_types)):
        return False
    A_buffer = 0
    B_buffer = 0
    Apos = len(A_types)-1
    Bpos = len(B_types)-1
    while(Apos >= 0 or Bpos >= 0):
        if(Apos > -1 and A_types[Apos]>=abs_buf):
            if(A_types[Apos] > B_types[Bpos]):
                B_buffer+=1
            elif(A_types[Apos] == B_types[Bpos]):
                Bpos-=1
            else:
                while(A_types[Apos] < B_types[Bpos]):
                    A_buffer+=1
                    Bpos-=1
        else:
            while(Bpos >= 0 and B_types[Bpos] >= abs_buf):
                A_buffer+=1
                Bpos-=1
            if(Bpos < 0):
                Apos-=1
                continue
            if(Apos > -1 and A_types[Apos] > B_types[Bpos]):
                A_buffer-=1
            elif(Apos > -1 and A_types[Apos] == B_types[Bpos]):
                Bpos-=1
            else:
                while((Apos < 0 and Bpos >= 0) or A_types[Apos] < B_types[Bpos]):
                    B_buffer-=1
                    Bpos-=1
                    if(Bpos == -1):
                        break
        Apos-=1
    if(A_buffer != 0 or B_buffer != 0):
        return False
    return True

def get_raw_type(ir):
    ttype = ir.type
    changed = False
    while(True):
        #print(ttype)
        changed = False
        if(isinstance(ttype, ArrayType)):
            changed = True
            ttype = ttype.type
        elif(isinstance(ttype, MappingType)):
            changed = True
            ttype = ttype.type_to
        if(not(changed)):
            return ttype

#USAGE: given an ir, propogate it's fields
def propagate_fields(ir):
    _ir = ir.extok
    #print(f"Type: {ir.type}")
    ttype = get_raw_type(ir)
    #print(f"Final Type: {ttype}")
    #Field tuple propagation
    if(isinstance(ttype, UserDefinedType)):
        fields = None
        ttype = ttype.type
        if isinstance(ttype, Structure):
            fields = ttype.elems.items()
        #elif isinstance(ttype, Contract):
        #    fields = ttype.variables_as_dict
        if(fields == None):
            #print(" NO FIELDS")
            return
        #is an oobject, may have fields
        for field_name, field in fields:
            #search for type tuple in type file
            print(_ir.function_name)
            print(_ir.name)
            print(field_name)
            if(_ir.function_name == None or _ir.name == None or field_name == None):
                continue
            field_tt = tcheck_parser.get_field(_ir.function_name, _ir.name, field_name)
            if(field_tt):
                _field_tt = field.extok
                copy_token_tuple(field, field_tt)
                _ir.add_field(field)
                _field_tt.name = _ir.name+'.'+field_name
                _field_tt.function_name = _ir.function_name
                propagate_fields(field)
                _field_tt.name = field_name
        #print("FIELDS:")
        #_ir.print_fields()

#USAGE: returns the variable with the higher amount of ABSTRACT variables (used in dest propagation)
def greater_abstract(varA, varB):
    if(amt_abstract(varA) > amt_abstract(varB)):
        return varA
    return varB

#USAGE: returns the variable with the fewer amount of ABSTRACT variables
def lesser_abstract(varA, varB):
    if(amt_abstract(varA) < amt_abstract(varB)):
        return varA
    return varB

#USAGE: returns the amount of ABSTRACT types that a certain variable has
def amt_abstract(var):
    amt = 0
    for n in var.token_typen:
        if(n >= abs_buf):
            amt+=1
    for d in var.token_typed:
        if(d >= abs_buf):
            amt+=1
    return amt
#USAGE: personal copy and sort
def copy_and_sort(types):
    ret = []
    for i in types:
        ret.append(i)
    ret.sort()
    return(ret)


