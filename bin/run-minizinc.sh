#!/bin/bash

# Set environment variables
source set-path.sh

# Parse command line arguments
m=$1
m_no_extension=$(basename -s .mzn $m)
i=$2
s=$3
filename=$(basename "$i")
i_no_extension=${filename%.*}
time_limit=$4
energy_profiler=$5
cores=$6

# Run minizinc command
minizinc $m $i --solver $s --time-limit $time_limit --statistics -f -p $cores > mznc_results/$energy_profiler/$m_no_extension,$i_no_extension,$s.txt 2>&1
