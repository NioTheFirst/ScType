#USAGE: library for functions that help propagate types
#       these functions contain handling for ABSTRACT types as well (any type > abs_buf is an ABSTRACT type)
#       ABSTRACT types take priority over CONCRETE types (temporary handling for if statements)
#       ABSTRACT type comparison to CONCRETE type comparison always holds true 

abs_buf = 10    

#USAGE: comapres the token types of two variables. Includes support for checking ABSTRACT types
def compare_token_type(varA, varB):
    A_num_types = varA.token_typen.copy().sort()
    A_den_types = varA.token_typed.copy().sort()
    B_num_types = varB.token_typen.copy().sort()
    B_den_types = varB.token_typed.copy().sort()
    if(_compare_token_type(A_num_types, B_num_types)):
        return _compare_token_type(A_den_types, B_den_types)
    return False

#USAGE: helper function for compare_token_type
def _compare_token_type(A_types, B_types):
    if(len(A_types) != len(B_types)):
        return False
    A_buffer = 1
    B_buffer = 1
    B_pos = len(B_types)-1
    for i in range(len(A_types), -1, -1):
        if(A_types[i]>=abs_buf):
            if(A_types[i] > B_types[Bpos]):
                B_buffer+=1
            elif(A_num_types[i] == B_num_types[Bpos]):
                Bpos-=1
            else:
                while(A_types[i] < B_types[Bpos]):
                    A_buffer+=1
                    Bpos-=1
        else:
            while(B_types[Bpos] >= abs_buf):
                A_buffer+=1
                Bpos-=1
            if(A_types[i] > B_types[Bpos]):
                A_buffer-=1
            elif(A_num_types[i] == B_num_types[Bpos]):
                Bpos-=1
            else:
                while(A_types[i] < B_types[Bpos]):
                    B_buffer-=1
                    Bpos-=1
    if(A_buffer != 0 or B_buffer != 0):
        return False
    return True

#USAGE: returns the variable with the higher amount of ABSTRACT variables (used in dest propagation)
def greater_abstract(varA, varB):
    A_abstract = 0
    B_abstract = 0
    for n in varA.token_typen:
        if(n >= abs_buf):
            A_abstract+=1
    for d in varA.token_typed:
        if(d >= abs_buf):
            A_abstract+=1
    for n in varB.token_typen:
        if(n >= abs_buf):
            B_abstract+=1
    for d in varB.token_typed:
        if(d >= abs_buf):
            B_abstract+=1
    if(A_abstract > B_abstract):
        return varA
    return varB

