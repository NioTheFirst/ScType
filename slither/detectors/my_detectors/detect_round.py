from collections import defaultdict
from slither.core.variables.local_variable import LocalVariable
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import Binary, Assignment, BinaryType, LibraryCall
from slither.slithir.variables import Constant, ReferenceVariable, TemporaryVariable, LocalIRVariable


def is_division(ir):
    #print("division found")
    if isinstance(ir, Binary):
        if ir.type == BinaryType.DIVISION:
            return True

    if isinstance(ir, LibraryCall):
        if ir.function.name.lower() in [
            "div",
            "safediv",
        ]:
            if len(ir.arguments) == 2:
                if ir.lvalue:
                    return True
    return False

def is_addition(ir):
    #print("addition found")
    if isinstance(ir, Binary):
        if ir.type == BinaryType.ADDITION:
            return True
    if isinstance(ir, LibraryCall):
        if ir.function.name.lower() in [
                "add",
                "safeadd",
        ]:
            if len(ir.arguments) == 2:
                if ir.lvalue:
                    return True
    return False

def is_multiplication(ir):
    if isinstance(ir, Binary):
        if ir.type == BinaryType.MULTIPLICATION:
            return True

    if isinstance(ir, LibraryCall):
        if ir.function.name.lower() in [
            "mul",
            "safemul",
        ]:
            if len(ir.arguments) == 2:
                if ir.lvalue:
                    return True
    return False

#def contains_equal(ir):
#    if isinstance(ir, Binary):
#        if ir.type == BinaryType.
def is_assert(node):
    if node.contains_require_or_assert():
        return True
    # Old Solidity code where using an internal 'assert(bool)' function
    # While we dont check that this function is correct, we assume it is
    # To avoid too many FP
    if "assert(bool)" in [c.full_name for c in node.internal_calls]:
        return True
    return False

# _exploreNon also checks from rounding + 1
def _exploreNon(to_explore, rurd, roundup, additions, add_constants):  # pylint: disable=too-many-branches
    explored = set()
    divisions = defaultdict(list)
    while to_explore:  # pylint: disable=too-many-nested-blocks
        node = to_explore.pop()
        if node in explored:
            continue
        explored.add(node)
        equality_found = False
        last_var = None
        # List of nodes related to one bug instance
        for ir in node.irs:
            #print(ir)
            if isinstance(ir, Assignment):
                last_var = ir.lvalue
                if add_constants[last_var] == None:
                    add_constants[last_var] = []
            if is_addition(ir):
                if(not isinstance(ir.lvalue, TemporaryVariable)):
                    last_var = ir.lvalue
                    if add_constants[last_var] == None:
                        add_constants[last_var] = []
                    #print(last_var)
            if is_division(ir):
                if(not isinstance(ir.lvalue, TemporaryVariable)):
                    last_var = ir.lvalue
                    if add_constants[last_var] == None:
                        add_constants[last_var] = []
                    if divisions[last_var] == None:
                        divisions[last_var] = []
                    divisions[last_var]+=[ir.lvalue]
                        
        for ir in node.irs:
            # check for Constant, has its not hashable (TODO: make Constant hashable)
            if isinstance(ir, Assignment) and not isinstance(ir.rvalue, Constant):
                if ir.rvalue in additions:
                    # Avoid dupplicate. We dont use set so we keep the order of the nodes
                    if node not in additions[ir.rvalue]:
                        additions[ir.lvalue] = additions[ir.rvalue] + [node]
                    else:
                        additions[ir.lvalue] = additions[ir.rvalue]
            if is_addition(ir) and divisions[last_var] != None:
                print("here")
                add_arguments = ir.read if isinstance(ir, Binary) else ir.arguments
                for r in add_arguments:
                    if(r == 1):
                        rurd.append([node])
                        break
            if is_division(ir) and last_var != None:
                #print(additions)
                add_arguments = ir.read if isinstance(ir, Binary) else ir.arguments
                nodes = []
                div_l = ir.lvalue
                div_r = ir.variable_right
                flag = False
                nodes = []
                for r in add_arguments:
                    #if not isinstance(r, Constant) and (r in additions):
                    if (r in additions):
                        for c in add_constants[r]:
                            print("checking add_constants...")
                            print(c.value)
                            print(div_r.value)
                            if(c.value>div_r.value/2 and c.value<=div_r.value):
                                # Dont add node already present to avoid dupplicate
                                # We dont use set to keep the order of the nodes
                                #print("in additions??: "+ r)
                                flag = True
                                break
                        if not flag:
                            break
                if flag:
                    print("RU: ", (last_var.name))
                    print(rurd)
                    print(roundup)
                else:
                    print("RD: ", last_var.name)
                print(" RURD Comparison name: ", (last_var.name))
                if (not flag) and [last_var.name] in roundup: #and not isinstance(last_var, LocalVariable):
                    #if not last_var.name in rurd:
                    #    rurd+=[last_var.name]
                    #    print("Roundup round down detected: " , (last_var))
                    #rurd+=[node]
                    #if node in additions[r]:
                    #    nodes += [n for n in additions[r] if n not in nodes]
                    #else:
                    #    nodes += [n for n in additions[r] + [node] if n not in nodes]
                    print(node)
                    rurd.append([node])
        for son in node.sons:
            to_explore.add(son)
