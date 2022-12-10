import ast, tokenize, sys, argparse

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--spec", required=True, type=str,
    help="spec file")
ap.add_argument("-p", "--prog", required=True, type=str,
    help="code file")
ap.add_argument("-c", "--col", type=str, default='false',
    help="color true/false (default: false)")
args = vars(ap.parse_args())

colorflag=False

if args['col']=='true':
    colorflag=True
    from colorama import Fore, Style, init
    init()

def colorprint(text, color):
    if colorflag:
        if color=='red':
            print(Fore.RED+text,Style.RESET_ALL, end='')
        elif color=='green':
            print(Fore.GREEN+text,Style.RESET_ALL, end='')
        elif color=='yellow':
            print(Fore.YELLOW+text,Style.RESET_ALL, end='')
    else:
        print(text, end='')

# read specifiction 
with open(args['spec'], 'r', encoding='utf8') as f: 
    spec = f.read()

# read code from file 
with open(args['prog'], 'r', encoding='utf8') as f: 
    src = f.read()

def CSList(args):
    s=''
    for i in args:
        s+=val2str(i)
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
        elif self.func=='Key(':
            return self.args[0]+'='+self.args[1].ExpString()
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
                s+=i.func+':'+val2str(i.args[0])
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
        elif self.func=='FloorDiv(':
            op='//'
        elif self.func=='Or(':
            op=' or '
        elif self.func=='And(':
            op=' and '
        elif self.func=='Lt(':
            op=' < '
        
        if self.func=='Project(':
            #print(self.func, ',', self.args)
            s=val2str(self.args[0])+op+val2str(self.args[1])
            return s

        if self.func=='Add(' or self.func=='Sub(' or self.func=='Mult(' or self.func=='MatMult(' or self.func=='Div(' or self.func=='FloorDiv(' or self.func=='Or(' or self.func=='And(' or self.func=='Lt(':
            #print(self.func, ',', self.args)
            s='('+val2str(self.args[0])+op+val2str(self.args[1])+')'
            return s

        s=self.func+'('+CSList(self.args)+')'
        return s

# Global 
# tmep vars
root=Node('null',[])
flag='spec'     # spec for running the getAssignment for specification 
                # src for source file 
funcName = ""   # 
lrflag='rvalue'

# Variables to check
spec_vars_list=set()

#create dictionary
spec_treedic={}
src_treedic={}

check_flag=False

# use the tokenize to annotation in the specification file 
# The target annotation is used to ma 
with tokenize.open(args['spec']) as f:
    token_src = tokenize.generate_tokens(f.readline)
    for token in token_src:
        #print(token)
        if token.type==60 and 'check' in token.string:
            tmpvars=token.string.split('check')[1].split(' ')
            del tmpvars[0]
            spec_vars_list|=set(tmpvars)
            check_flag=True

if(not check_flag):
    colorprint("Error:", 'red')
    print(" No check comment in specification.\n")

def val2str(elem):
    if isinstance(elem, Node):
        return elem.ExpString()
    return str(elem)

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
        tmpval=val2str(handleLangFeat(node, treedic))
        if funcName == "":
            funcName = tmpval
        else: 
            funcName = tmpval+"."+funcName
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
        addKeys(tmpNode,treedic,node.keywords)
        #print(tmpNode.traverse())
        funcNode.args.append(tmpNode)
        return funcNode
    else:
        print("unknown instance {}".format(node))
        print("instance: {}".format(ast.dump(node)))

def handleConstName(elem, treedic):
    global lrflag
    #print(ast.dump(elem))
    if isinstance(elem, ast.Constant):
        if isinstance(elem.value,str):
            return '\''+elem.value+'\''
        return elem.value
    elif isinstance(elem, ast.Name):
        #if isinstance(elem.id, Node):
        #    print(elem.id.traverse())
        #print(treedic)
        if elem.id in treedic and lrflag == 'rvalue':
            return treedic[elem.id]
        else:
            return elem.id
    elif not hasattr(elem, '__dict__'):
        return elem
    else:
        #print("Cannot handle object: ", ast.dump(elem))
        return None

