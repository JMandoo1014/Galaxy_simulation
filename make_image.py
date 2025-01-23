import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys
from PIL import Image
import os
import time

# python make_image.py --load_dir outputs --prefix snapshot --frame 1 --save_dir Images --resol 1
class Img:
    def __init__(self, args):
        self.args = args

        load_dir  = self.args.load_dir
        prefix    = self.args.prefix
        frame_num = str(self.args.frame).zfill(4)

        # Construct the file path based on the folder, file name, and snapshot number
        file_path = os.path.join(load_dir, f"{prefix}_t{frame_num}.npy")
        # Load the frame data from the given file
        self.frame_data = np.load(file_path, allow_pickle=True)

    def draw_frame(self, data):
        resolution = self.args.resol
        save_dir  = self.args.save_dir
        os.makedirs(save_dir, exist_ok=True)

        file_name = "snapshot_t"+str(self.args.frame).zfill(4)+".png"
        output_path = os.path.join(save_dir, f"{file_name}")

        fig = plt.figure(figsize=(16 * resolution, 9 * resolution))
        ax  = plt.axes(projection='3d')

        ax.set_xlim(-15, 15)
        ax.set_ylim(-15, 15)
        ax.set_zlim(-15, 15)

        ax.view_init(elev=self.args.elev, azim=self.args.azim) #카메라 돌리기
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')

        sizes_0 = np.random.uniform(0.2, 0.5, size=data[0].shape[1])
        sizes_1 = np.random.uniform(0.2, 0.5, size=data[1].shape[1])

        ax.scatter3D(data[0][0, :], data[0][1, :], data[0][2, :], s=sizes_0, c='white')
        ax.scatter3D(data[1][0, :], data[1][1, :], data[1][2, :], s=sizes_1, c='gray')

        # Add title and legend
        ax.set_title('Galaxy Collision')
        ax.grid(False)
        ax.set_axis_off()
        
        # Save or show the image
        fig.canvas.draw()
        image = np.array(fig.canvas.buffer_rgba())
        image = np.array(Image.fromarray(image).resize((1920, 1080)))
        plt.savefig(output_path, facecolor=fig.get_facecolor())
        plt.close(fig)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Draw Image")
    parser.add_argument("--load_dir", type=str, default="outputs", help="Load directory")
    parser.add_argument("--prefix", type=str, default="snapshot", help="Prefix of an output file")
    parser.add_argument("--frame", type=int, default=700, help="Frame number")
    parser.add_argument("--save_dir", type=str, default="Images", help="Save directory")
    parser.add_argument("--resol", type=int, default=2, help="Image resolution")
    parser.add_argument("--elev", type=float, default=60, help="elev angle")
    parser.add_argument("--azim", type=float, default=0, help="azim angle")

    start_time = time.time()
    args = parser.parse_args()

    data=Img(args)
    data.draw_frame(data.frame_data)
    end_time = time.time()

    print(f"\(^_^)/ \(^_^)/ Total time for making the image: {end_time - start_time:.3f} seconds.")
