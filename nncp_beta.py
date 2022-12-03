import ast, tokenize, csv, sys

# read specifiction 
with open(str(sys.argv[1]), 'r', encoding='utf8') as f: 
    spec = f.read()

# read code from file 
with open(str(sys.argv[2]), 'r', encoding='utf8') as f: 
    src = f.read()

def CSList(args):
    s=''
    for i in args:
        if isinstance(i, Node):
            s+=i.ExpString()
        else:
            s+=str(i)
        if not i is args[-1]:
            s+=','
    return s

# Node structure: used for the function representation.  
class Node:
    def __init__(self, func, args):
        self.func=func
        self.args=args
    
    def traverse(self):
        s='Node(func=\"'+self.func+'\", args=['
        for i in self.args:
            if isinstance(i, Node):
                s+=i.traverse()
                if not i == self.args[-1]:
                    s+=', '
            else:
                s+=str(i)
        s+='])'
        return s
    
    def ExpString(self):
        if not isinstance(self.func, str):
            s=str(self.func)
            return s
        elif self.func=='FList(':
            s=""
            for elem in self.args:
                s+=elem.ExpString()
                if not elem is self.args[-1]:
                    s+='.'
            return s
        elif self.func=='List(':
            s='['+CSList(self.args)+']'
            return s
        elif self.func=='Tuple(':
            s='('+CSList(self.args)+')'
            return s
        elif self.func=='Set(':
            s='{'+CSList(self.args)+'}'
            return s
        elif self.func=='Dict(':
            s='{'
            for i in self.args:
                s+=i.func+':'
                if isinstance(i.args[0], Node):
                    s+=i.args[0].ExpString()
                else:
                    s+=str(i.args[0])
                if not i is self.args[-1]:
                    s+=','
            s+='}'
            return s
        elif self.func=='Project(':
            op=''
        elif self.func=='Add(':
            op='+'
        elif self.func=='Sub(':
            op='-'
        elif self.func=='Mult(':
            op='*'
        elif self.func=='MatMult(':
            op=' MatMult '
        elif self.func=='Div(':
            op='/'
        
        if self.func=='Project(' or self.func=='Add(' or self.func=='Sub(' or self.func=='Mult(' or self.func=='MatMult(' or self.func=='Div(':
            if isinstance(self.args[0], Node):
                s=self.args[0].ExpString()
            else:
                s=str(self.args[0])
            s+=op
            if isinstance(self.args[1], Node):
                s+=self.args[1].ExpString()
            else:
                s+=str(self.args[1])
            return s

        s=self.func+'('+CSList(self.args)+')'
        return s

# Global 
# tmep vars
root=Node('null',[])
flag='spec'     # spec for running the getAssignment for specification 
                # src for source file 
funcName = ""   # 

# Variables to check
spec_vars_list=set()

#create dictionary
spec_treedic={}
src_treedic={}

check_flag=False

# use the tokenize to annotation in the specification file 
# The target annotation is used to ma 
with tokenize.open(str(sys.argv[1])) as f:
    token_src = tokenize.generate_tokens(f.readline)
    for token in token_src:
        #print(token)
        if token.type==60 and 'check' in token.string:
            tmpvars=token.string.split('check')[1].split(' ')
            del tmpvars[0]
            spec_vars_list|=set(tmpvars)
            check_flag=True

if(not check_flag):
    print("Warning: No check comment in specification.\n")

# get function name
# get function name
def getFuncName(node, funcName, funcNode, treedic):
    if isinstance(node, ast.Name):
        if funcName == "":
            funcName = node.id
        else:
            funcName = node.id+"."+funcName
        return funcName
    elif isinstance(node, ast.Attribute): # is an ast.Attribute
        if hasattr(node, 'attr'):
            if funcName == "":
                funcName = node.attr
            else: 
                funcName = node.attr+"."+funcName
        return getFuncName(node.value, funcName, funcNode, treedic)
    elif isinstance(node, ast.Call):
        #funcNode=Node("Dot(",[node])
        packFunc(node, funcNode, treedic)
        #funcNode.args.append(x)
        #handleLangFeat(node, treedic=funcTree)
    else:
        print("getFuncName: unknown Function name {}".format(node))
        print("instance type: {}".format(type(node)))
    return funcName

