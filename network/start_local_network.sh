(trap "kill 0" SIGINT;
 for ((j=0;j<$((2*${1})); j++))
 do
     IP=$((j + 50000)) 
     python3 node.py -a "localhost:${IP}" -i ${j} &
 done
 wait
)



