from mpi4py import MPI

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import imageio
import os
import sys
import tqdm
import time
import argparse

# mpi reset
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

resolution = 1

def make_frame_image(file_path, index, resolution, args):
    data = np.load(file_path, allow_pickle=True)

    fig = plt.figure(figsize=(16 * resolution, 9 * resolution))
    ax = plt.axes(projection='3d')
    ax.view_init(elev=args.elev, azim=args.elev)
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    ax.grid(False)
    ax.set_axis_off()
    ax.scatter3D(data[0][0, :], data[0][1, :], data[0][2, :], s=1, c='white')
    ax.scatter3D(data[1][0, :], data[1][1, :], data[1][2, :], s=1, c='gray')
    ax.set_title(f'Frame {index}')
    fig.canvas.draw()
    image = np.array(fig.canvas.buffer_rgba())
    image = np.array(Image.fromarray(image).resize((1920, 1080)))
    plt.close(fig)
    return index, image

if __name__ == '__main__':
    local_frames = []

    parser = argparse.ArgumentParser(description="Galaxy Collision Simulation")
    parser.add_argument("--load_dir", type=str, default="outputs", help="Load directory")
    parser.add_argument("--elev", type=float, default=0, help="elev angle")
    parser.add_argument("--azim", type=float, default=0, help="azim angle")
    parser.add_argument("--name", type=str, default="outputs_mov", help="fileName")

    args = parser.parse_args()

    if rank == 0 :
        frame_files = sorted([os.path.join(args.load_dir, f) for f in os.listdir(args.load_dir) if f.endswith('.npy')])
    else:
        frame_files = None

    # 파일 배분
    frame_files = comm.bcast(frame_files, root=0)
    local_files = frame_files[rank::size]

    start_time = time.time()

    for i, file_path in enumerate(tqdm.tqdm(local_files, desc=f"rank : {rank} ; Rendering frames")):
        global_index = frame_files.index(file_path) + 1
        frame = make_frame_image(file_path, global_index, resolution, args)
        local_frames.append(frame)

        if rank != 0 : 
            comm.send(frame, dest=0, tag=rank)
        else :
            for j in range(1, size) :
                received_frame = comm.recv(source=j, tag=j)
                local_frames.append(received_frame)

    if rank == 0 :
        # all_frames = [frame for sublist in all_frames for frame in sublist]
        all_frames = local_frames
        all_frames.sort(key=lambda x: x[0])

        image_frames = [frame[1] for frame in all_frames]

        # Create the video
        output_file = f'{args.name}_mov.mp4'
        writer = imageio.get_writer(output_file, fps=60, macro_block_size=None, format='MP4')

        for image in tqdm.tqdm(image_frames, desc="Making Movie"):
            writer.append_data(image)

        writer.close()
        print(f"The movie saved as {output_file}")

        end_time = time.time()
        print(f"\\(^_^)/ \\(^_^)/ Total time for making the movie: {end_time - start_time:.3f} seconds.")