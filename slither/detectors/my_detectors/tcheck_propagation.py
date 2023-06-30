#USAGE: library for functions that help propagate types
#       these functions contain handling for ABSTRACT types as well (any type > abs_buf is an ABSTRACT type)
#       ABSTRACT types take priority over CONCRETE types (temporary handling for if statements)
#       ABSTRACT type comparison to CONCRETE type comparison always holds true 

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

    for field in _src.fields:
        _dest.add_field(field)

#USAGE: copies inverse token types from the 'src' ir node from the 'dest' ir node
def copy_inv_token_type(src, dest):
    _dest = dest.extok
    _src = src.extok
    for n in _src.num_token_types:
        _dest.add_den_token_type(n)
    for d in _src.den_token_types:
        _dest.add_den_token_type(d)
    if _src.linked_contract:
        _dest.linked_contract = _src.linked_contract

#USAGE: copy and replace a token from a param_cache to an ir
#RETURNS: nN/A
def copy_pc_token_type(src, dest):
    _dest = dest.extok
    _dest.token_type_clear()
    for n in src[0]:
        _dest.add_num_token_type(n)
    for d in src[1]:
        _dest.add_den_token_type(d)
    if(src[3] != None):
        _dest.linked_contract = src[3]
    if(src[4] != None):
        for field in _src[4]:
            _dest.add_field(field)


#USAGE: directly copies a norm value. WARNING: skips typechecks associated with normalization
def copy_norm(src, dest):
    _src = src.extok
    _dest = dest.extok
    _dest.norm = _src.norm

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
