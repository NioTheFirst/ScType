"""
    Variable module
"""
from typing import Optional, TYPE_CHECKING, List, Union, Tuple

from slither.detectors.my_detectors.ExtendedType import ExtendedType
from slither.core.source_mapping.source_mapping import SourceMapping
from slither.core.solidity_types.type import Type
from slither.core.solidity_types.elementary_type import ElementaryType

if TYPE_CHECKING:
    from slither.core.expressions.expression import Expression

# pylint: disable=too-many-instance-attributes
class Variable(SourceMapping):
    def __init__(self):
        super().__init__()
        self._name: Optional[str] = None
        self._initial_expression: Optional["Expression"] = None
        self._type: Optional[Type] = None
        self._initialized: Optional[bool] = None
        self._visibility: Optional[str] = None
        self._is_constant = False
        self._is_immutable: bool = False
        self._is_reentrant: bool = True
        self._write_protection: Optional[List[str]] = None
        self._token_type = -2
        self._token_dim = 0;
        self._token_typen : List[int] = []
        self._token_typed : List[int] = []
        self._norm = -100;
        self._parent_function : Optional[str] = None
        self._link_function : Optional[str] = None
        self._tname: Optional[str] = None
        self._et = ExtendedType()

    @property
    def is_scalar(self) -> bool:
        return isinstance(self.type, ElementaryType)

    @property
    def expression(self) -> Optional["Expression"]:
        """
        Expression: Expression of the node (if initialized)
        Initial expression may be different than the expression of the node
        where the variable is declared, if its used ternary operator
        Ex: uint a = b?1:2
        The expression associated to a is uint a = b?1:2
        But two nodes are created,
        one where uint a = 1,
        and one where uint a = 2

        """
        return self._initial_expression

    @expression.setter
    def expression(self, expr: "Expression") -> None:
        self._initial_expression = expr

    @property
    def initialized(self) -> Optional[bool]:
        """
        boolean: True if the variable is initialized at construction
        """
        return self._initialized

    @initialized.setter
    def initialized(self, is_init: bool):
        self._initialized = is_init

    @property
    def uninitialized(self) -> bool:
        """
        boolean: True if the variable is not initialized
        """
        return not self._initialized
    
    @property
    def extok(self):
        return self._et

    @property
    def name(self) -> Optional[str]:
        """
        str: variable name
        """
        return self._name

    @name.setter
    def name(self, name):
        self._et.name = name
        self._name = name
    
    @property
    def link_function(self)->Optional[str]:
        return self._et.linked_contract

    @link_function.setter
    def link_function(self, function):
        self._link_function = function
        self._et.linked_contract = function

    def change_name(self, name):
        self._tname = name
    
    @property
    def norm(self) -> int:
        return self._norm

    @norm.setter
    def norm(self, norm):
        self._norm = norm

    @property
    def tname(self)-> Optional[str]:
        return self._tname

    @property
    def parent_function(self) -> Optional[str]:
        """
        str: variable name
        """
        return self._parent_function

    @parent_function.setter
    def parent_function(self, name):
        self._et.function_name = name
        self._parent_function = name

    @property
    def token_typen(self) -> Optional[int]:
        #return self._token_typen
        return self._et.num_token_types

    
    def add_token_typen(self, a):
        for denom in self._token_typed:
            if(denom == a):
                if(a!=-1):
                    self._token_typed.remove(denom)
                    return
        if((a in self._token_typen and a == -1) or (a==-1 and len(self._token_typen) > 0 and (not(a in self._token_typen)))):
            return
        if(-1 in self._token_typen and a != -1):
            self._token_typen.remove(-1)
        self._token_typen.append(a)
        self._et.add_num_token_type(a)

    @property
    def token_typed(self) -> Optional[int]:
        #return self._token_typed
        return self._et.den_token_types


    def add_token_typed(self, a):
        for num in self._token_typen:
            if(num == a):
                if(a != -1):
                    self._token_typen.remove(num)
                    return
        if((a in self._token_typed and a == -1) or (a==-1 and len(self._token_typed) > 0 and (not(a in self._token_typed)))):
            return
        if(-1 in self._token_typed and a != -1):
            self._token_typed.remove(-1)
        self._token_typed.append(a)
        self._et.add_den_token_type(a)

    @property
    def token_type(self):
        return self._token_type

    @token_type.setter
    def token_type(self, toke_type):
        self._token_type = toke_type

    @property
    def token_dim(self):
        return self._token_dim

    @token_type.setter
    def token_dim(self, toke_dim):
        self._token_dim = toke_dim
    @property
    def type(self) -> Optional[Union[Type, List[Type]]]:
        return self._type

    @type.setter
    def type(self, types: Union[Type, List[Type]]):
        self._type = types

    @property
    def is_constant(self) -> bool:
        return self._is_constant

    @is_constant.setter
    def is_constant(self, is_cst: bool):
        self._is_constant = is_cst

    @property
    def is_reentrant(self) -> bool:
        return self._is_reentrant

    @is_reentrant.setter
    def is_reentrant(self, is_reentrant: bool) -> None:
        self._is_reentrant = is_reentrant

    @property
    def write_protection(self) -> Optional[List[str]]:
        return self._write_protection

    @write_protection.setter
    def write_protection(self, write_protection: List[str]) -> None:
        self._write_protection = write_protection

    @property
    def visibility(self) -> Optional[str]:
        """
        str: variable visibility
        """
        return self._visibility

    @visibility.setter
    def visibility(self, v: str) -> None:
        self._visibility = v

    def set_type(self, t: Optional[Union[List, Type, str]]) -> None:
        if isinstance(t, str):
            self._type = ElementaryType(t)
            return
        assert isinstance(t, (Type, list)) or t is None
        self._type = t

    @property
    def is_immutable(self) -> bool:
        """
        Return true of the variable is immutable

        :return:
        """
        return self._is_immutable

    @is_immutable.setter
    def is_immutable(self, immutablility: bool) -> None:
        self._is_immutable = immutablility

    ###################################################################################
    ###################################################################################
    # region Signature
    ###################################################################################
    ###################################################################################

    @property
    def signature(self) -> Tuple[str, List[str], List[str]]:
        """
        Return the signature of the state variable as a function signature
        :return: (str, list(str), list(str)), as (name, list parameters type, list return values type)
        """
        # pylint: disable=import-outside-toplevel
        from slither.utils.type import (
            export_nested_types_from_variable,
            export_return_type_from_variable,
        )

        return (
            self.name,
            [str(x) for x in export_nested_types_from_variable(self)],
            [str(x) for x in export_return_type_from_variable(self)],
        )

    @property
    def signature_str(self) -> str:
        """
        Return the signature of the state variable as a function signature
        :return: str: func_name(type1,type2) returns(type3)
        """
        name, parameters, returnVars = self.signature
        return name + "(" + ",".join(parameters) + ") returns(" + ",".join(returnVars) + ")"

    @property
    def solidity_signature(self) -> str:
        name, parameters, _ = self.signature
        return f'{name}({",".join(parameters)})'

    def __str__(self) -> str:
        return self._name
