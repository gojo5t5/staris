import json
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import os
import re


results = {
    # satisfaction problems
    "UNSAT": {},
    # optimization problems
    "SOLVED": {},
    "ERR": {}
}

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

def process_files(folder_path):

    for filename in os.listdir(folder_path):
        fullpath = os.path.join(folder_path, filename)
        args = filename.split(',')
        # print(args)
        model = args[0]
        instance = args[1]
        solver = args[2]

        if os.path.isfile(fullpath):
            # Do something with the file
            with open(fullpath, 'r') as f:
                output = f.read()
                if '==========' in output:
                    # The problem completed
                    add_to_dict('SOLVED', model, instance, solver)

                elif '=====UNSATISFIABLE=====' in output:
                    # The problem is unsatisfiable
                    add_to_dict('UNSAT', model, instance, solver)

                elif "=====ERROR=====" in output:
                    add_to_dict('ERR', model, instance, solver)
                elif "=====UNKNOWN=====" in output:  # minizinc had an ERROR
                    add_to_dict('UNK', model, instance, solver)

        elif os.path.isdir(fullpath):
            # Recursively process the subdirectory
            process_files(fullpath)

def get_data(model, instance, solver, path):
    joules_pattern = r'([\d\.]+) Joules power/energy-'
    # Get the energy consumption data and elapsed time for the given model, instance, and solver
    join_path = os.path.join(path, "perf", model + ',' + instance + "," + solver)
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
    energy_folder_path = "./energy_data/"
    mznc_folder_path = "./mznc_results/perf/"
    process_files(mznc_folder_path)
    
    with open("sample.json", "w") as outfile:
        json.dump(dictionary, outfile)

    for category, v in results.items():
        instances = []
        time_taken = []
        energy_consumption = []
        instance_mapping = {} # create a mapping of instances to numerical values

        # iterate through the results and collect data
        for model, u in v.items():
            for instance, w in u.items():
                if instance not in instance_mapping:
                    instance_mapping[instance] = len(instance_mapping) # assign a numerical value to the instance
                for solver in w:
                    instances.append(instance)
                    energy, time = get_data(model, instance, solver, energy_folder_path)
                    energy_consumption.append(energy)
                    time_taken.append(time)

        # Create 3D scatterplot
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        z = [instance_mapping[i] for i in instances]
        ax.scatter(time_taken, energy_consumption, z, cmap='hsv', c=energy_consumption)
        ax.set_zlabel('Instances')
        ax.set_zticks(list(instance_mapping.values()))
        ax.set_zticklabels(list(instance_mapping.keys()))
        ax.set_ylabel("Energy Consumption")
        ax.set_xlabel("Elapsed Time")
        name = category + "_energy_consumption_graph"
        subprocess.call(['mkdir', name])
        # Rotate the graph
        for angle in range(0, 360):
            ax.view_init(30, angle)
            plt.savefig(name + "/file%03d.png" % angle)

        # subprocess.call([
        #     'ffmpeg', '-framerate', '8', '-i', 'file%03d.png', '-r', '30', '-pix_fmt', 'yuv420p',
        #     name + '.mp4'
        # ])
        # for file_name in glob.glob("*.png"):
        #     os.remove(file_name)
if __name__ == "__main__":
    main()  