def packFunc(node, funcNode, treedic):
    funcName ="" 
    global funcTree
    if isinstance(node, ast.Call):
        funcName = getFuncName(node.func, "", funcNode, treedic)
        #print(funcName)
        tmpNode = Node(funcName, [])
        #print(tmpNode.traverse())
        addArgs(tmpNode,treedic,node.args)
        #print(tmpNode.traverse())
        funcNode.args.append(tmpNode)
        return funcNode
    else:
        print("unknown instance {}".format(node))
        print("instance: {}".format(ast.dump(node)))

def handleConstName(elem, treedic):
    #print(ast.dump(elem))
    if isinstance(elem, ast.Constant):
        if isinstance(elem.value,str):
            return '\''+elem.value+'\''
        return elem.value
    elif isinstance(elem, ast.Name):
        #if isinstance(elem.id, Node):
        #    print(elem.id.traverse())
        #print(treedic)
        if elem.id in treedic:
            return treedic[elem.id]
        else:
            return elem.id
    elif not hasattr(elem, '__dict__'):
        return elem
    else:
        #print("Cannot handle object: ", elem)
        return None

def SliceStr(slice, treedic):
    #print(ast.dump(slice))

    tmpstr='['

    tmpval = handleConstName(slice, treedic)
    if tmpval is not None:
        tmpstr+=tmpval+']'
        return tmpstr
    elif isinstance(slice, ast.Index):
        dims=slice.value.elts
    elif isinstance(slice, ast.Tuple):
        dims=slice.elts
    elif isinstance(slice, ast.ExtSlice):
        dims=slice.dims
    elif isinstance(slice, ast.Call):
        return handleLangFeat(slice,treedic).ExpString()
    elif isinstance(slice, ast.Slice):
        dims=[slice]
    else:
        print("Slice is an unrecognized object: ", ast.dump(slice))
    
    #print(dims)

    for i in dims:
        if isinstance(i, ast.Slice):
            if i.lower is None:
                tmpstr+=':'
                if not i == dims[-1]:
                    tmpstr+=','
                continue
            
            tmpval=handleConstName(i.lower, treedic)
            if tmpval is not None:
                tmpstr+=tmpval
            tmpstr+=':'
            tmpval=handleConstName(i.upper, treedic)
            if tmpval is not None:
                tmpstr+=tmpval
            tmpval=handleConstName(i.step, treedic)
            if tmpval is not None:
                tmpstr+=':'+tmpval
        elif isinstance(slice, ast.Index):
            #print(ast.dump(i))
            tmpstr+=handleConstName(i, treedic)
        elif isinstance(i, ast.Name):
            tmpval=handleConstName(i, treedic)
            if isinstance(tmpval, Node):
                tmpstr+=tmpval.ExpString()
            else:
                tmpstr+=tmpval
        else:
            print("Element of slice is an unrecognized object: ", i)
        
        if not i == dims[-1]:
            tmpstr+=','

    tmpstr+=']'
    return tmpstr

