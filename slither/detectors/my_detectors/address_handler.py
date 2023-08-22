#Handles address things
from slither.core.variables.variable import Variable
#label to normalization
num_to_norm = {}
label_sets = {}
label_to_address
global_address_counter = 0
temp_address_counter = -1000


def new_address(ir, isGlobal):
    global global_address_counter
    global temp_address_counter
    global label_sets
    global label_to_address
    if(not(isinstance(ir, Variable))):
        return None
    _ir = ir.extok
    if(_ir.address != 'u'):
        return None
    if(isGlobal):
        global_address_counter+=1
        _ir.address = global_address_counter
    else:
        temp_address_counter+=1
        _ir.address = temp_address_counter
    label_sets[_ir.address] = {_ir.address}
    label_to_address[_ir.address] = str(_ir.function_name)+":"+str(_ir.name)
        
