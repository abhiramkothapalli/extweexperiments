
(trap "kill 0" SIGINT;
 for i in 0 1
 do
     for ((j=0;j<$1; j++))
     do
	 python3 node.py $i $j localhost localhost 9090 &
     done
 done
 wait
)



