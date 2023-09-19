#Handles address things
#label to normalization
import tcheck_parser
from tcheck_parser import f_type_name, f_type_num, update_start
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
        self._norm = '*'
        self._finance_type = '*' #Reserve or balance...
  
    @property
    def head(self):
        return(self._head)
    
    @head.setter
    def head(self, x):
        self._head = x

    @property
    def finance_type(self):
        return(self._finance_type)
    @finance_type.setter
    def finance_type(self, x):
        self._finance_type = x
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
        if(self._norm != '*' and a.norm != '*'):
            if(self._norm != a.norm):
                return False
        elif(self._head < 0):
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
        temp_set = set()
        temp_set = temp_set.union(self._set)
        temp_set = temp_set.union(a.set)
        self._set = temp_set
        a.set = temp_set
        return True

    def __str__(self):
        f_type = "NULL"
        if(self._finance_type in f_type_num):
            f_type = f_type_num[self._finance_type]

        return(f"Head Addr: {self._head}\n"
               f"    Norm: {self._norm}\n"
               f"    Set: {str(self._set)}\n"
               f"    Fin: {f_type}")

def get_address_label(func_name, name):
    name_key = str(func_name) + ":" + str(name)
    if name_key in address_to_label:
        return(label_sets[address_to_label[name_key]])
    else:
        return None   

def new_address(ir, isGlobal):
    global global_address_counter
    global temp_address_counter
    global label_sets
    global label_to_address
    _ir = ir.extok
    if(not(isinstance(_ir.address, int))):
        _ir.address = 'u'
    print(f"prev address? {_ir.address}")
    if(_ir.address != 'u' and _ir.address != None):
        return label_sets[_ir.address]
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
    return label
        
