import ast, tokenize, csv, sys
from copy import deepcopy

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
    
    def ExpString(self):
        if not isinstance(self.func, str):
            s=str(self.func)
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
        
        if self.func=='Project(' or self.func=='Add(' or self.func=='Sub(' or self.func=='Mult(' or self.func=='MatMult(':
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
        return elem.value
    elif isinstance(elem, ast.Name):
        if elem.id in treedic:
            return deepcopy(treedic[elem.id])
        else:
            return elem.id
    elif not hasattr(elem, '__dict__'):
        return elem
    else:
        #print("Cannot handle object: ", elem)
        return False

def SliceStr(slice, treedic):
    #print(ast.dump(slice))

    tmpstr='['

    tmpval = handleConstName(slice, treedic)
    if not tmpval==False:
        tmpstr+=tmpval+']'
        return tmpstr
    elif isinstance(slice, ast.Index):
        dims=slice.value.elts
    elif isinstance(slice, ast.Tuple):
        dims=slice.elts
    elif isinstance(slice, ast.ExtSlice):
        dims=slice.dims
    else:
        print("Slice is an unrecognized object: ", slice)
    
    #print(dims)

    for i in dims:
        if isinstance(i, ast.Slice):
            if i.lower is None:
                tmpstr+=':'
                if not i == dims[-1]:
                    tmpstr+=','
                continue
            
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
    if not tmpval==False:
        if not hasattr(tmpval, '__dict__'):
            node.func=tmpval
        else:
            node=tmpval
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
        packFunc(feat.func)
        node.func=funcName
        addArgs(node, treedic, feat.args)
    elif isinstance(feat, ast.Subscript):
        node.func='Project('
        node.args.append(feat.value.id)
        node.args.append(SliceStr(feat.slice, treedic))
    elif isinstance(feat, ast.BinOp):
        if isinstance(feat.op, ast.Add):
            node.func='Add('
        elif isinstance(feat.op, ast.Sub):
            node.func='Sub('
        elif isinstance(feat.op, ast.Mult):
            node.func='Mult('
        elif isinstance(feat.op, ast.MatMult):
            node.func='MatMult('
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
        if flag=="src":
            if node.targets[0].id not in spec_treedic: #one way nesting
                return
            treedic=src_treedic
        else:
            treedic=spec_treedic
        
        #print(ast.dump(node.value))
        if isinstance(node.targets[0], ast.Tuple):
            root=Node('List(',[])
            addArgs(root, treedic, node.targets[0].elts)
        else:
            root=handleLangFeat(node.value,treedic)
        
        treedic[node.targets[0].id]=root

#execute
# parse the specification file and build the spec_treeDict 
def nncp_check(spec, src):
    out=[]
    outflag=0

    spec_tree=ast.parse(spec,mode='exec')
    flag='spec'
    GetAssignments().visit(spec_tree)

    for i in spec_vars_list:
        if i not in spec_treedic:
            out.append("Error: Variable "+str(i)+" specified for checking is not defined in the specification.")
            out.insert(0, 1)
            return out

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
            out.append("Warning: Variable "+ key+ " is not defined in the code.")
            outflag=1
            continue
        if not spec_treedic[key].ExpString() == src_treedic[key].ExpString():
            out.append("Warning: Variable "+ key+ "does not match specification. Details: Specification: "+spec_treedic[key].ExpString()+". Code: "+src_treedic[key].ExpString()+".")
            outflag=1
            continue
        out.append("Match: Variable "+key+" matches specification. Details: "+spec_treedic[key].ExpString()+".")
    
    out.insert(0, outflag)
    return out


