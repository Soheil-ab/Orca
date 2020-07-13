#!/bin/bash
if [ $# != 12 ]
then
    echo -e "usage:$0 port period first_time [underlying scheme:cubic , vegas , westwood , illinois , bbr, yeah , veno, scal , htcp , cdg , hybla ,... ] [path to ddpg.py] [actor id] [downlink] [uplink] [one-way link delay] [time time] [Qsize] [Max iterations per run]"
    exit
fi

port=$1
period=$2
first_time=$3
x=100
scheme=$4
path=$5
id=$6
down=$7
up=$8
latency=$9
finish_time=${10}
qsize=${11}
max_it=${12}

echo "Running orca-$scheme: $down"

trace=""
scheme_des="orca-$scheme-$latency-$period-$qsize"
log="orca-$scheme-$down-$up-$latency-${period}-$qsize"

#Bring up the actor i:
echo "will be done in $finish_time seconds ..."
echo "$path/orca-server-mahimahi $port $path ${period} ${first_time} $scheme $id $down $up $latency $log $finish_time $qsize $max_it"

$path/orca-server-mahimahi $port $path ${period} ${first_time} $scheme $id $down $up $latency $log $finish_time $qsize $max_it

#sudo killall -s15 python
#sleep 10
echo "Finished."
if [ ${first_time} -eq 2 ] || [ ${first_time} -eq 4 ]
then
    echo "Doing Some Analysis ..."
    out="sum-${log}.tr"
    echo $log >> $path/log/$out
    $path/mm-thr 500 $path/log/down-${log} 1>tmp 2>res_tmp
    cat res_tmp >>$path/log/$out
    echo "------------------------------" >> $path/log/$out
    rm *tmp
fi
echo "Done"

