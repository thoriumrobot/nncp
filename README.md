# Static Analysis of Neural Network Calculation in PyTorch (NNCP)

This is a tool to verify a subsequence of operations in Python code. To pass, the code must satisfy a
specification written by the user. The tool checks whether the code performs the specified operations in the same order. This tool is intended for use in verifying machine learning projects. As a case study, we evaluate this tool by using it to debug changes in the Yolov5 object detection model.

[![Python application](https://github.com/thoriumrobot/nncp/actions/workflows/python-app.yml/badge.svg?branch=beta)](https://github.com/thoriumrobot/nncp/actions/workflows/python-app.yml)

## Getting Started

Instructions for installing and setting up your project, including any necessary dependencies.


### Usage

`$ python nncp_beta.py -s specfile.spec -p codefile.py`

### Basic example 

`$ python nncp_beta.py -s testcases/example_1.spec -p testcases/example_1.py`

usage: nncp_beta.py [-h] -s SPEC -p PROG [-c COL]

optional arguments:
  -h, --help            show this help message and exit
  -s SPEC, --spec SPEC  spec file
  -p PROG, --prog PROG  code file
  -c COL, --col COL     color true/false

### How to run the code (using a single testcase)
To successfully run the analysis, the following files are required:
1. `nncp_beta.py`: python file of the static analysis tool. `nncp_beta.py` was developed using python `3.8.13`. 
2. `-s`/`--spec`: A specification file that contains which variables/assignment expression and expected order of operations on this variable. Refer to #How to Write a specificaton file section below for more information. 
3. `-p`/`--prog`: An input python file to be analyzed. No annotation required
4. (Optional) `-c`/`--col` `false`||`true`: enable colorful output. The default value is false. This requires `colorama` package to be installed. `colorama` can be installed using `pip install colorama`. We used the version `0.4.5`.

### Run Testcases
To run all the test cases with color output, run:

`\$ python runtestcases.py -c true`

First, run `python gen_output.py` to generate the output for each pair of .spec and .py files in testcases directory.
Second, run `python runtestcases.py` to examine all files in testcases directory. 

usage: runtestcases.py [-h] [-d DIR] [-c COL]

optional arguments:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  test case directory
  -c COL, --col COL  color true/false

#### Add custom file to the testcases directory
Once you have the input Python file ready, create the specification file, refer to #How to Write a specificaton file section below for more information.
Run `gen_output.py` to generated the output, this will generate the output of all python files in testcases directory. Warning: some files will be overwritten. 
Now, the custom file will be analyzed every time `runtestcases.py` executed.

## How to write a specification file 

Specification files consist of a comment and a piece of code. The comment `#check ...` enable checking which assignment expressions to be analyzed. For example `#check a`, the analysis checks the spec file and python file for all the occuracance of variable `a`. Variable `a` is used to map between both spec and input python file. To analyze variable `a` correctly, the analysis build up the tree from the code that exists in both input python file and spec file. The analysis compares these trees to check the order of operations are indeed valid. What in the spec file is a subsquent code of the input python file. 

### Steps:
1. Identify which assignment expressions (`e`) in the input python file (`test.py`) that needs to be analyzed
2. Create an empty (`test.spec`) file. 
3. Write in `test.spec`: (`#check e`)
4. Write in `test.spec`: all occurrances of `e` in the correct order.
5. Run `python nncp_beta.py test.spec test.py`.

