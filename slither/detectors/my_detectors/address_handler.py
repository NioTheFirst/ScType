#Handles address things
#label to normalization
num_to_norm = {}
label_sets = {}
label_to_address = {}
address_to_label = {}
global_address_counter = 0
temp_address_counter = -1000

norm_offsets = {}

class Address_label():
    def __init__(self, _head):
        self._head = _head
        self._set = {_head}
        self._norm = "norm("+str(_head)+")"
  
    @property
    def head(self):
        return(self._head)
    
    @head.setter
    def head(self, x):
        self._head = x

    @property
    def norm(self):
        return(self._norm)

    @norm.setter
    def norm(self, norm):
        self._norm = norm

    @property
    def set(self):
        return(self._set)

    @set.setter
    def set(self, x):
        self._set = x

    def union(self, a):
        if(a.head > 0 and self.head > 0 and a.head != self.head):
            return False
        if(self._head < 0):
            if(a.head < 0 and self._head < a.head):
                a.head = self._head
                a.norm = self._norm
            else:
                self._head = a.head
                self._norm = a.norm
        else:
            if(a.head < 0 or self._head < a.head):
                a.head = self._head
                a.norm = self._norm
            else:
                self._head = a.head
                self._norm = a.norm
        temp_set = {}
        temp_set.union(self._set)
        temp_set.union(a.set)
        self._set = temp_set
        a.set = temp_set
        return True

    def __str__(self):
        return(f"Head: {self._head}\n"
               f"    Norm: {self._norm}\n"
               f"    Set: {self._set}")



def new_address(ir, isGlobal):
    global global_address_counter
    global temp_address_counter
    global label_sets
    global label_to_address
    _ir = ir.extok
    print(f"prev address? {_ir.address}")
    if(_ir.address != 'u' and _ir.address != None):
        return None
    if(isGlobal):
        global_address_counter+=1
        print(f"global assignment: {global_address_counter}")
        _ir.address = global_address_counter
    else:
        temp_address_counter+=1
        _ir.address = temp_address_counter
    label = Address_label(_ir.address)
    label_sets[_ir.address] = label
    name_key = str(_ir.function_name)+":"+str(_ir.name)
    label_to_address[_ir.address] = name_key
    address_to_label[name_key] = _ir.address
    print(_ir.address)
    return _ir.address
        
