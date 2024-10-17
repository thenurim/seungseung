
sudo apt install virtualenv fonts-unfonts-core libraspberrypi-dev raspberrypi-kernel-headers vim libopenblas-dev
pip install adafruit-circuitpython-dht pillow adafruit-circuitpython-rgb-display numpy

numpy를 설치하지 않아도 실행은 되지만 속도가 느림

추가되어 있지 않으면
sudo adduser thenurim gpio



- pip install  adafruit-circuitpython-display-text

- adagruit rgb의 속도를 높이는 방법
```
sudo apt install libopenblas-dev
pip instal numpy
```

<!-- sudo apt-get install python3-pyaudio -->


# 사운드 설정
- 스피커 테스트
$ arecord --format=S16_LE --duration=5 --rate=16000 --file-type=raw out.raw

- 마이크 테스트
$ arecord --format=S16_LE --duration=5 --rate=16000 --file-type=raw out.raw
$ aplay --format=S16_LE --rate=16000 out.raw

- 볼륨 조절
$ alsamixer

https://diy-project.tistory.com/88