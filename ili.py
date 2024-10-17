# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Quick test of TFT FeatherWing (ILI9341) with Feather M0 or M4
# Will fill the TFT black and put a red pixel in the center, wait 2 seconds,
# then fill the screen blue (with no pixel), wait 2 seconds, and repeat.

import time
from datetime import datetime, timedelta
import random
import busio
import digitalio
import board
import subprocess
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display.rgb import color565
from adafruit_rgb_display import ili9341
import adafruit_dht 

from datetime import datetime

import os
import wave
import pyaudio
import tempfile
from openai import OpenAI
import soundfile as sf
import numpy as np
import warnings

# 숫자키입력제어
# from pynput import keyboard
import time

# 버퍼 비우기
import sys
import platform

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

FONT_HEIGHT_TITLE = 14
FONT_HEIGHT_MAIN = 20

font = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnBatang.ttf", FONT_HEIGHT_MAIN)
font_title = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnGraphicBold.ttf", FONT_HEIGHT_TITLE)

TITLE = "간식창고:승승장구"
count = 1

warnings.filterwarnings("ignore", category=DeprecationWarning)


# Configuratoin for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D22)
rst_pin = digitalio.DigitalInOut(board.D27)
# temp_pin = digitalio.DigitalInOut(board.D23)
# temp_pin.direction = digitalio.Direction.INPUT
# temp_pin.pull = digitalio.Pull.DOWN

pin_switch = digitalio.DigitalInOut(board.D26)

# pin_servo_plus = digitalio.DigitalInOut(board.D5)
# pin_servo_minus = digitalio.DigitalInOut(board.D6)

# pin_servo_plus.direction = digitalio.Direction.OUTPUT
# pin_servo_plus.pull = digitalio.Pull.UP

# pin_servo_minus.direction = digitalio.Direction.OUTPUT
# pin_servo_minus.pull = digitalio.Pull.DOWN

# pin_servo_minus.value = False


temp_sensor = adafruit_dht.DHT11(board.D23)

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create the ILI9341 display:
disp = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=rst_pin, baudrate=BAUDRATE, rotation=90)

if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

draw = ImageDraw.Draw(image)

def disp_status():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    try:

        text_temperature = f"온도 : {temp_sensor.temperature}°C"
        text_humidity = f"습도 : {temp_sensor.humidity}%"

        #draw.text((0, 0), f"{TITLE}({count})", font=font_title, fill="#FFFFFF")
        draw.text((0, 0), f"{TITLE} ({datetime.now().strftime('%y%m%d / %H:%M:%S')})", font=font_title, fill="#FFFFFF")
        #draw.text((0, 20), f"({datetime.now().strftime('%y%m%d.%H:%M:%S')})", font=font_title, fill="#FFFFFF")
        #draw.rectangle((0, 20, (width, 20)), outline=0, fill=(255,255,255))
        # draw.rectangle((0, 20, width, 40), outline=0, fill=(85,85,85))
        # draw.text((0, 20), f"{datetime.now().strftime('%y%m%d.%H:%M:%S')}", font=font_title, fill="#FF0000")
        if temp_sensor.temperature is not None:
            draw.text((0, FONT_HEIGHT_MAIN), text_temperature, font=font, fill="#FFFFFF")
        if temp_sensor.humidity is not None:
            draw.text((0, FONT_HEIGHT_MAIN * 2), text_humidity, font=font, fill="#FFFFFF")

        text_box_remaining = f"남은시간: {box.get_remaining_time()}"
        draw.text((0, FONT_HEIGHT_MAIN * 3), text_box_remaining, font=font, fill="#FFFFFF")

        text_box_open = f"상자열림: {box.isOpen}"
        draw.text((0, FONT_HEIGHT_MAIN * 4), text_box_open, font=font, fill="#FFFFFF")

        text_box_content = f"간식 종류: {box.content}"
        draw.text((0, FONT_HEIGHT_MAIN * 5), text_box_content, font=font, fill="#FFFFFF")

        # text_switch = f"스위치: {pin_switch.value}"
        # draw.text((0, 115), text_switch, font=font, fill="#FFFFFF")

        # if pin_switch.value == True:
        #     print("switch on")
        #     pin_servo_plus.value = True
        #     pin_servo_minus.value = False

    except RuntimeError:
        pass

    disp.image(image)

def on_switch_main():
    if pin_switch.value:
        
        if box.isOpen:
            box.toggle()    
        else:
            assistant.run()

# def on_switch_record():

