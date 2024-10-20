# Team 승승장구. 2024 임베디드 SW 공모전 메이커 히어로즈 부문

## 실행 환경 구성
- 실행을 위한 raspberry pi 패키지 설치
```
sudo apt install virtualenv fonts-unfonts-core libraspberrypi-dev raspberrypi-kernel-headers vim libopenblas-dev
pip install adafruit-circuitpython-dht pillow adafruit-circuitpython-rgb-display numpy

```
- numpy를 설치하지 않아도 실행은 되지만 속도가 느림. 설치후 import 필요
- 실행을 위한 pip 패키지 설치
```
pip install  adafruit-circuitpython-display-text
```

- adagruit rgb의 속도를 높이는 방법
```
sudo apt install libopenblas-dev
pip instal numpy
```

## 사운드 설정
- 스피커 테스트
$ arecord --format=S16_LE --duration=5 --rate=16000 --file-type=raw out.raw

- 마이크 테스트
$ arecord --format=S16_LE --duration=5 --rate=16000 --file-type=raw out.raw
$ aplay --format=S16_LE --rate=16000 out.raw

- 볼륨 조절
$ alsamixer

- refs : https://diy-project.tistory.com/88