def SliceStr(slice, treedic):
    #print(ast.dump(slice))

    tmpstr='['

    tmpval = handleConstName(slice, treedic)
    if tmpval is not None:
        tmpstr+=val2str(tmpval)+']'
        return tmpstr
    elif isinstance(slice, ast.Index):
        #print(ast.dump(slice))
        if hasattr(slice.value, 'elts'):
            dims=slice.value.elts
        else:
            return '['+val2str(handleLangFeat(slice.value,treedic))+']'
    elif isinstance(slice, ast.Tuple):
        dims=slice.elts
    elif isinstance(slice, ast.ExtSlice):
        dims=slice.dims
    elif isinstance(slice, ast.Call):
        return val2str(handleLangFeat(slice,treedic))
    elif isinstance(slice, ast.Slice):
        dims=[slice]
    elif isinstance(slice, ast.Subscript):
        return '['+SliceStr(slice.slice, treedic)+']'
    else:
        print("Slice is an unrecognized object: ", ast.dump(slice))
    
    #print(dims)

    for i in dims:
        if isinstance(i, ast.Slice):
            tmpval=handleConstName(i.lower, treedic)
            if tmpval is not None:
                tmpstr+=val2str(tmpval)
            tmpstr+=':'
            tmpval=handleConstName(i.upper, treedic)
            if tmpval is not None:
                tmpstr+=val2str(tmpval)
            tmpval=handleConstName(i.step, treedic)
            if tmpval is not None:
                tmpstr+=':'+val2str(tmpval)
        elif isinstance(slice, ast.Index) or isinstance(i, ast.Name):
            #print(ast.dump(i))
            tmpstr+=val2str(handleConstName(i, treedic))
        elif isinstance(i, ast.Index):
            #print(ast.dump(i))
            tmpstr+=val2str(handleConstName(i.value, treedic))
        else:
            print("Element of slice is an unrecognized object: ", ast.dump(i))
        
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
        else:
            node.args.append(handleLangFeat(feat.value,treedic))
        
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
        elif isinstance(feat.op, ast.FloorDiv):
            node.func='FloorDiv('
        else:
            print("Unsupported operation: ", ast.dump(feat.op))
        #print(args)
        args=[feat.left, feat.right]
        addArgs(node, treedic, args)
    elif isinstance(feat, ast.BoolOp):
        if isinstance(feat.op, ast.Or):
            node.func='Or('
        elif isinstance(feat.op, ast.And):
            node.func='And('
        else:
            print("Unsupported operation: ", ast.dump(feat.op))
        #print(args)
        args=[feat.values[0], feat.values[1]]
        addArgs(node, treedic, args)
    elif isinstance(feat, ast.Compare):
        if isinstance(feat.ops[0], ast.Lt):
            node.func='Lt('
        else:
            print("Unsupported operation: ", ast.dump(feat.ops))
        args=[feat.left, feat.comparators[0]] # assume comparators list has one variable
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

# populate keywords
def addKeys(somenode, treedic, keys):
    for i in keys:
        #if not isinstance(i, str):
        #print(ast.dump(i))
        
        tmpnode=handleLangFeat(i.value,treedic)
        if isinstance(tmpnode, Node):
            child=Node('Key(',[i.arg, tmpnode])
        else:
            child=i.arg+'='+str(tmpnode)
        
        somenode.args.append(child)

# visit assignments
class GetAssignments(ast.NodeVisitor):
    def visit_Assign(self, node):
        global flag, root, spec_treedic, src_treedic, funcName, lrflag
        #print(ast.dump(node.targets[0]))
        #print(ast.dump(node.value))

        if isinstance(node.targets[0], ast.Tuple):
            lvalue=[]
        
        lrflag='lvalue'

        if flag=="src":
            treedic=src_treedic
            if isinstance(node.targets[0], ast.Tuple):
                #print(ast.dump(node.targets[0]))
                for elem in node.targets[0].elts:
                    tmpval=val2str(handleLangFeat(elem, treedic))
                    if tmpval in spec_treedic:
                        lvalue.append(tmpval)
                if len(lvalue)==0:
                    return
            else:
                lvalue=val2str(handleLangFeat(node.targets[0], treedic))
                if lvalue not in spec_treedic: #one way nesting
                    return
        else:
            treedic=spec_treedic
            lvalue=val2str(handleLangFeat(node.targets[0], treedic))
        
        lrflag='rvalue'
        
        if isinstance(node.targets[0], ast.Tuple):
            root=val2str(handleLangFeat(node.value,treedic))

            for (i,elem) in enumerate(lvalue):
                treedic[elem]=root+'['+str(i)+']'
        else:
            root=handleLangFeat(node.value,treedic)
            treedic[lvalue]=root

#execute
# parse the specification file and build the spec_treeDict 
spec_tree=ast.parse(spec,mode='exec')
flag='spec'
GetAssignments().visit(spec_tree)

'''
for key in spec_treedic:
    print(key,': ',val2str(spec_treedic[key]))
'''

for i in spec_vars_list:
    if i not in spec_treedic:
        colorprint("Error:", 'red')
        print(" Variable ",i," specified for checking is not defined in the specification.")
        print('The variables defined in the specification are:')
        for key in spec_treedic:
            print(key)
        sys.exit(0)

# parse and build the src tree and its dicationary 
src_tree=ast.parse(src,mode='exec')
flag='src'
GetAssignments().visit(src_tree)

#print(src_treedic)
#print(val2str(src_treedic['c']))
#print(src_treedic['c'].args[0].func)
#print(spec_vars_list)
#print(src_treedic['x'].traverse())

#check for incompatibilities
for key in spec_vars_list:
    if key not in src_treedic:
        colorprint("Warning:", 'yellow')
        print(" Variable ", key, " is not defined in the code.")
        continue
    if not val2str(spec_treedic[key]) == val2str(src_treedic[key]):
        colorprint("Warning:", 'yellow')
        print(" Variable ", key, "does not match specification. Details: Specification: ",val2str(spec_treedic[key]),". Code: ",val2str(src_treedic[key]),".")
        continue
    colorprint("Match:", 'green')
    print(" Variable ",key," matches specification. Details: ",val2str(spec_treedic[key]),".")



