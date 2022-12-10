import os, subprocess, argparse
from colorama import Fore, Style

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dir", type=str, default='testcases/',
    help="test case directory (default: testcases/)")
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

for dirpath, dirname, filename in os.walk(args["dir"]):
    outPaths = [dirpath + f for f in filename if f.endswith(".out")]

outPaths.sort()

for (i, outPath) in enumerate(outPaths):
    specPath=outPath[:-3]+'spec'
    casePath=outPath[:-3]+'py'
    output=subprocess.check_output(['python', 'nncp_beta.py', '-s', specPath, '-p', casePath]).decode().strip().split('\n')
    print('Case ', i+1, " ", casePath, ":")
    with open(outPath, 'r', encoding='utf8') as f:
        out = f.readlines()
    for line in out:
        if not line.strip() in output:
            colorprint("Mismatch: ", 'red')
            print(line, end='')
        else:
            colorprint("Pass: ", 'green')
            print(line, end='')
    print('\n')