import sys, os, subprocess, argparse
from colorama import Fore, Style

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dir", type=str, default='testcases/',
    help="test case directory")
args = vars(ap.parse_args())

for dirpath, dirname, filename in os.walk(args["dir"]):
    outPaths = [dirpath + '/' + f for f in filename if f.endswith(".out")]

#print(casePaths)

for (i, outPath) in enumerate(outPaths):
    specPath=outPath[:-3]+'spec'
    casePath=outPath[:-3]+'py'
    output=subprocess.check_output(['python', 'nncp_v1.py', specPath, casePath]).decode().strip().split('\n')
    print('\nCase ', i+1, " ", casePath, ":")
    with open(outPath, 'r', encoding='utf8') as f:
        out = f.readlines()
    for line in out:
        if not line.strip() in output:
            print(Fore.RED+"Mismatch: ", Style.RESET_ALL, line, end='')
        else:
            print(Fore.GREEN+"Pass: ", Style.RESET_ALL, line, end='')