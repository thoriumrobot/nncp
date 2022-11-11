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

# populate args
def addArgs(somenode, sometreedic, args):
    for i in args:
        if isinstance(i, ast.Constant):
            somenode.args.append(i.value)
            continue
        elif isinstance(i, ast.Name):
            if i.id in sometreedic:
                somenode.args.append(sometreedic[i.id])
            else:
                somenode.args.append(i.id)
            continue
        #print(ast.dump(i))
        nodeobj=Node(i.func.value.id+'.'+i.func.attr, [])
        addArgs(nodeobj, sometreedic, i.args)
        somenode.args.append(nodeobj)

# visit assignments
class GetAssignments(ast.NodeVisitor):
    def visit_Assign(self, node):
        global flag, root, spec_treedic, src_treedic
        if flag=="src":
            if node.targets[0].id not in spec_treedic:
                return
            treedic=src_treedic
        else:
            treedic=spec_treedic
        #print(ast.dump(node.value))
        root=Node('null',[])
        if isinstance(node.value, ast.Constant):
            root.func=node.value.value
            return
        elif isinstance(node.value, ast.Name):
            if node.value.id in treedic:
                root.args.append(treedic[node.value.id])
            else:
                root.args.append(node.value.id)
            return
        root.func=node.value.func.value.id+'.'+node.value.func.attr
        addArgs(root, treedic, node.value.args)

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


