if [ $# -eq 2 ]
then
    source setup.sh

    first_time=$1
    port_base=$2
    cur_dir=`pwd -P`
    scheme_="cubic"
    max_steps=500000         #Run untill you collect 50k samples per actor
    eval_duration=30
    num_actors=1
    memory_size=$((max_steps*num_actors))
    dir="${cur_dir}/rl-module"

    sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"
    sed -i "s/\"memsize\"\: 5320000/\"memsize\"\: $memory_size/" "${dir}/params.json"
    sudo killall -s9 python client orca-server-mahimahi

    epoch=20
    act_port=$port_base

    if [ $1 -eq 4 ]
    then
       # If you are here: You are going to perform an evaluation over an emulated link
       num_actors=1
       sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base.json > "${dir}/params.json"

       echo "./learner.sh  $dir $first_time  &"
       ./learner.sh  $dir ${first_time} &
       #Bring up the actors:
       act_id=0
       for dl in 48
       do
           downl="wired$dl"
           upl="wired48"
           for del in 10
           do
               bdp=$((2*dl*del/12))     #12Mbps=1pkt per 1 ms ==> BDP=2*del*BW=2*del*dl/12
               for qs in $((2*bdp))
               do
                   ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 &
                   pids="$pids $!"
                   act_id=$((act_id+1))
                   act_port=$((port_base+act_id))
                   sleep 2
               done
           done
       done
        for pid in $pids
        do
            echo "waiting for $pid"
            wait $pid
        done
        #Bring down the learner and actors ...
        for i in `seq 0 $((num_actors))`
        do
            sudo killall -s15 python
            sudo killall -s15 orca-server-mahimahi
            sudo killall -s15 client
        done
    else
    # If you are here: You are going to start/continue learning a better model!

      #Bring up the learner:
      echo "./learner.sh  $dir $first_time &"
      if [ $1 -eq 1 ];
      then
          # Start the learning from the scratch
           /home/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} &
           lpid=$!
       else
          # Continue the learning on top of previous model
           /home/`logname`/venv/bin/python ${dir}/d5.py --job_name=learner --task=0 --base_path=${dir} --load &
           lpid=$!
       fi
       sleep 10

       #Bring up the actors:
       # Here, we go with single actor
       act_id=0
       for dl in 48
       do
           downl="wired$dl"
           upl=$downl
           for del in 10
           do
               bdp=$((2*dl*del/12))      #12Mbps=1pkt per 1 ms ==> BDP=2*del*BW=2*del*dl/12
               for qs in $((2*bdp))
               do
                   ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del 0 $qs $max_steps
                   pids="$pids $!"
                   act_id=$((act_id+1))
                   act_port=$((port_base+act_id))
                   sleep 2
               done
           done
       done

       for pid in $pids
       do
           echo "waiting for $pid"
           wait $pid
       done

       #Kill the learner
       sudo kill -s15 $lpid

       #Wait if it needs to save somthing!
       sleep 30

       #Make sure all are down ...
        for i in `seq 0 $((num_actors))`
       do
           sudo killall -s15 python
           sudo killall -s15 orca-server-mahimahi
       done
    fi
else
    echo "usage: $0 [{Learning from scratch=1} {Continue your learning=0} {Just Do Evaluation=4}] [base port number ]"
fi

