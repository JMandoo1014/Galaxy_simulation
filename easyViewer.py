import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Outputs 폴더 경로 설정
OUTPUT_DIR = "outputs"
ANGLE_FILE = "camera_angles.txt"  # 카메라 각도를 저장할 파일

def load_npy_files(output_dir):
    """Load .npy files in the output directory."""
    npy_files = sorted([f for f in os.listdir(output_dir) if f.endswith(".npy")])
    return [os.path.join(output_dir, f) for f in npy_files]

def visualize_snapshot(data, ax):
    gal1, gal2 = data  # Extract galaxy data (each shape: 3, n)
    
    # Clear the current plot
    ax.clear()
    
    # Plot galaxy 1 (white)
    ax.scatter(gal1[0], gal1[1], gal1[2], color="white", s=0.5, label="Galaxy 1")
    
    # Plot galaxy 2 (gray)
    ax.scatter(gal2[0], gal2[1], gal2[2], color="gray", s=0.5, label="Galaxy 2")
    
    # Remove grid, axes, and background elements
    ax.set_axis_off()
    ax.set_facecolor("black")  # Set background to black

def update_status_bar(ax, fig):
    """Update the status bar with the current camera angles."""
    elev, azim = ax.elev, ax.azim
    fig.canvas.toolbar.set_message(f"Camera Angles - Elev: {elev:.2f}, Azim: {azim:.2f}")

def save_camera_angle(ax, angle_file):
    """Save the current camera angles to a file."""
    elev = ax.elev
    azim = ax.azim
    with open(angle_file, "a") as f:
        f.write(f"elev: {elev}, azim: {azim}\n")
    print(f"카메라 각도 저장됨 -> elev: {elev}, azim: {azim}")

def on_mouse_event(event, fig, ax):
    """Handle mouse motion and update the status bar."""
    update_status_bar(ax, fig)

def main():
    # Load all .npy files
    npy_files = load_npy_files(OUTPUT_DIR)
    
    if not npy_files:
        print("파일 경로 없음")
        return

    # Create a matplotlib 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', facecolor="black")  # Set figure background to black
    
    print("엔터는 다음 스냅샷, 숫자는 숫자번 스냅샷, save는 현재 카메라 각도 저장.")
    snapshot_idx = 0  # Current snapshot index

    # Set the initial status bar
    update_status_bar(ax, fig)
    
    # Connect mouse events to update the status bar
    fig.canvas.mpl_connect("motion_notify_event", lambda event: on_mouse_event(event, fig, ax))
    fig.canvas.mpl_connect("button_release_event", lambda event: on_mouse_event(event, fig, ax))
    
    while True:
        # Ensure the index is valid
        if snapshot_idx < 0 or snapshot_idx >= len(npy_files):
            print(f"1 이랑 {len(npy_files)} 사이 입력.")
            snapshot_idx = 0

        # Load the current snapshot
        data = np.load(npy_files[snapshot_idx])

        # Visualize the snapshot
        visualize_snapshot(data, ax)
        plt.draw()
        plt.pause(0.1)  # Update the plot
        
        print(f"스냅샷 {snapshot_idx + 1}/{len(npy_files)} 보는 중")
        print(f"현재 카메라 각도 -> elev: {ax.elev}, azim: {ax.azim}")  # 현재 각도 출력
        
        # Wait for user input
        user_input = input("exit : 프로그램 종료\nNUM :  snapshot_tNUM.npy 오픈\nsave : 카메라 각도 저장\nenter : 다음\n입력하세요. : ").strip().lower()
        print()
        
        if user_input == "exit":
            break
        elif user_input == "save":
            save_camera_angle(ax, ANGLE_FILE)
        elif user_input.isdigit():
            snapshot_idx = int(user_input) - 1  
        else:
            snapshot_idx += 1  

    print("종료.")
    plt.close(fig)

if __name__ == "__main__":
    main()
