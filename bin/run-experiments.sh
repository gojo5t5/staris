#!/bin/bash
time_limit=$((1000 * 60 * 20)) #20 minutes
# time_limit=$((1000)) #20 minutes
# solvers=(chuffed gecode jacop ortools picat)
solvers=(gecode ortools picat)
repeats=1
cores=4

if [ ! -d "mznc2022_probs" ]; then
    tar -xvf mznc2022_probs.tar
fi

mkdir -p mznc_results
# chmod u+rw mznc_results/
mkdir -p mznc_results/perf/
mkdir -p mznc_results/jouleit/
mkdir -p mznc_results/powertop/
# sudo chmod -R 775 mznc_results/perf/

# /Users/matteohe/Documents/staris/AutoIG/bin/run-experiments.sh
mkdir -p energy_data
mkdir -p energy_data/perf/
mkdir -p energy_data/jouleit/
mkdir -p energy_data/powertop/

chmod +x run-minizinc.sh
# sudo chmod -R 775 energy_data/perf/
# sudo chmod -R 775 energy_data/jouleit/

# allow perf to run without root
# sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
# sudo sysctl -w kernel.perf_event_paranoid=-1

# Start Powertop in calibration mode
# sudo powertop --calibrate

# start experiment
while read line; do
    echo "$line"
    path_to_model=$(echo $line | cut -d " " -f 1)
    path_to_instance=$(echo $line | cut -d " " -f 2)
    m=$(basename "$path_to_model")
    i=$(basename "$path_to_instance")
    extension=${m##*.}
    i_filename=${i%.*}

    if [ "$extension" = "mzn" ]; then

        for s in "${solvers[@]}"; do

            results_file_name=$(basename -s .mzn $m),$i_filename,$s
            echo "results file name is: $results_file_name"

            printf "\n:: Running minizinc on model $m, instance $i, and using solver $s, for 20 minutes.\n"

            printf "\n\n-----Measuring with perf-----\n\n"
            energy_profiler="perf"

            cat ../../password.txt | \
            sudo -S perf stat \
            -e power/energy-cores/,power/energy-ram/,power/energy-gpu/,power/energy-pkg/ \
            ./run-minizinc.sh $path_to_model $path_to_instance $s $time_limit $energy_profiler $cores \
            > energy_data/$energy_profiler/$results_file_name.txt 2>&1

            printf "\n-----Measuring with jouleit----\n\n"
            energy_profiler="jouleit"

            cat ../../password.txt | \
            sudo -S ./jouleit.sh -b \
            ./run-minizinc.sh $path_to_model $path_to_instance $s $time_limit $energy_profiler $cores \
            > energy_data/$energy_profiler/$results_file_name.txt 

            # printf "\n-----Measuring with powertop----\n\n"
            # energy_profiler="powertop"

            # ./run-minizinc.sh $path_to_model $path_to_instance $s $time_limit $energy_profiler $cores &
            # program_pid=$!

            # # Wait until the program has fully initialized
            # while kill -0 $program_pid >/dev/null 2>&1; do
            #     sleep 1
            # done

            # Start powertop and wait for the program to finish
            # cat ../../password.txt | \
            # sudo -S powertop --csv=energy_data/$energy_profiler/nfc,12_2_11,gecode.csv &
            # powertop_pid=$!

            # wait $program_pid
            # kill $powertop_pid

        done
    fi

done < instances-set2.txt

# for model in ./mznc2022_probs/*; do
#     printf "\n model: $model"

#     for m in $model/*.mzn; do
#         printf "\n mzn file: $m"

#         for i in "$model"/*.{dzn,json}; do
#             if [ -e $i ]; then
#                 printf "\n instance: $i"
#                 filename=$(basename "$i")
#                 i_no_extension=${filename%.*}
#                 # echo $i_no_extension

#                 for s in "${solvers[@]}"; do
#                     printf "\n:: Running minizinc on model $m, instance $i, and using solver $s, for 20 minutes.\n"

#                     printf "\n\n-----Measuring with perf-----\n\n"
#                     energy_profiler="perf"
#                     cat ../../password.txt | sudo -S perf stat -e power/energy-cores/,power/energy-ram/,power/energy-gpu/,power/energy-pkg/ bash -c "source set-path.sh; minizinc $m $i --solver $s --time-limit $time_limit -s > mznc_results/$energy_profiler/$results_file_name.txt" > energy_data/$energy_profiler/$results_file_name.txt 2>&1

#                     printf "\n-----Measuring with jouleit----\n\n"
#                     energy_profiler="jouleit"
#                     cat ../../password.txt | sudo -S ./jouleit.sh -n $repeats -c 

#                     printf "\n-----Measuring with powertop----\n\n"

#                     energy_profiler="powertop"
#                     ./run-minizinc.sh $m $i $s $time_limit $energy_profiler $cores &
#                     program_pid=$!

#                     # Wait until the program has fully initialized
#                     while kill -0 $program_pid >/dev/null 2>&1; do
#                         sleep 1
#                     done

#                     # Start powertop and wait for the program to finish
#                     cat ../../password.txt | sudo -S powertop --csv=energy_data/$energy_profiler/$(basename -s .mzn $m),$i_no_extension,$s.csv --time=$((time_limit / 1000)) &
#                     powertop_pid=$!

#                     wait $program_pid
#                     wait $powertop_pid

#                     energy_profiler="powertop"
#                     ./run-minizinc.sh $m $i $s $time_limit $energy_profiler & cat ../../password.txt | sudo -S powertop --csv=energy_data/$energy_profiler/$(basename -s .mzn $m),$i_no_extension,$s.csv --time= $time_limit & wait

#                 done
#             fi
#         done
#     done
# done

# scp -r mh354@hawthorn.cs.st-andrews.ac.uk:AutoIG/bin/UNSAT_energy_consumption.png /Users/matteohe/Desktop/
# scp -r /Users/matteohe/Documents/staris/AutoIG/bin/plot_graphs.py mh354@hawthorn.cs.st-andrews.ac.uk:AutoIG/bin/