def _explore(to_explore, f_results, v_results,  additions, add_constants):  # pylint: disable=too-many-branches
    explored = set()
    while to_explore:  # pylint: disable=too-many-nested-blocks
        node = to_explore.pop()

        if node in explored:
            continue
        explored.add(node)

        equality_found = False
        # List of nodes related to one bug instance
        node_results = []
        var_results = []
        last_var = None
        for ir in node.irs:
            print(ir)
            if isinstance(ir, Assignment):
                #print("assignment found")
                last_var = ir.lvalue
                if add_constants[last_var] == None:
                    add_constants[last_var] = []
                #print(last_var)
            if is_addition(ir):
                if(isinstance(ir.lvalue, ReferenceVariable)):
                    print("ir is reference")
                if(not isinstance(ir.lvalue, TemporaryVariable)):
                    #print("ir is not temporary")
                    last_var = ir.lvalue
                    if add_constants[last_var] == None:
                        add_constants[last_var] = []
                if is_division(ir) and last_var != None:
                    if(not isinstance(ir.lvalue, TemporaryVariable)):
                        last_var = ir.lvalue
                        if add_constants[last_var] == None:
                            add_constants[last_var] = []
        print("MRA: ", (last_var))
        for ir in node.irs:
            #print(ir)
            # check for Constant, has its not hashable (TODO: make Constant hashable)
            if isinstance(ir, Assignment) and not isinstance(ir.rvalue, Constant):
                if ir.rvalue in additions:
                    # Avoid dupplicate. We dont use set so we keep the order of the nodes
                    if node not in additions[ir.rvalue]:
                        additions[ir.lvalue] = additions[ir.rvalue] + [node]
                    else:
                        additions[ir.lvalue] = additions[ir.rvalue]
                    #print("switched?")
                    #print(ir.lvalue)
                    #print(ir.rvalue)
            #if isinstance(ir, Assignment):
            #    print("assignment found")
            #    last_var = ir.lvalue
            #    add_constants[last_var] = []
            #    print(last_var)
            if is_addition(ir):
                additions[ir.lvalue] = [node]
                if isinstance(ir.variable_left, Constant):
                    add_constants[last_var]+=[ir.variable_left]
                if isinstance(ir.variable_right, Constant):
                    #print("right var aded")
                    add_constants[last_var]+=[ir.variable_right]
                #additions[ir.variable_right] = [node]
                #if isinstance(ir.lvalue, Constant):
                #    add_constants[ir.lvalue] = ir.lvalue
                #print(last_var)
                #print(ir.lvalue)
                #print(ir.variable_left)
                #print(ir.variable_right)
                #print(add_constants[last_var])
                #recursively find the head assignment
            if is_division(ir):
                #print(additions)
                
                add_arguments = ir.read if isinstance(ir, Binary) else ir.arguments
                nodes = []
                div_l = ir.lvalue
                div_r = ir.variable_right
                for r in add_arguments:
                    print ("args",  r)
                    #print("-----")
                    #print (add_constants[r])
                    #if not isinstance(r, Constant) and (r in additions):
                    if (r in additions):
                        for c in add_constants[r]:
                            print(c.value)
                            if(c.value>div_r.value/2 and c.value<=div_r.value):
                                # Dont add node already present to avoid dupplicate
                                # We dont use set to keep the order of the nodes
                                #print("in additions??: "+ r)
                                if not last_var in var_results:
                                    print("Round up var added:", (last_var))
                                    var_results+=[last_var.name]
                                if node in additions[r]:
                                    nodes += [n for n in additions[r] if n not in nodes]
                                else:
                                    nodes += [n for n in additions[r] + [node] if n not in nodes]
                                break
                if nodes:
                    node_results = nodes

            if isinstance(ir, Binary) and ir.type == BinaryType.EQUAL:
                equality_found = True

        if node_results:
            # We do not track the case where the multiplication is done in a require() or assert()
            # Which also contains a ==, to prevent FP due to the form
            # assert(a == b * c + a % b)
            if not (is_assert(node) and equality_found):
                f_results.append(node_results)
        if var_results:
            v_results.append(var_results)
        for son in node.sons:
            to_explore.add(son)
def detect_add_b4_div(contract):
    results = []
    v_results = []
    rurd = []
    for function in contract.functions_declared:
        if not function.entry_point:
            continue
        f_results = []
        #v_results = []
        additions = defaultdict(list)
        add_constants = defaultdict(list)
        _explore({function.entry_point}, f_results, v_results, additions, add_constants)
        print("V_RESULTS:______________________________")
        for v in v_results:
            print(v)
        _exploreNon({function.entry_point}, rurd, v_results, additions, add_constants)
        for f_result in rurd:
            
            results.append((function, f_result))
    return results
class detect_round(AbstractDetector):
    """
    Detects round up round down functions
    """

    ARGUMENT = 'detect_round' # slither will launch the detector with slither.py --detect mydetector
    HELP = 'Help printed by slither'
    IMPACT = DetectorClassification.INFORMATIONAL
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = 'Initialized i guess?'

    WIKI_TITLE = 'woops'
    WIKI_DESCRIPTION = 'i am initializing'
    WIKI_EXPLOIT_SCENARIO = 'finding external'
    WIKI_RECOMMENDATION = 'i will do something later'

    def _detect(self):
        results = []
        for contract in self.contracts:
            #TODO
            add_b4_div = detect_add_b4_div(contract)
            if add_b4_div:
                for (func, nodes) in add_b4_div:
                    info = [
                            func,
                            " performs an add before division (basic) "         
                    ]
                    nodes.sort(key = lambda x:x.node_id)
                    for node in nodes:
                        info += ["\t= ", node, "\n"]
                    res = self.generate_result(info)
                    results.append(res)

        return results
