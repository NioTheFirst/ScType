#Handles address things
#label to normalization
num_to_norm = {}
label_sets = {}
label_to_address = {}
global_address_counter = 0
temp_address_counter = -1000

class Address_label():
    def __init__(self, _head):
        self._head = _head
        self._set = {_head}

    
    @property
    def head(self):
        return(self._head)
    
    @head.setter
    def head(self, x):
        self._head = x

    @property
    def set(self):
        return(self._set)

    @set.setter
    def set(self, x):
        self._set = x

    def union(self, a):
        if(self._head < 0):
            if(a.head < 0 and self._head < a.head):
                a.head = self._head
            else:
                self._head = a.head
        else:
            if(a.head < 0 or self._head < a.head):
                a.head = self._head
            else:
                self._head = a.head
        temp_set = {}
        temp_set.union(self._set)
        temp_set.union(a.set)
        self._set = temp_set
        a.set = temp_set



def new_address(ir, isGlobal):
    global global_address_counter
    global temp_address_counter
    global label_sets
    global label_to_address
    _ir = ir.extok
    if(_ir.address != 'u'):
        return None
    if(isGlobal):
        global_address_counter+=1
        _ir.address = global_address_counter
    else:
        temp_address_counter+=1
        _ir.address = temp_address_counter
    label = Address_label(_ir.address)
    label_sets[_ir.address] = label
    label_to_address[_ir.address] = str(_ir.function_name)+":"+str(_ir.name)
    return _ir.address
        