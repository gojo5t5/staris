import os
import re
import csv


results = {
    "UNSAT": {},
    "SOLVED": {},
    "ERR": {},
    "UNK": {}
}
ENERGY_PROFILERS = ["jouleit", "perf"]
ENERGY_DATA_PATH = "./energy_data/"
MZNC_RESULTS_PATH = "./mznc_results/"
CSV_PATH = "./csvs/"


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

def process_files(energy_folder_path, mznc_folder_path, csv_writer):
    count = 0
    processed_files = 0
    for filename in os.listdir(mznc_folder_path):
        count += 1
        fullpath = os.path.join(mznc_folder_path, filename)
        args = filename.split(',')
        # print(args)
        model = args[0]
        instance = args[1]
        solver = args[2][:-4]

        if os.path.isfile(fullpath):
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

                elif "=====ERROR=====" in output or "error" in output:
                    add_to_dict('ERR', model, instance, solver)

                    energy, runtime = get_data(model, instance, solver, energy_folder_path)
                    csv_writer.writerow([model, instance, solver, "", "ERR", runtime, energy])
                
                elif "=====UNKNOWN=====" in output:  # minizinc had an ERROR
                    add_to_dict('UNK', model, instance, solver)

                    energy, runtime = get_data(model, instance, solver, energy_folder_path)
                    csv_writer.writerow([model, instance, solver, "", "UNK", runtime, energy])

        elif os.path.isdir(fullpath):
            # Recursively process the subdirectory
            process_files(energy_folder_path, fullpath, csv_writer)

def parse_jouleit_file(string):
    parts = string.split(';')
    print("splitting: " + string, parts)
    result = {}
    for i in range(0, len(parts), 2):
        result[parts[i][:-1]] = int(parts[i+1])
    return result

def get_data(model, instance, solver, path):
    energy_profiler = os.path.basename(os.path.normpath(path))
    
    file_path = model + ',' + instance + "," + solver + ".txt"
    # Get the energy consumption data and elapsed time for the given model, instance, and solver
    join_path = os.path.join(path, file_path)
    with open(join_path, 'r') as f:
        if energy_profiler == "perf":
            joules_pattern = r'([\d\.]+) Joules power/energy-'
            content = f.read()
            joules_values = re.findall(joules_pattern, content)
            total_energy = sum(map(float, joules_values))

            match = re.search(r'\d+\.\d+ seconds', content)
            if match:
                elapsed_time_str = match.group(0).split(' ')[0]
                elapsed_time = float(elapsed_time_str)
            else:
                elapsed_time = 0
        elif energy_profiler == "jouleit":
            parsed_dict = parse_jouleit_file(f.read())
            print(parsed_dict)
            elapsed_time = parsed_dict['DURATION'] / 10**6
            
            joules_values = [parsed_dict['CORE'], parsed_dict['CPU'], parsed_dict['DRAM'], parsed_dict['UNCORE']]
            total_energy = sum(map(float, joules_values)) / 10**6

    return total_energy, elapsed_time

def main():

    for power_profiler in ENERGY_PROFILERS:
        energy_folder_path = ENERGY_DATA_PATH + power_profiler
        mznc_folder_path = MZNC_RESULTS_PATH + power_profiler
        csv_path = CSV_PATH + power_profiler + ".csv"
        with open(csv_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["model", "instance", "solver", "seed", "run_status", "run_time", "energy"])
            process_files(energy_folder_path, mznc_folder_path, csv_writer)

if __name__ == "__main__":
    main()