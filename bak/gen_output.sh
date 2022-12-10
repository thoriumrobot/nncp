#!/bin/bash

dir_py=./testcases/

for fil in "$dir_py"*.py
  do
  spec_file=${fil/py/spec}

    if test -f "$spec_file"; then 
        out_file=${fil/py/out}
        echo "$out_file"
        python nncp_beta.py $spec_file $fil >$out_file
    fi
done
