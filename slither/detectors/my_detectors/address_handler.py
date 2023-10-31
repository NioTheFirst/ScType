#Handles address things
#label to normalization
f_type_num = {
    -1: "undef",
    0: "raw balance",
    1: "net balance",
    2: "accrued balance",
    3: "final balance",
    10: "compound fee ratio (t)",
    11: "transaction fee",  
    12: "simple fee ratio",
    13: "transaction fee (n)",
    14: "transaction fee (d)",
    20: "simple interest ratio",
    21: "compound interest ratio",
    22: "simple interest",
    23: "compound interest",
    30: "reserve",
    40: "price/exchange rate",
    50: "debt",
}
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
        self._norm = 'u'
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
        if(self._head == -993 and norm == 0):
            print("Changed here")
        self._norm = norm

    @property
    def set(self):
        return(self._set)

    @set.setter
    def set(self, x):
        self._set = x

    def union(self, a):
        print(f"Head,Norm: {self.head}, {self._norm}   {a.head}, {a.norm}")
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

def type_file_new_address(name_key, isGlobal):
    global global_address_counter
    global temp_address_counter
    global label_sets
    global label_to_address
    global address_to_label
    if(name_key in address_to_label):
        return(label_sets[address_to_label[name_key]])
    else:
        upcounter = None
        if(isGlobal):
            global_address_counter+=1
            upcounter = global_address_counter
        else:
            temp_address_counter+=1
            upcounter = temp_address_counter
        label = Address_label(upcounter)
        label_to_address[upcounter] = name_key
        label_sets[upcounter] = label
        address_to_label[name_key] = upcounter
        print(f"Add to address_to_label {address_to_label}")
        
        return label

def new_address(ir, isGlobal):
    global global_address_counter
    global temp_address_counter
    global label_sets
    global label_to_address
    global address_to_label
    _ir = ir.extok
    if(not(isinstance(_ir.address, int))):
        _ir.address = 'u'
    
    print(f"prev address? {_ir.address}")
    if(_ir.address != 'u' and _ir.address != None):
        return label_sets[_ir.address]
    name_key = str(_ir.function_name)+":"+str(_ir.name)
    if(name_key in address_to_label):
        _ir.address = address_to_label[name_key]
        return label_sets[_ir.address]
    #Create new
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
        
