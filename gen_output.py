import sys, os, subprocess

for dirpath, dirname, filename in os.walk(str(sys.argv[1])):
    casePaths = [dirpath + '/' + f for f in filename if f.endswith(".py")]

#print(casePaths)

for (i, casePath) in enumerate(casePaths):
    specPath=casePath[:-2]+'spec'
    outPath=casePath[:-2]+'out'
    output=subprocess.check_output(['python', 'nncp_alpha.py', specPath, casePath]).decode().strip()
    #print('Case ', i, " ", casePath, ":\n", output)
    with open(outPath, 'w') as f:
        f.write(output)