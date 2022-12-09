#!/bin/bash

dir_py=./testcases/

for fil in "$dir_py"*.py
  do
    #echo "Checking file: '$fil'"
    spec_file=${fil/py/spec}

    if test -f "$spec_file"; then 
        #echo " $spec_file exists"
        output=$(python nncp_v1.py $spec_file $fil)
        #echo "output of $fil: $output"
        
        out_file=${fil/py/out}
        if test -f "$out_file"; then 
            # compare output with the content of .out file
            #tmp=$()
            if cmp -s $output $(cat $out_file); then
                echo "$fil PASS"
            else
                echo -e "$fil FAILED\n>\n$output\n<\n$(cat $out_file)"
            fi

        #else
            #echo "file $fil does not have a .out file!!"
        fi
    #else
        #echo "file $fil does not have a .spec file!!"
    fi
  done


