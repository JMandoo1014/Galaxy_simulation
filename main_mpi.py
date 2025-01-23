from Galaxy import Galaxy
from Stars import Stars
from Orbit import Orbit
import argparse
import numpy as np
import tqdm
import time
import os
from mpi4py import MPI

In_theta1 = 0
In_phi1 =90
In_theta2 = 0
In_phi2 = 0
In_tot_nstar = 100000
In_mratio = 5
In_peri = 5
In_nstep = 1000

class Sim:

    def __init__(self, args):
        self.args = args

    def makeGalaxy(self):

        #\/\/\/# Constants - Please, do not change!!
        galmass = 4.8  # Galaxy mass (Host)
        ahalo   = 0.1  # Acceleration of the dark matter halo equivalent to the central gravity
        vhalo   = 1.0  # sqrt(r*dPhi/dr) of the dark matter halo
        rhalo   = 5.0  # Radius of the dark matter
        diskSize= 2.5  # Disk size of Host galaxy in kpc

        #=====#=====# Arrays for 3D position & velocity of the galaxy #=====#=====#      
        galpos = np.full((3, 1), 0.)
        galvel = np.full((3, 1), 0.)

        #=====#=====# Initial conditions for Galaxy1 and Galaxy2      #=====#=====#
        gal1theta = self.args.theta1 * (np.pi/180.) # theta of Galaxy1 (degree => Radian)
        gal1phi   = self.args.phi1   * (np.pi/180.) #  phi  of Galaxy1 (degree => Radian)
        gal2theta = self.args.theta2 * (np.pi/180.) # theta of Galaxy2 (degree => Radian)
        gal2phi   = self.args.phi2   * (np.pi/180.) #  phi  of Galaxy2 (degree => Radian)
        tot_nstar = self.args.tot_nstar             # Number of Total stars
        mratio = self.args.mratio                   # Mass ratio = M_gal2 / M_gal1

        n_gal1 = int(tot_nstar* 1.0 / (1.0 + mratio)) # Number of stars in Galaxy1
        n_gal2 = tot_nstar - n_gal1                   # Number of stars in Galaxy2

        #=====#=====# Make the initial positions of stars in Galaxies #=====#=====# 
        self.galaxy1 = Stars(galmass, ahalo, vhalo, rhalo, galpos, galvel, diskSize, gal1theta, gal1phi, n_gal1)
        self.galaxy2 = Stars(galmass, ahalo, vhalo, rhalo, galpos, galvel, diskSize, gal2theta, gal2phi, n_gal2)

        #\/\/\/# Initial parameters for the Halos - Please, do not change!!
        if self.args.big_halo:
            self.galaxy1.rhalo   = 20.0
            self.galaxy1.galmass = (self.galaxy1.vhalo**2 * self.galaxy1.rhalo**3)/((self.galaxy1.ahalo+self.galaxy1.rhalo)**2)
        else:
            self.galaxy1.rhalo   = 5.0
            self.galaxy1.galmass = 4.8

        if self.args.big_halo:
            self.galaxy2.rhalo   = self.galaxy2.rhalo*4.0
            self.galaxy2.galmass = (self.galaxy2.vhalo**2 * self.galaxy2.rhalo**3)/((self.galaxy2.ahalo+self.galaxy2.rhalo)**2)

        self.galaxy2.scaleMass(mratio)

    def makeOrbit(self):
        #\/\/\# Make orbits of colliding galaxies - Please, do not change!!
        energy = 0
        ecc    = 1    # eccentricity; ecc=0~1 elliptical, ecc=1 parabolic, ecc>1 hyperbolic orbit
        rperi  = 3.0  # The periapsis of a parabolic orbit which is the point of closest approach 
        tperi  = self.args.peri

        #=====# Calculate the initial colliding orbits of galaxies          #=====#
        self.crashOrbit = Orbit(energy, rperi, tperi, ecc, self.galaxy1.galmass, self.galaxy2.galmass, self.galaxy1.galpos, self.galaxy2.galpos, self.galaxy1.galvel, self.galaxy2.galvel)

        #=====# Updagte position and velocity of each galaxy                #=====#
        self.galaxy1.setPosvel(self.crashOrbit.p1pos, self.crashOrbit.p1vel)
        self.galaxy2.setPosvel(self.crashOrbit.p2pos, self.crashOrbit.p2vel)

        #\/\/\/# The initial distance and relative velocity between two galaxies
        dist = 3.5 * np.linalg.norm((self.galaxy1.galpos-self.galaxy2.galpos))
        vel  = 250.* np.linalg.norm((self.galaxy1.galvel-self.galaxy2.galvel))
    
    def runSim(self):
        part1LoadTime = 0
        part2LoadTime = 0
        part3LoadTime = 0
        allLoadTime = 0
        allSimTime = 0
        # MPI 초기화
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        dt = self.args.dt  # 시간 간격
        nstep = self.args.nstep  # 전체 시뮬레이션 단계
        
        datas_gal1_starpos = []
        datas_gal2_starpos = []
        datas_gal1_starvel = []
        datas_gal2_starvel = []
        #별들 위치 설정
        if rank == 0 :
            if self.args.seed_fix:
                self.galaxy1.initStars(seed=111203)
                self.galaxy2.initStars(seed=111203)
            else:   
                self.galaxy1.initStars()
                self.galaxy2.initStars()


            # 별을 프로세스 수만큼 분할
            total_stars_gal1 = self.galaxy1.starpos.shape[1]
            total_stars_gal2 = self.galaxy2.starpos.shape[1]
            for r in range(size) :
                #1개마다 얼마
                part_stars_gal1 = total_stars_gal1 // size
                part_stars_gal2 = total_stars_gal2 // size

                # 각 프로세스가 처리할 별의 범위 계산
                start_gal1 = r * part_stars_gal1 + r
                end_gal1 = start_gal1 + part_stars_gal1 + (r < total_stars_gal1 % size)

                start_gal2 = r * part_stars_gal2 + r
                end_gal2 = start_gal2 + part_stars_gal2 + (r < total_stars_gal2 % size)

                # 해당 프로세스의 별 데이터
                datas_gal1_starpos.append(self.galaxy1.starpos[:, start_gal1:end_gal1])
                datas_gal2_starpos.append(self.galaxy2.starpos[:, start_gal2:end_gal2])
                datas_gal1_starvel.append(self.galaxy1.starvel[:, start_gal1:end_gal1])
                datas_gal2_starvel.append(self.galaxy2.starvel[:, start_gal2:end_gal2])

        local_gal1_starpos = comm.scatter(datas_gal1_starpos, root=0)
        local_gal2_starpos = comm.scatter(datas_gal2_starpos, root=0)
        local_gal1_starvel = comm.scatter(datas_gal1_starvel, root=0)
        local_gal2_starvel = comm.scatter(datas_gal2_starvel, root=0)

        # 시뮬레이션 루프
        for step in range(nstep) :
            st = time.time()
            # 은하 간 거리 계산
            dist = 3.5 * np.linalg.norm((self.galaxy1.galpos - self.galaxy2.galpos))

            # 각 은하 중심의 가속도 계산
            self.galaxy1.galacc = self.galaxy2.acceleration(self.galaxy1.galpos)
            self.galaxy2.galacc = self.galaxy1.acceleration(self.galaxy2.galpos)

            # 각 은하 중심에 항력 추가
            self.galaxy1.galacc += self.galaxy2.dynFriction(self.galaxy1.interiorMass(dist / 3.5), self.galaxy1.galpos, self.galaxy1.galvel)
            self.galaxy2.galacc += self.galaxy1.dynFriction(self.galaxy2.interiorMass(dist / 3.5), self.galaxy2.galpos, self.galaxy2.galvel)

            # 은하 질량 중심 가속도를 제거하여 상대적인 움직임 계산
            comacc = ((self.galaxy1.galmass * self.galaxy1.galacc) + (self.galaxy2.galmass * self.galaxy2.galacc)) / (self.galaxy1.galmass + self.galaxy2.galmass)
            self.galaxy1.galacc -= comacc
            self.galaxy2.galacc -= comacc

            # 별의 가속도 계산 (각 프로세스는 자신의 범위만 계산)
            local_gal1_staracc = self.galaxy1.acceleration(local_gal1_starpos) + self.galaxy2.acceleration(local_gal1_starpos)
            local_gal2_staracc = self.galaxy1.acceleration(local_gal2_starpos) + self.galaxy2.acceleration(local_gal2_starpos)

            # 별의 위치와 속도 업데이트
            local_gal1_starpos += local_gal1_starvel * dt + 0.5 * local_gal1_staracc * (dt**2)
            local_gal1_starvel += local_gal1_staracc * dt

            local_gal2_starpos += local_gal2_starvel * dt + 0.5 * local_gal2_staracc * (dt**2)
            local_gal2_starvel += local_gal2_staracc * dt

            # 은하 중심의 위치 업데이트
            self.galaxy1.moveGalaxy(dt)
            self.galaxy2.moveGalaxy(dt)

            # 별 위치 저장
            frame = {
                "gal1": local_gal1_starpos,
                "gal2": local_gal2_starpos,
            }
            et = time.time()
            allSimTime += et-st

            st = time.time()
            if self.args.frame_number == -1 or step == self.args.frame_number:
                if rank != 0 :
                    comm.send(frame, dest=0, tag=step)
                else :
                    st2=time.time()
                    gal1_positions = frame["gal1"]
                    gal2_positions = frame["gal2"]
                    st = time.time()
                    for i in range(1,size) : 
                        received_frame = comm.recv(source=i, tag=step)

                        gal1_positions = np.hstack([gal1_positions, received_frame["gal1"]])
                        gal2_positions = np.hstack([gal2_positions, received_frame["gal2"]])
                    et = time.time()
                    part1LoadTime += et-st

                    # 크기 조정
                    st = time.time()
                    max_size = max(gal1_positions.shape[1], gal2_positions.shape[1])
                    gal1_positions_padded = np.pad(gal1_positions, ((0, 0), (0, max_size - gal1_positions.shape[1])),constant_values=np.nan)
                    gal2_positions_padded = np.pad(gal2_positions, ((0, 0), (0, max_size - gal2_positions.shape[1])),constant_values=np.nan)

                    # 결합
                    combined_frame = np.stack([gal1_positions_padded, gal2_positions_padded])
                    filename = os.path.join(self.args.save_dir, f"snapshot_t{step:04d}.npy")
                    et = time.time()
                    part2LoadTime += et-st
                    
                    st = time.time()
                    np.save(filename, combined_frame)
                    et = time.time()
                    
                    et2 = time.time()
                    part3LoadTime += et-st
                    allLoadTime+=et2-st2
                #특정 프레임만 원한다면 그 뒤는 시뮬 돌릴 필요가 없음
                if step == self.args.frame_number :
                    break

        #sim 끝날때 결과 출력
        print(f"\nabout rank{rank}")
        if rank == 0 :
            print("part1LoadTime :",part1LoadTime)
            print("part2LoadTime :",part2LoadTime)
            print("part3LoadTime :",part3LoadTime)
        print("allLoadTime :",allLoadTime)
        print("allSimTime :",allSimTime)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Galaxy Collision Simulation")
    parser.add_argument("--theta1", type=float, default=In_theta1, help="Polar angle of Galaxy #1 [0, 180]")
    parser.add_argument("--phi1", type=float, default=In_phi1, help="Azimuthal angle of Galaxy #1 [0, 360]")
    parser.add_argument("--theta2", type=float, default=In_theta2, help="Polar angle of Galaxy #2 [0, 180]")
    parser.add_argument("--phi2", type=float, default=In_phi2, help="Azimuthal angle of Galaxy #2 [0, 360]")
    parser.add_argument("--tot_nstar", type=int, default=In_tot_nstar, help="Total number of stars in galaxies")
    parser.add_argument("--mratio", type=float, default=In_mratio,  help="Mass ratio (M_g2/M_g1)")
    parser.add_argument("--peri", type=float, default=In_peri, help="Pericenter distance of galaxies in kpc [0, 100]")
    parser.add_argument("--dt", type=float, default=0.04, help="Time step [0.01, 0.10]")
    parser.add_argument("--nstep", type=int,   default=In_nstep, help="Total number of simulation steps [1, INF]")
    parser.add_argument("--big_halo", action="store_true", help="Use a larger halo size (rhalo=20.0)")
    parser.add_argument("--seed_fix", action="store_true", help="For fixing a seed #, seed=111203")

    #내가 만든 argument
    parser.add_argument("--save_dir", type=str, default="outputs", help="Save directory")
    # -1 이면 그냥 일반 다른 값이면 ezStarter용도로 사용
    parser.add_argument("--frame_number", type=int, default=-1, help="If you want specific frame use this")

    overall_start_time = time.time()
    args = parser.parse_args()
    os.makedirs(args.save_dir, exist_ok=True)

    sim = Sim(args)
    sim.makeGalaxy()
    sim.makeOrbit()

    sim.runSim()

    overall_end_time = time.time()
    if MPI.COMM_WORLD.Get_rank() == 0 :
        print(f"\(^_^)/ \(^_^)/ Total execution time: {overall_end_time - overall_start_time:.3f} seconds.")