import matplotlib.pyplot as plt
import numpy as np
import os
import re
import csv


results = {
    "UNSAT": {},
    "SOLVED": {},
    "ERR": {}
}

energy_folder_path = "./energy_data/perf/"
mznc_folder_path = "./mznc_results/perf/"
csv_path = "./perf_results.csv"


def add_to_dict(category, model, instance, solver):
    if category in results:
        if model in results[category]:
            if instance in results[category][model]:
                results[category][model][instance].append(solver)
            else:
                # Create the 'instance' key and add the data
                results[category][model][instance] = [solver]
        else:
            # Create the 'model' key and add the data
            results[category][model] = {instance: [solver]}
    else:
        # Create the 'ERR' key and add the data
        results[category] = {model: {instance: [solver]}}

def process_files(folder_path, csv_writer):
    count = 0
    processed_files = 0
    for filename in os.listdir(folder_path):
        count += 1
        fullpath = os.path.join(folder_path, filename)
        args = filename.split(',')
        # print(args)
        model = args[0]
        instance = args[1]
        solver = args[2][:-4]

        if os.path.isfile(fullpath):
            # Do something with the file
            with open(fullpath, 'r') as f:
                output = f.read()
                processed_files += 1
                print("Processed files: " + str(processed_files) + "/" + str(count))
                if '==========' in output:
                    # The problem completed
                    add_to_dict('SOLVED', model, instance, solver)

                    # Get energy and runtime data and write to CSV
                    energy, runtime = get_data(model, instance, solver, energy_folder_path)
                    csv_writer.writerow([model, instance, solver, "", "SOLVED", runtime, energy])

                elif '=====UNSATISFIABLE=====' in output:
                    # The problem is unsatisfiable
                    add_to_dict('UNSAT', model, instance, solver)

                    energy, runtime = get_data(model, instance, solver, energy_folder_path)
                    csv_writer.writerow([model, instance, solver, "", "UNSAT", runtime, energy])

                elif "=====ERROR=====" in output or "=====UNKNOWN=====" in output:  # minizinc had an ERROR
                    add_to_dict('ERR', model, instance, solver)

                    energy, runtime = get_data(model, instance, solver, energy_folder_path)
                    csv_writer.writerow([model, instance, solver, "", "ERR", runtime, energy])
                

        elif os.path.isdir(fullpath):
            # Recursively process the subdirectory
            process_files(fullpath, csv_writer)

def get_data(model, instance, solver, path):
    joules_pattern = r'([\d\.]+) Joules power/energy-'
    file_path = model + ',' + instance + "," + solver + ".txt"
    # Get the energy consumption data and elapsed time for the given model, instance, and solver
    join_path = os.path.join(path, file_path)
    with open(join_path, 'r') as f:
        content = f.read()
        joules_values = re.findall(joules_pattern, content)
        match = re.search(r'\d+\.\d+ \+\-', content)
        if match:
            elapsed_time_str = match.group(0).split('+-')[0]
            elapsed_time = float(elapsed_time_str)
        else:
            elapsed_time = 0
    return sum(map(float, joules_values)), elapsed_time

def main():
    with open(csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["model", "instance", "solver", "seed", "run_status", "run_time", "energy"])
        process_files(mznc_folder_path, csv_writer)

if __name__ == "__main__":
    main()