#handle Python language features
def handleLangFeat(feat, treedic):
    global funcName
    node=Node('null',[])
    tmpval=handleConstName(feat, treedic)
    #print(tmpval)
    if tmpval is not None:
        if not hasattr(tmpval, '__dict__'):
            return tmpval
        else:
            node=tmpval
    elif isinstance(feat, ast.Attribute):
        return getFuncName(feat, "", Node("null",[]), treedic)
    elif isinstance(feat, ast.List):
        node.func='List('
        addArgs(node, treedic, feat.elts)
    elif isinstance(feat, ast.Tuple):
        node.func='Tuple('
        addArgs(node, treedic, feat.elts)
    elif isinstance(feat, ast.Set):
        node.func='Set('
        addArgs(node, treedic, feat.elts)
    elif isinstance(feat, ast.Dict):
        node.func='Dict('
        #print(ast.dump(feat))
        #print(ast.dump(feat.keys[0]))
        for idx, key in enumerate(feat.keys):
            tmpval=Node(key.value, [])
            tmparg=[feat.values[idx]]
            addArgs(tmpval, treedic, tmparg)
            node.args.append(tmpval)
    elif isinstance(feat, ast.Call):
        funcName=""
        funcNode=Node("FList(",[])
        node=packFunc(feat,funcNode,treedic)
    elif isinstance(feat, ast.Subscript):
        node.func='Project('
        if hasattr(feat.value, 'id'):
            node.args.append(feat.value.id)
        elif isinstance(feat.value, ast.Subscript):
            node.args.append(handleLangFeat(feat.value,treedic))
        else:
            print('Unrecognized subscript:', ast.dump(feat.value))
        node.args.append(SliceStr(feat.slice, treedic))
    elif isinstance(feat, ast.UnaryOp): #lazy method
        if isinstance(feat.op, ast.UAdd):
            node=handleLangFeat(feat.operand,treedic)
        if isinstance(feat.op, ast.USub):
            node.func='Mult('
            node.args=[-1,handleLangFeat(feat.operand,treedic)]
    elif isinstance(feat, ast.BinOp):
        if isinstance(feat.op, ast.Add):
            node.func='Add('
        elif isinstance(feat.op, ast.Sub):
            node.func='Sub('
        elif isinstance(feat.op, ast.Mult):
            node.func='Mult('
        elif isinstance(feat.op, ast.MatMult):
            node.func='MatMult('
        elif isinstance(feat.op, ast.Div):
            node.func='Div('
        else:
            print("Unsupported operation: ", feat.op)
        #print(args)
        args=[feat.left, feat.right]
        addArgs(node, treedic, args)
    else:
        print("Unrecognized node: ", ast.dump(feat))
    
    return node

# populate args
def addArgs(somenode, treedic, args):
    for i in args:
        #if not isinstance(i, str):
        #    print(ast.dump(i))
        
        child=handleLangFeat(i,treedic)
        
        somenode.args.append(child)

# visit assignments
class GetAssignments(ast.NodeVisitor):
    def visit_Assign(self, node):
        global flag, root, spec_treedic, src_treedic, funcName
        #print(ast.dump(node.targets[0]))
        #print(ast.dump(node.value))

        tmpTup=[]

        if flag=="src":
            if isinstance(node.targets[0], ast.Tuple):
                for elem in node.targets[0]:
                    if elem.id in spec_treedic:
                        tmpTup.append(elem.id)
                tmpTup=tuple(tmpTup)
            elif node.targets[0].id not in spec_treedic: #one way nesting
                return
            treedic=src_treedic
        else:
            treedic=spec_treedic
        
        if isinstance(node.targets[0], ast.Tuple):
            root=handleLangFeat(node.value,treedic).ExpString()
            for (i,elem) in enumerate(tmpTup):
                
        else:
            root=handleLangFeat(node.value,treedic)
        
        lvalue=handleLangFeat(node.targets[0], treedic)
        if isinstance(lvalue, Node):
            lvalue=lvalue.ExpString()

        treedic[lvalue]=root

#execute
# parse the specification file and build the spec_treeDict 
spec_tree=ast.parse(spec,mode='exec')
flag='spec'
GetAssignments().visit(spec_tree)

#'''
for key in spec_treedic:
    rvalue=spec_treedic[key]
    if isinstance(rvalue,Node):
        rvalue=rvalue.ExpString()
    print(key,': ',rvalue)
#'''

for i in spec_vars_list:
    if i not in spec_treedic:
        print("Error: Variable ",i," specified for checking is not defined in the specification.")
        sys.exit(0)

# parse and build the src tree and its dicationary 
src_tree=ast.parse(src,mode='exec')
flag='src'
GetAssignments().visit(src_tree)

#print(src_treedic)
#print(src_treedic['c'].ExpString())
#print(src_treedic['c'].args[0].func)
#print(spec_vars_list)

#check for incompatibilities
for key in spec_vars_list:
    if key not in src_treedic:
        print("Warning: Variable ", key, " is not defined in the code.")
        continue
    if not spec_treedic[key].ExpString() == src_treedic[key].ExpString():
        print("Warning: Variable ", key, "does not match specification. Details: Specification: ",spec_treedic[key].ExpString(),". Code: ",src_treedic[key].ExpString(),".")
        continue
    print("Match: Variable ",key," matches specification. Details: ",spec_treedic[key].ExpString(),".")



