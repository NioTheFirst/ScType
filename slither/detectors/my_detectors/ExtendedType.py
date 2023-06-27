from collections import defaultdict
import os
import sys

#USAGE: file containing the structure representing an Extended type instance
#       Extended types have two main subclasses: token types and business types
#       Token types follow the default token structure of:
#           - numerator type(s)
#           - denominator type(s)
#           - normalization amt
#           - linked contract (for addresses)
#           - fields          (for objects)
#       Business types (usually one) are categorical, i.e. (fee, balance, ...) and their relations will be defined here

class ExtendedType():
    def __init__(self):
        #Initialized an 'undefined' data type
        self._name: Optional[str] = None
        self._function_name: Optional[str] = None
        self._contract_name: Optional[str] = None
        #Token type
        self._num_token_types = []
        self._den_token_types = []
        self._decimals = 0
        self._normalization = 0
        self._linked_contract = None
        self._fields: Optional[ExtendedType] = []
        #Business type
        self._business_type = None

    #Getters and setters for the fields
    @property
    def name(self):
        return(self._name)

    @name.setter
    def name(self, sname):
        self._name = sname

    @property
    def function_name(self):
        return(self._function_name)

    @function_name.setter
    def function_name(self, fname):
        self._functon_name = fname

    @property
    def contract_name(self):
        return(self._contract_name)
    
    @contract_name.setter
    def contract_name(self, cname):
        self._contract_name = cname
    
    @property
    def num_token_types(self):
        return(self._num_token_types)

    def add_num_token_type(self, token_type):
        if(token_type == -1):
            if(len(self._num_token_types) != 0 or token_type in self._num_token_types):
                return
            self._num_token_types.append(token_type)
        else:
            if(token_type in self._den_token_types):
                self._den_token_types.remove(token_type)
            else:
                if(-1 in self._num_token_types):
                    self._num_token_types.remove(-1)
                self._num_token_types.append(token_type)

    @property
    def den_token_types(self):
        return(self._den_token_types)

    def add_den_token_type(self, token_type):
        if(token_type == -1):
            if(len(self._den_token_types) != 0 or token_type in self._den_token_types):
                return
            self._den_token_types.append(token_type)
        else:
            if(token_type in self._num_token_types):
                self._num_token_types.remove(token_type)
            else:
                if(-1 in self._den_token_types):
                    self._den_token_types.remove(-1)
                self._den_token_types.append(token_type)
    @property
    def is_undefined(self) -> bool:
        if(len(self._num_token_type) == 0 and len(self._den_token_type) == 0):
            return True
        return False

    
    def init_constant(self):
        print("woow")
        

