import os
import math
import numpy as np
import pandas as pd
import scipy.io
import matplotlib.pyplot as plt

# Step 1: Read CSV and extract x, y, z points
def read_csv(file_path):
    df = pd.read_csv(file_path)
    points = df.iloc[:, 7:10].to_numpy()  # x, y, z assumed in columns 7, 8, 9
    return points

# Step 2: Create empty 3D grid for cubes
def create_cubes(lcubes, xmin, xmax, ymin, ymax, zmin, zmax):
    x_bins = math.floor((xmax - xmin) / lcubes)
    y_bins = math.floor((ymax - ymin) / lcubes)
    z_bins = math.floor((zmax - zmin) / lcubes)
    return np.zeros((x_bins, y_bins, z_bins), dtype=object)

# Step 3: Classify points into the corresponding cubes
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

# Step 4: Identify high-density background cubes
def evaluate_density(cubes, threshold):
    background = []
    for cb_x in range(len(cubes)):
        for cb_y in range(len(cubes[0])):
            for cb_z in range(len(cubes[0][0])):
                cell = cubes[cb_x][cb_y][cb_z]
                if isinstance(cell, list) and len(cell) > threshold:
                    background.append([cb_x, cb_y, cb_z])
    scipy.io.savemat('background_filtering.mat', {'background': background})
    return background

# Step 5: Filter out background points
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

# Step 6: Plot the filtered and background points in 2D
def plot_points(foreground, background):
    foreground = np.array(foreground)
    background = np.array(background)

    plt.figure(figsize=(10, 6))  # Optional: better size

    if len(foreground) > 0:
        plt.scatter(foreground[:, 0], foreground[:, 1], c='green', label='Foreground', s=1)
    if len(background) > 0:
        plt.scatter(background[:, 0], background[:, 1], c='red', label='Background', s=1)

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("2D Point Cloud: Background Filtering")
    plt.legend()
    plt.tight_layout()


    plt.savefig("Frame0_result.png")  # You can name it anything


    plt.show()

# def plot_points(foreground, background):
#     foreground = np.array(foreground)
#     background = np.array(background)
#
#     if len(foreground) > 0:
#         plt.scatter(foreground[:, 0], foreground[:, 1], c='green', label='Foreground', s=1)
#     if len(background) > 0:
#         plt.scatter(background[:, 0], background[:, 1], c='red', label='Background', s=1)
#
#     plt.xlabel("X")
#     plt.ylabel("Y")
#     plt.title("2D Point Cloud: Background Filtering")
#     plt.legend()
#     plt.tight_layout()
#     plt.show()

# Main
def main():
    file_path = '/Users/shubhambastola/Desktop/Research /Pedestrian/PEDESTRIAN (Frame 0).csv'

    # Parameters
    lcubes = 0.5
    xmin, xmax = -100, 100
    ymin, ymax = -100, 100
    zmin, zmax = -5, 5
    threshold = 50

    # Step-by-step pipeline
    points = read_csv(file_path)
    cubes = create_cubes(lcubes, xmin, xmax, ymin, ymax, zmin, zmax)
    cubes = classify_points(points, cubes, lcubes, xmin, ymin, zmin, xmax, ymax, zmax)
    background = evaluate_density(cubes, threshold)
    filtered_points, background_points = filter_points(points, background, lcubes, xmin, ymin, zmin, xmax, ymax, zmax)
    plot_points(filtered_points, background_points)

# Run the script
if __name__ == '__main__':
    main()
# os.listdir(path) " create the for loop and show the frames from the folder.