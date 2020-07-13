#!/bin/bash

if [ $# != 2 ]
then
    echo -e "usage:$0 [path to train_dir & d5.py] [first_time==1]"
    echo "$@"
    echo "$#"
    exit
fi

path=$1
first_time=$2
##Bring up the learner:
if [ $first_time -eq 1 ];
then
    /home/`whoami`/venv/bin/python $path/d5.py --job_name=learner --task=0 --base_path=$path &
elif [ $first_time -eq 4 ]
then
    /home/`whoami`/venv/bin/python $path/d5.py --job_name=learner --task=0 --base_path=$path --load --eval &
else
    /home/`whoami`/venv/bin/python $path/d5.py --job_name=learner --task=0 --base_path=$path --load &
fi
