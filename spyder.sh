#!/bin/bash

let fsize=0 # log file size
let rflag=0 # ? run the command : don't run the command

for (( ; ; )) # infinite loop
do
    if [ -e "./done.txt" ]; then
      printf "Ending\n"
      break
    fi
    if [ "$rflag" -eq 0 ]; then
      nohup /usr/local/bin/python ./spyder.py >>gp.log 2>&1 &
      child=$! # make a note of the child pid
      rflag=1  # set to running
      printf "spawning %s\n" "$child" #debug
    fi
    sleep 60
    let tmp=`/usr/bin/du -k gp.log | cut -f1` # check the size of the file
    if [ "$fsize" -eq "$tmp" ]; then
      /bin/kill -9 $child
      printf "killing %s\n" "$child"
      let rflag=0
    else
      let fsize="$tmp" # else set to the current size
    fi
done
