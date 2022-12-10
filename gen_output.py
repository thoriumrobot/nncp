import os, subprocess, argparse

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dir", type=str, default='testcases/',
    help="test case directory")
args = vars(ap.parse_args())

for dirpath, dirname, filename in os.walk(args["dir"]):
    specPaths = [dirpath + f for f in filename if f.endswith(".spec")]

#print(casePaths)

for (i, specPath) in enumerate(specPaths):
    casePath=specPath[:-4]+'py'
    outPath=specPath[:-4]+'out'
    output=subprocess.check_output(['python', 'nncp_beta.py', '-s', specPath, '-p', casePath]).decode().strip()
    #print('Case ', i, " ", casePath, ":\n", output)
    with open(outPath, 'w') as f:
        f.write(output)