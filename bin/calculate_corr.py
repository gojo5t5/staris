import pandas as pd
import numpy as np
import os 

def process_files(csvs_folder_path, dfs):
    for filename in os.listdir(csvs_folder_path):
        fullpath = os.path.join(csvs_folder_path, filename)
        if os.path.isfile(fullpath) and filename.endswith('.csv'):
            if "perf" in fullpath:
                continue
            print("Processing file: " + fullpath)
            df = pd.read_csv(fullpath)
            print(df.describe())
            dfs.append(df)
        elif os.path.isdir(fullpath):
            # Recursively process the subdirectory
            process_files(fullpath, dfs)

# between solvers
# between cores
# between energy tools

def main():
    dfs = []
    process_files('../experiment_data/', dfs)

    # Concatenate dataframes
    df = pd.concat(dfs)

    # Clean data
    print(df.isna().sum())
    print(df.describe())

    # group by solvers
    grouped = df.groupby('solver')

    # Create dictionary of dataframes
    dfs = {}
    for solver, group in grouped:
        print("correlation for solver: " + solver)
        # Calculate correlation coefficient
        corr = np.corrcoef(group['run_time'], group['energy'])
        print(corr)

if __name__ == '__main__':
    main()