class FoodAssistant:
    def __init__(self):
        self.client = OpenAI(api_key="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")
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 5

    @staticmethod
    def flush_input():
        if platform.system() == "Windows":
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        else:
            import termios
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)

    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        
        print("스위치를 누르고 있는 동안 녹음됩니다. 스위치를 떼면 녹음이 종료됩니다.")
        print("스위치를 짧게 한 번만 누르면 프로그램이 종료됩니다.")

        frames = []
        is_recording = False
        switch_press_time = 0
        program_exit = False
        recording_started = False

        while True:
            if pin_switch.value:
                if not is_recording:
                    is_recording = True
                    switch_press_time = time.time()
                
                if is_recording:
                    if not recording_started and time.time() - switch_press_time >= 0.5:
                        print("녹음 시작...")
                        recording_started = True
                    data = stream.read(self.CHUNK)
                    frames.append(data)
            else:
                if is_recording:
                    is_recording = False
                    if time.time() - switch_press_time < 0.5:
                        program_exit = True
                        print("프로그램을 종료합니다.")
                        break
                    else:
                        print("녹음 종료")
                        break

        stream.stop_stream()
        stream.close()
        p.terminate()

        if program_exit:
            return None

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wf = wave.open(tmp_file.name, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return tmp_file.name

    # def record_audio(self):
    #     p = pyaudio.PyAudio()
    #     stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        
    #     print("숫자 키 1을 누르고 있는 동안 녹음됩니다. 키를 떼면 녹음이 종료됩니다.")
    #     print("1을 짧게 한 번만 누르면 프로그램이 종료됩니다.")

    #     frames = []
    #     is_recording = False
    #     key_press_time = 0
    #     program_exit = False
    #     recording_started = False

    #     def on_press(key):
    #         nonlocal is_recording, key_press_time
    #         if key == keyboard.KeyCode.from_char('1'):
    #             if not is_recording:
    #                 is_recording = True
    #                 key_press_time = time.time()

    #     def on_release(key):
    #         nonlocal is_recording, key_press_time, program_exit, recording_started
    #         if key == keyboard.KeyCode.from_char('1'):
    #             is_recording = False
    #             if time.time() - key_press_time < 0.5:
    #                 program_exit = True
    #                 print("프로그램을 종료합니다.")
    #             else:
    #                 print("녹음 종료")
    #             return False

    #     listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    #     listener.start()

    #     while listener.running:
    #         if is_recording:
    #             if not recording_started and time.time() - key_press_time >= 0.5:
    #                 print("녹음 시작...")
    #                 recording_started = True
    #             data = stream.read(self.CHUNK)
    #             frames.append(data)

    #     stream.stop_stream()
    #     stream.close()
    #     p.terminate()

    #     if program_exit:
    #         return None

    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
    #         wf = wave.open(tmp_file.name, 'wb')
    #         wf.setnchannels(self.CHANNELS)
    #         wf.setsampwidth(p.get_sample_size(self.FORMAT))
    #         wf.setframerate(self.RATE)
    #         wf.writeframes(b''.join(frames))
    #         wf.close()
    #         return tmp_file.name

    def speech_to_text(self, audio_file):
        with open(audio_file, "rb") as file:
            transcript = self.client.audio.transcriptions.create(model="whisper-1", file=file, language="ko")
        return transcript.text

    def get_chatgpt_response(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": """당신은 음식에 대한 정보를 제공하는 도우미입니다. 다음 지침을 따라주세요:
                    1. 음식이나 과자에 대한 정보를 제공할 때, 아토피가 있는 사람이 그 음식을 먹을 때 주의해야 할 사항을 두 줄 이내로 알려줘.
                    2. 제시된 음식을 반드시 먹는다는 전제 하에, 섭취 주기와 주의사항 위주로 조언해.
                    3. 해당 음식과 관련된 즐겁고 재미있는 이야기를 한 줄 추가해.
                    4. 추상적인 이야기보다는 음식을 재미있게 먹을 수 있는 구체적인 방법 위주로 추가해.
                    5. 과자나 음식의 주제에서 벗어나면 다시 질문해.
                     """},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"오류가 발생했습니다: {str(e)}"

    @staticmethod
    def play_audio(data, samplerate):
        p = pyaudio.PyAudio()
        data_int16 = (data * 32767).astype(np.int16)
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=samplerate, output=True)
        for i in range(0, len(data_int16), 1024):
            chunk = data_int16[i:i+1024]
            stream.write(chunk.tobytes())
        stream.stop_stream()
        stream.close()
        p.terminate()

    @staticmethod
    def adjust_speed(data, speed):
        length = len(data)
        new_length = int(length / speed)
        return np.interp(np.linspace(0, length, new_length), np.arange(length), data)

    def text_to_speech(self, text, speed=1.0):
        tmp_file_name = "./output.wav"
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text,
        )
        response.stream_to_file(tmp_file_name)
        data, samplerate = sf.read(tmp_file_name)
        if speed != 1.0:
            data = self.adjust_speed(data, speed)
        self.play_audio(data, samplerate)
        os.unlink(tmp_file_name)

    # def run(self):
    #     while True:
    #         print("음식 이름을 말씀해주세요. (종료하려면 '종료'라고 말씀하세요)")
    #         while True:
    #             audio_file = self.record_audio()
    #             if audio_file is None:
    #                 return
    #             user_input = self.speech_to_text(audio_file)
    #             os.unlink(audio_file)
    #             print(f"인식된 텍스트: {user_input}")
    #             self.flush_input()
    #             confirmation = input("인식된 텍스트가 맞습니까? (y/n): ").lower()
    #             if confirmation == 'y':
    #                 break
    #             else:
    #                 print("다시 녹음해 주세요.")
    #         prompt = f"{user_input}에 대해 알려주세요."
    #         response = self.get_chatgpt_response(prompt)
    #         print("\nChatGPT 응답:")
    #         print(response)
    #         print("\n음성으로 응답을 들려드리겠습니다.")
    #         self.text_to_speech(response, 1.5)

    def run(self):
        while True:
            print("음식 이름을 말씀해주세요. (종료하려면 스위치를 짧게 누르세요)")
            audio_file = self.record_audio()
            if audio_file is None:
                return
            user_input = self.speech_to_text(audio_file)
            os.unlink(audio_file)
            print(f"인식된 텍스트: {user_input}")
            self.flush_input()
            print("인식된 텍스트가 맞으면 스위치를 길게, 다시 녹음하려면 짧게 누르세요.")
            
            switch_press_time = 0
            while True:
                if pin_switch.value:
                    switch_press_time = time.time()
                    while pin_switch.value:
                        pass  # 스위치가 눌려있는 동안 대기
                    if time.time() - switch_press_time >= 0.5:
                        break  # 긴 누름: 확인
                    else:
                        print("다시 녹음해 주세요.")
                        audio_file = self.record_audio()
                        if audio_file is None:
                            return
                        user_input = self.speech_to_text(audio_file)
                        os.unlink(audio_file)
                        print(f"인식된 텍스트: {user_input}")
            
            prompt = f"{user_input}에 대해 알려주세요."
            response = self.get_chatgpt_response(prompt)
            print("\nChatGPT 응답:")
            print(response)
            print("\n음성으로 응답을 들려드리겠습니다.")
            self.text_to_speech(response, 1.5)
class TimeLockedBox:
    def __init__(self, content, unlock_date):
        self.content = content
        self.isOpen = False
        self.unlock_date = unlock_date
        self.last_closed_time = None

    def toggle(self):
        current_time = datetime.now()

        if self.isOpen:
            print("상자가 닫혔습니다.")
            self.isOpen = False
            self.last_closed_time = current_time
            self.unlock_date = datetime.now() + timedelta(minutes=1)  # 10분 후에 열 수 있도록 설정
        else:
            if current_time >= self.unlock_date:
                # if self.last_closed_time is None or (current_time - self.last_closed_time) <= timedelta(minutes=5):
                if self.last_closed_time is None or (current_time - self.last_closed_time) <= timedelta(seconds=3):
                    self.isOpen = True
                    print("상자가 열렸습니다.")
                else:
                    print("상자를 열 수 없습니다. 5분 이상 지났습니다.")
            else:
                print(f"상자의 내용: {self.content}")
                remaining_time = self.unlock_date - current_time
                print(f"상자를 열 수 있을 때까지 남은 시간: {remaining_time}")

    def get_remaining_time(self):
        current_time = datetime.now()
        # return self.unlock_date - current_time

        time_diff = self.unlock_date - current_time
        
        if time_diff <= timedelta():
            return "00일 00시간 00분 00초"
        
        days = time_diff.days
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        
        return f"{days:02d}일 {hours:02d}시간 {minutes:02d}분 {time_diff.seconds:02d}초"

    def display_remaining_time(self):
        current_time = datetime.now()
        if current_time < self.unlock_date:
            remaining_time = self.unlock_date - current_time
            print(f"상자를 열 수 있을 때까지 남은 시간: {remaining_time}")
        else:
            print("상자를 열 수 있습니다.")

# 사용 예시
unlock_date = datetime.now() + timedelta(minutes=1)  # 10분 후에 열 수 있도록 설정
box = TimeLockedBox("중요한 문서", unlock_date)
assistant = FoodAssistant()


while True:
    # pin_servo_plus.value = True    
    on_switch_main()

    disp_status()

    count = count + 1

    # time.sleep(0.01)