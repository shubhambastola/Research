import os
import math
import numpy as np
import pandas as pd
import scipy.io
import matplotlib.pyplot as plt

# Step 1: Read CSV and extract x, y, z points
def read_csv(file_path):
    df = pd.read_csv(file_path)
    points = df.iloc[:, 7:10].to_numpy()  # Columns: X, Y, Z
    return points

# Step 2: Create empty 3D grid
def create_cubes(lcubes, xmin, xmax, ymin, ymax, zmin, zmax):
    x_bins = math.floor((xmax - xmin) / lcubes)
    y_bins = math.floor((ymax - ymin) / lcubes)
    z_bins = math.floor((zmax - zmin) / lcubes)
    return np.zeros((x_bins, y_bins, z_bins), dtype=object)

# Step 3: Put points into cubes
def classify_points(points, cubes, lcubes, xmin, ymin, zmin, xmax, ymax, zmax):
    for point in points:
        x, y, z = point
        if xmin < x < xmax and ymin < y < ymax and zmin < z < zmax:
            cb_x = math.floor((x - xmin) / lcubes)
            cb_y = math.floor((y - ymin) / lcubes)
            cb_z = math.floor((z - zmin) / lcubes)

            if not isinstance(cubes[cb_x][cb_y][cb_z], list):
                cubes[cb_x][cb_y][cb_z] = [point]
            else:
                cubes[cb_x][cb_y][cb_z].append(point)
    return cubes

# Step 4: Identify background cubes
def evaluate_density(cubes, threshold):
    background = []
    for cb_x in range(len(cubes)):
        for cb_y in range(len(cubes[0])):
            for cb_z in range(len(cubes[0][0])):
                cell = cubes[cb_x][cb_y][cb_z]
                if isinstance(cell, list) and len(cell) > threshold:
                    background.append([cb_x, cb_y, cb_z])
    return background

# Step 5: Filter background and foreground points
def filter_points(points, background, lcubes, xmin, ymin, zmin, xmax, ymax, zmax):
    foreground = []
    background_points = []
    for point in points:
        x, y, z = point
        if xmin < x < xmax and ymin < y < ymax and zmin < z < zmax:
            cb_x = math.floor((x - xmin) / lcubes)
            cb_y = math.floor((y - ymin) / lcubes)
            cb_z = math.floor((z - zmin) / lcubes)

            if [cb_x, cb_y, cb_z] in background:
                background_points.append(point)
            else:
                foreground.append(point)
    return foreground, background_points

# Step 6: Plot and save results
def plot_points(foreground, background, filename):
    foreground = np.array(foreground)
    background = np.array(background)

    plt.figure(figsize=(10, 6))
    if len(foreground) > 0:
        plt.scatter(foreground[:, 0], foreground[:, 1], c='green', s=1, label='Foreground')
    if len(background) > 0:
        plt.scatter(background[:, 0], background[:, 1], c='red', s=1, label='Background')

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("2D Background Filtering")
    plt.legend()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Main function
def main():
    print("✅ Script started...")

    # Set folder and parameters
    folder_path = '/Users/shubhambastola/Desktop/background_filtering/'
    lcubes = 0.5
    xmin, xmax = -100, 100
    ymin, ymax = -100, 100
    zmin, zmax = -5, 5
    threshold = 50
    max_frames = 2500

    # Create output folders
    os.makedirs("plots", exist_ok=True)
    os.makedirs("mat_files", exist_ok=True)

    # Get list of CSV files
    all_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.csv')])
    print(f" Total CSV files found: {len(all_files)}")

    # Process up to 2500 frames
    for i, filename in enumerate(all_files):
        if i >= max_frames:
            print("Reached 2500 frames. Stopping.")
            break

        file_path = os.path.join(folder_path, filename)
        print(f" Processing Frame {i}: {filename}")

        try:
            points = read_csv(file_path)
            cubes = create_cubes(lcubes, xmin, xmax, ymin, ymax, zmin, zmax)
            cubes = classify_points(points, cubes, lcubes, xmin, ymin, zmin, xmax, ymax, zmax)
            background = evaluate_density(cubes, threshold)
            fg, bg = filter_points(points, background, lcubes, xmin, ymin, zmin, xmax, ymax, zmax)

            # Save plot
            plot_file = f"plots/Frame{i}_result.png"
            plot_points(fg, bg, plot_file)

            # Save .mat
            mat_file = f"mat_files/Frame{i}_background.mat"
            scipy.io.savemat(mat_file, {'background': background})

        except Exception as e:
            print(f" Error in Frame {i}: {e}")
            continue

    print(" All frames processed successfully!")

# Run script
if __name__ == '__main__':
    main()


