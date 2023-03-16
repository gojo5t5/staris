import os
import glob
import random

fullpath_to_model = ""

def find_all_instances(directory, list_of_files=None):
    if list_of_files is None:
        list_of_files = []

    for filename in os.listdir(directory):
        fullpath = os.path.join(directory, filename)

        if os.path.isdir(fullpath):
            find_all_instances(fullpath, list_of_files)

        elif filename.endswith(".mzn"):
            fullpath_to_model = fullpath

            for instance_file in os.listdir(directory):
                fullpath_to_instance = os.path.join(directory, instance_file)

                if instance_file.endswith(".mzn"):
                    continue

                list_of_files.append([fullpath_to_model, fullpath_to_instance])
           
    return list_of_files

def main():
    files = find_all_instances("./mznc2022_probs/")
    random.shuffle(files)
    # open file in write mode
    with open("./instances.txt", 'a') as fp:
        for line in files:
            # write each item on a new line
            fp.write(line[0] + "\t")
            fp.write(line[1] + "\n")

        print('Done')

if __name__ == '__main__':
    main()