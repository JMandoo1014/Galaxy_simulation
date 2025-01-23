import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse

# Outputs 폴더 경로 설정
OUTPUT_DIR = "outputs"
ANGLE_FILE = "test.txt"  # 카메라 각도를 저장할 파일
INPUT_INFO = """
exit : 프로그램 종료
NUM :  snapshot_tNUM.npy 열기
+NUM : 현재 프레임 NUM번 '후' 프레임 열기
-NUM : 현재 프레임 NUM번 '전' 프레임 열기
save : 카메라 각도 저장
enter : 다음
make_image : 지금 보고있는 화면 이미지로 만들기
make_movie : 지금 보고있는 각도로 동영상 만들기
elevNUM : elev각도를 NUM으로 변경
azimNUM : azim각도를 NUM으로 변경

입력 : """
# npy파일들 정렬해서 반환
def load_npy_files(output_dir):
    npy_files = sorted([f for f in os.listdir(output_dir) if f.endswith(".npy")])
    return [os.path.join(output_dir, f) for f in npy_files]

def visualize_snapshot(data, ax, fig):
    gal1, gal2 = data 
    
    ax.clear()

    fig.patch.set_facecolor('black')
    ax.view_init(elev = ax.elev, azim = ax.azim)
    
    ax.scatter(gal1[0], gal1[1], gal1[2], color="white", s=0.5, label="Galaxy 1")
    ax.scatter(gal2[0], gal2[1], gal2[2], color="gray", s=0.5, label="Galaxy 2")
    
    ax.set_axis_off()
    ax.set_facecolor("black")  # Set background to black

def update_status_bar(ax, fig):
    elev, azim = ax.elev, ax.azim
    fig.canvas.toolbar.set_message(f"Elev: {elev:.2f}, Azim: {azim:.2f}")

def save_camera_angle(ax, angle_file):
    elev = ax.elev
    azim = ax.azim
    with open(angle_file, "a") as f:
        f.write(f"elev: {elev}, azim: {azim}\n")
    print(f"카메라 각도 저장됨 -> elev: {elev}, azim: {azim}")

def on_mouse_event(event, fig, ax):
    update_status_bar(ax, fig)

def main():

    #npy파일들 리스트
    npy_files = load_npy_files(OUTPUT_DIR)
    
    if not npy_files:
        print("파일 경로 없음")
        return


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', facecolor="black")
    ax.elev = 0
    ax.azim = 0
    snapshot_idx = 0  # 초기값
    # Set the initial status bar
    update_status_bar(ax, fig)
    
    # Connect mouse events to update the status bar
    fig.canvas.mpl_connect("motion_notify_event", lambda event: on_mouse_event(event, fig, ax))
    fig.canvas.mpl_connect("button_release_event", lambda event: on_mouse_event(event, fig, ax))
    
    while True:
        # 에러방지
        if snapshot_idx < 0 or snapshot_idx >= len(npy_files):
            print(f"인덱스 에러, 최대 크기 : {len(npy_files)}")
            snapshot_idx = 0

        #스냅샷.npy 불러오기
        data = np.load(npy_files[snapshot_idx])

        #그리기
        visualize_snapshot(data, ax, fig)
        plt.draw()
        plt.pause(0.1)
        
        print(f"스냅샷 {snapshot_idx + 1}/{len(npy_files)} 보는 중")
        
        user_input = input(INPUT_INFO).strip().lower()
        print()
        
        if user_input == "exit":
            break
        elif user_input == "save":
            save_camera_angle(ax, ANGLE_FILE)
        elif user_input == "make_movie" :
            os.system(f"mpiexec -n 10 python make_movie.py --elev {ax.elev} --azim {ax.azim} --name ezViewer")
        elif user_input == "make_image" :
            os.system(f"python make_image.py --elev {ax.elev} --azim {ax.azim} --save_dir ezViewerImages --resol 1")
        elif user_input.isdigit():
            snapshot_idx = int(user_input) - 1
        elif len(user_input) and user_input[0]=="+":
            snapshot_idx+=int(user_input[1:])
        elif len(user_input) and user_input[0]=="-":
            snapshot_idx-=int(user_input[1:])
        elif len(user_input) and user_input[0:4]=="elev":
            ax.elev = int(user_input[4:])
        elif len(user_input) and user_input[0:4]=="azim":
            ax.azim = int(user_input[4:])
        else:
            snapshot_idx += 1  

    print("종료.")
    plt.close(fig)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_dir", type=str, default="outputs", help="Save directory")
    main()
