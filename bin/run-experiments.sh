#!/bin/bash
repeats=3
time_limit=$((1000)) #20 minutes
# time_limit=$((1000)) #20 minutes


if [ ! -d "mznc2022_probs" ]; then
    tar -xvf mznc2022_probs.tar
fi

solvers=(ortools yuck picat)

mkdir -p mznc_results
chmod u+rw mznc_results/
mkdir -p mznc_results/perf/
sudo chmod -R 775 mznc_results/perf/

/Users/matteohe/Documents/staris/AutoIG/bin/run-experiments.sh
mkdir -p energy_data
chmod u+rw energy_data/
mkdir -p energy_data/perf/
sudo chmod -R 775 energy_data/perf/

# allow perf to run without root
# sudo sh -c 'echo -1 >/proc/sys/kernel/perf_event_paranoid'
# sudo sysctl -w kernel.perf_event_paranoid=-1

# start experiment
for model in ./mznc2022_probs/*; do
    printf "\n model: $model"

    for m in $model/*.mzn; do
        printf "\n mzn file: $m"

        for i in "$model"/*.{dzn,json}; do
            if [ -e $i ]; then
                printf "\n instance: $i"
                filename=$(basename "$i")
                i_no_extension=${filename%.*}
                # echo $i_no_extension

                for s in "${solvers[@]}"; do
                    printf "\n:: Running minizinc on model $m, instance $i, and using solver $s, for 20 minutes.\n"

                    # printf "\n\n-----Measuring with perf-----\n\n"

                    # cat ../../password.txt | sudo -S perf stat -r $repeats -e power/energy-cores/,power/energy-ram/,power/energy-gpu/,power/energy-pkg/ bash -c "source set-path.sh; minizinc $m $i --solver $s --time-limit $time_limit -s > mznc_results/perf/$(basename -s .mzn $m),$i_no_extension,$s.txt" > energy_data/perf/$(basename -s .mzn $m),$i_no_extension,$s.txt 2>&1

                    # printf "\n\n-Printing results for minizinc from the perf command----\n\n"
                    # cat mznc_results/perf/$(basename -s .mzn $m)-$i_no_extension-$s.txt
                    # printf "\n\n-Printing results of energy data gathered from the perf command----\n\n"
                    # cat energy_data/perf/$(basename -s .mzn $m)-$i_no_extension-$s.txt


                    printf "\n-----Measuring with jouleit----\n\n"

                    cat ../../password.txt | sudo ./jouleit.sh -n $repeats -b -o energy_data/jouleit/$(basename -s .mzn $m)-$i_no_extension-$s.txt bash -c "source ./set-path.sh; minizinc $m $i --solver $s --time-limit $time_limit -s > mznc_results/jouleit/$(basename -s .mzn $m)-$i_no_extension-$s.txt"

                    # cat mznc_results/jouleit/$(basename -s .mzn $m)-$i_no_extension-$s.txt
                    # cat energy_data/jouleit/$(basename -s .mzn $m)-$i_no_extension-$s.txt

                    # echo "-----Measuring with powertop-----"
                    # echo "sudo powertop --csv=reports/$(basename -s .mzn $m)-$i_no_extension-$s.data -t 60 & minizinc $m $i --solver $s -t $((1000 * 60 * 1)) \n\n"

                    # sudo powertop --csv=results/powertop/$(basename -s .mzn $m)-$i_no_extension-$s.data -t $time_limit & $minizinc $m $i --solver $s -t $time_limit
                    
                    # PID=$(pgrep powertop) # Get the PID of the Powertop process
                    # sudo kill -2 $PID # Send a SIGINT signal to the Powertop process
                done
            fi
        done
    done
done

# scp -r mh354@hawthorn.cs.st-andrews.ac.uk:AutoIG/bin/UNSAT_energy_consumption.png /Users/matteohe/Desktop/
# scp -r /Users/matteohe/Documents/staris/AutoIG/bin/plot_graphs.py mh354@hawthorn.cs.st-andrews.ac.uk:AutoIG/bin/
