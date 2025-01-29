# TrackON

2025 Unist Supercomputing camp

은하간 충돌 시뮬레이션

## 개발팀

최지호 : https://github.com/JMandoo1014

심기찬 : https://github.com/strain7626

## parameters

## Stacks

### environment

<div>
  <img src="https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"> 
  <br>
  
  <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
</div>

### development

<div>
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
</div>

## Code Files

- `Stars`, `Galaxy`, `Orbit` : 계산을 위한 클래스 파일들입니다.
- `mapi_mpi.py` : 은하간 충돌 시뮬레이션이 mpi 병렬화 처리되었습니다.
- `easyStarter.py`, `easyStarter.ui` : parameter 값들을 실시간으로 수정하며 볼 수 있게 구성된 파이썬 파일과 ui 파일입니다. pyQt로 통신합니다.
- `easyViewer.py` : 실시간 카메라 각도 수정이 가능한 파이썬 파일입니다.
- `make_mov_mpi.py`, `make_image` : 생성된 npy파일을 이미지와 영상으로 출력해주는 파이썬 파일입니다. 영상 출력의 경우 mpi 병렬화 처리되었습니다.
