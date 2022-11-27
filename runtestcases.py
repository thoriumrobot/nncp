import sys, os, subprocess, difflib
from colorama import Fore, Back, Style

for dirpath, dirname, filename in os.walk(str(sys.argv[1])):
    casePaths = [dirpath + '/' + f for f in filename if f.endswith(".py")]

#print(casePaths)

for (i, casePath) in enumerate(casePaths):
    d=difflib.Differ()
    specPath=casePath[:-2]+'spec'
    outPath=casePath[:-2]+'out'
    output=subprocess.check_output(['python', 'nncp_alpha.py', specPath, casePath]).decode().strip()
    print('Case ', i+1, " ", casePath, ":\n")
    with open(outPath, 'r', encoding='utf8') as f:
        out = f.read()
    if out==output:
        print(Fore.GREEN + "Pass\n",Style.RESET_ALL, output,"\n")
    else:
        diff=d.compare(output, out)
        print(Fore.RED+"Fail\n", Style.RESET_ALL,"".join(diff),"\n")