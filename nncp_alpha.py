import ast, tokenize, csv, sys

# read specifiction 
with open(str(sys.argv[1]), 'r') as f: 
    spec = f.read()

# read code from file 
with open(str(sys.argv[2]), 'r', encoding='utf8') as f: 
    src = f.read()

# Node structure: used for the function representation.  
class Node:
    def __init__(self, func, args):
        self.func=func
        self.args=args

    def ExpString(self):
        if not isinstance(self.func, str):
            s=str(self.func)
            return s
        s=self.func+'('
        for i in self.args:
            if isinstance(i, Node):
                s+=i.ExpString()
            else:
                s+=str(i)
            if not i is self.args[-1]:
                s+=','
        s+=')'
        return s

# Global 
# tmep vars
root=Node('null',[])
flag='spec'     # spec for running the getAssignment for specification 
                # src for source file 
funcName = ""   # 

# Variables to check
spec_vars_list=[]

#create dictionary
spec_treedic={}
src_treedic={}

# use the tokenize to annotation in the specification file 
# The target annotation is used to ma 
with tokenize.open(str(sys.argv[1])) as f:
    token_src = tokenize.generate_tokens(f.readline)
    for token in token_src:
        #print(token)
        if token.type==60 and 'check' in token.string:
            tmpvars=token.string.split('check')[1].split(' ')
            spec_vars_list.extend(tmpvars)
            del spec_vars_list[0]

# get function name
def packFunc(node):
    global funcName
    if isinstance(node, ast.Name):
        if funcName == "":
            funcName = node.id
        else:
            funcName = node.id+"."+funcName
        return node.id
    else: # is an ast.Attribute
        if hasattr(node, 'attr'):
            if funcName == "":
                funcName = node.attr
            else: 
                funcName = node.attr+"."+funcName
        return packFunc(node.value)

def handleConstName(elem, treedic):
    #print(ast.dump(elem))
    if isinstance(elem, ast.Constant):
        return str(elem.value)
    elif isinstance(elem, ast.Name):
        if elem.id in treedic:
            return treedic[elem.id]
        else:
            return elem.id
    else:
        #print("Cannot handle object: ", elem)
        return False

def SliceStr(slice, treedic):
    tmpstr='['

    if isinstance(slice, ast.Index):
        dims=slice.value.elts
    elif isinstance(slice, ast.ExtSlice):
        dims=slice.dims
    else:
        print("Slice is an unrecognized object: ", slice)
    
    #print(dims)

    for i in dims:
        if isinstance(i, ast.Slice):
            tmpval=handleConstName(i.lower, treedic)
            if not tmpval==False:
                tmpstr+=tmpval
            tmpstr+=':'
            tmpval=handleConstName(i.upper, treedic)
            if not tmpval==False:
                tmpstr+=tmpval
            tmpval=handleConstName(i.step, treedic)
            if not tmpval==False:
                tmpstr+=':'+tmpval
        elif isinstance(slice, ast.Index):
            #print(ast.dump(i))
            tmpstr+=handleConstName(i, treedic)
        else:
            print("Element of slice is an unrecognized object: ", i)
        
        if not i == dims[-1]:
            tmpstr+=','

    tmpstr+=']'
    return tmpstr

# populate args
def addArgs(somenode, treedic, args):
    global funcName
    for i in args:
        #print(ast.dump(i))
        tmpval = handleConstName(i, treedic)
        if not tmpval==False:
            pass
        elif isinstance(i, ast.List):
            tmpval=Node('List', [])
            addArgs(tmpval, treedic, i.elts)
        elif isinstance(i, ast.Call):
            funcName=""
            packFunc(i.func)
            tmpval=Node(funcName, [])
            addArgs(tmpval, treedic, i.args)
        elif isinstance(i, ast.Subscript):
            tmpval=Node('Project', [])
            tmpval.args.append(i.value.id)
            tmpval.args.append(SliceStr(i.slice, treedic))
        elif isinstance(i, ast.BinOp):
            if isinstance(i.op, ast.Add):
                funcName='Add'
            elif isinstance(i.op, ast.Sub):
                funcName='Sub'
            elif isinstance(i.op, ast.Mult):
                funcName='Mult'
            elif isinstance(i.op, ast.MatMult):
                funcName='MatMult'
            else:
                print("Unsupported operation: ", i.op)
            tmpval=Node(funcName, [])
            args=[i.left.id, i.right.id]
            addArgs(tmpval, treedic, args)
        else:
            print("Unrecognized node: ", i)
        
        somenode.args.append(tmpval)

# visit assignments
class GetAssignments(ast.NodeVisitor):
    def visit_Assign(self, node):
        global flag, root, spec_treedic, src_treedic, funcName
        if flag=="src":
            if node.targets[0].id not in spec_treedic:
                return
            treedic=src_treedic
        else:
            treedic=spec_treedic
        #print(ast.dump(node.value))
        root=Node('null',[])
        tmpval=handleConstName(node.value, treedic)
        if not tmpval==False:
            root.func=tmpval
        elif isinstance(node.value, ast.List):
            root.func='List'
            addArgs(root, treedic, node.value.elts)
        elif isinstance(node.value, ast.Call):
            funcName=""
            packFunc(node.value.func)
            root.func=funcName
            addArgs(root, treedic, node.value.args)
        elif isinstance(node.value, ast.Subscript):
            root.func='Project'
            root.args.append(node.value.value.id)
            root.args.append(SliceStr(node.value.slice, treedic))
        elif isinstance(node.value, ast.BinOp):
            if isinstance(node.value.op, ast.Add):
                root.func='Add'
            elif isinstance(node.value.op, ast.Sub):
                root.func='Sub'
            elif isinstance(node.value.op, ast.Mult):
                root.func='Mult'
            elif isinstance(node.value.op, ast.MatMult):
                root.func='MatMult'
            else:
                print("Unsupported operation: ", node.value.op)
            args=[node.value.left.id, node.value.right.id]
            addArgs(root, treedic, args)
        else:
            print("Unrecognized node: ", node.value)
    
        treedic[node.targets[0].id]=root

#execute
# parse the specification file and build the spec_treeDict 
spec_tree=ast.parse(spec,mode='exec')
flag='spec'
GetAssignments().visit(spec_tree)

for i in spec_vars_list:
    if i not in spec_treedic:
        print("Error: Variable ",i," specified for checking is not defined in the specification.")
        sys.exit(0)

# parse and build the src tree and its dicationary 
src_tree=ast.parse(src,mode='exec')
flag='src'
GetAssignments().visit(src_tree)

#check for incompatibilities
for key in spec_vars_list:
    if key not in src_treedic:
        print("Warning: Variable ", key, " is not defined in the code.")
        continue
    if not spec_treedic[key].ExpString() == src_treedic[key].ExpString():
        print("Warning: Variable ", key, "does not match specification. Details: Specification: ",spec_treedic[key].ExpString(),". Code: ",src_treedic[key].ExpString(),".")
        continue
    print("Match: Variable ",key," matches specification. Details: ",spec_treedic[key].ExpString(),".")


