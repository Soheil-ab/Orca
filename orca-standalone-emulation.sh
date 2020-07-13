if [ $# -eq 1 ]
then
    source setup.sh
    first_time=4
    port_base=$1

    max_steps=500000
    eval_duration=30
    num_actors=1
    epoch=20
    memory_size=$((max_steps*num_actors))

    scheme_="cubic"
    cur_dir=`pwd -P`
    dir="${cur_dir}/rl-module"

    sed "s/\"num_actors\"\: 1/\"num_actors\"\: $num_actors/" $cur_dir/params_base_eval.json > "${dir}/params.json"
    sed -i "s/\"memsize\"\: 2553600/\"memsize\"\: $memory_size/" "${dir}/params.json"
    sudo killall -s9 python client orca-server-mahimahi

    #Bring up the actor(s):
    act_id=0
    act_port=$port_base

    #Use a wired48 link for both down & up links (you just need to change the downlink side, if you need.)
    dl=48
    downl="wired$dl"
    upl="wired48"
    #one-way delay=10ms
    del=10
    bdp=$((2*dl*del/12))     #12Mbps=1pkt per 1 ms ==> BDP=2*del*BW=2*del*dl/12
    qs=$((2*bdp))

    # For the Step-scenraio, you can use follwoing parameters:
    #downl="step-10s-3-level"
    #qs=1000
    #eval_duration=60

    ./actor.sh ${act_port} $epoch ${first_time} $scheme_ $dir $act_id $downl $upl $del $eval_duration $qs 0 &
    pids="$pids $!"

    #in case you need more actors: increase number actor's id and port. and run actor.sh again ...
    #act_id=$((act_id+1))
    #act_port=$((port_base+act_id))
    #sleep 2

    #Wait for them ...
    for pid in $pids
    do
        echo "waiting for $pid"
        wait $pid
    done
    #Make sure that learner and actors are down ...
    for i in `seq 0 $((num_actors))`
    do
        sudo killall -s15 python
        sudo killall -s15 orca-server-mahimahi
        sudo killall -s15 client
    done
else
    echo "usage: $0 [base port number]"
fi

