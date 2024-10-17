# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Quick test of TFT FeatherWing (ILI9341) with Feather M0 or M4
# Will fill the TFT black and put a red pixel in the center, wait 2 seconds,
# then fill the screen blue (with no pixel), wait 2 seconds, and repeat.

import sounddevice
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

FONT_SIZE_TITLE = 14
FONT_SIZE_MAIN = 16
FONT_HEIGHT_TITLE = FONT_SIZE_TITLE + 1
FONT_HEIGHT_MAIN = FONT_SIZE_MAIN + 5

PERIOD_LOCK_DAY = 3
# PERIOD_LOCK_SEC = PERIOD_LOCK_DAY * 24 * 60 * 60
PERIOD_LOCK_SEC = 20
# PERIOD_GUARD_SEC = 5 * 60
PERIOD_GUARD_SEC = 2
PERIOD_LOCKING_SEC = 10

MENU_STATE_MAIN = 1
MENU_STATE_BOX_LOCKING = 2

menu_state = MENU_STATE_MAIN

font = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnDinaruLight.ttf", FONT_SIZE_MAIN)
font_title = ImageFont.truetype("/usr/share/fonts/truetype/unfonts-core/UnGraphicBold.ttf", FONT_SIZE_TITLE)

TITLE = "간식창고:승승장구"


ALERT_SILICA_GEL_DIFF = 20

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuratoin for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D22)
rst_pin = digitalio.DigitalInOut(board.D27)

pin_switch = digitalio.DigitalInOut(board.D26)
pin_switch.pull = digitalio.Pull.DOWN

# pin_servo_plus = digitalio.DigitalInOut(board.D5)
# pin_servo_minus = digitalio.DigitalInOut(board.D6)
# pin_servo_plus.direction = digitalio.Direction.OUTPUT
# pin_servo_minus.direction = digitalio.Direction.OUTPUT

temp_sensor_internal = adafruit_dht.DHT11(board.D23)
temp_sensor_external = adafruit_dht.DHT11(board.D24)

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

# 디스플레이 폭에 맞는 기준 글자 수 (숫자나 특수문자 기준)
CHARS_PER_LINE = 17

# 한글 문자의 상대적 폭
KOREAN_CHAR_WIDTH = 0.6

def is_korean(char):
    return ord('가') <= ord(char) <= ord('힣')

def char_width(char):
    return KOREAN_CHAR_WIDTH if is_korean(char) else 1

# Updated wrap_text function to consider Korean characters' width
def wrap_text(text):
    wrapped_lines = []
    current_line = ""
    current_width = 0

    for char in text:
        char_w = char_width(char)
        if current_width + char_w > CHARS_PER_LINE:
            wrapped_lines.append(current_line)
            current_line = char
            current_width = char_w
        else:
            current_line += char
            current_width += char_w

    if current_line:
        wrapped_lines.append(current_line)

    return wrapped_lines


def do_change_silica_gel():
    if temp_sensor_external.humidity is None or temp_sensor_internal.humidity is None:
        return False

    if temp_sensor_external.humidity - temp_sensor_internal.humidity < ALERT_SILICA_GEL_DIFF:
        return True
    else:
        return False


def disp_title():
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), f"{TITLE} ({datetime.now().strftime('%y%m%d / %H:%M:%S')})", font=font_title, fill="#FFFFFF")
    
def disp_main():    
    try:
        disp_title()

        text_temperature_humidity_int = f"내부 : {temp_sensor_internal.temperature}°C / {temp_sensor_internal.humidity}%"
        text_temperature_humidity_ext = f"외부 : {temp_sensor_external.temperature}°C / {temp_sensor_external.humidity}%"
        text_temperature_humidity = f"온습도. {text_temperature_humidity_int}, {text_temperature_humidity_ext}"

        if temp_sensor_internal.temperature is not None and temp_sensor_internal.humidity is not None:
            draw.text((0, FONT_HEIGHT_MAIN), text_temperature_humidity, font=font, fill="#FFFFFF")
        
        
        if do_change_silica_gel():
            text_change_silica_gel = f"실리카겔 교체 알림: 교체 필요"
            draw.text((0, FONT_HEIGHT_MAIN * 2), text_change_silica_gel, font=font, fill="#FF0000")
        else:
            text_change_silica_gel = f"실리카겔 교체 알림: 교체 불필요"
            draw.text((0, FONT_HEIGHT_MAIN * 2), text_change_silica_gel, font=font, fill="#FFFFFF")

        if box.isOpen == True:
            text_box_remaining = f"간식 창고가 열려있습니다."
        else:
            if box.is_unlockable() == True:
                text_box_remaining = f"간식 창고를 열 수 있습니다."
            else:
                text_box_remaining = f"남은시간: {box.get_remaining_time()}"

        # text_box_remaining = f"남은시간: {box.get_remaining_time()}"
        draw.text((0, FONT_HEIGHT_MAIN * 3), text_box_remaining, font=font, fill="#FFFFFF")

        text_box_content = f"간식 종류: {box.content}"
        draw.text((0, FONT_HEIGHT_MAIN * 4), text_box_content, font=font, fill="#FFFFFF")

        text_box_content_desc = f"{box.content_desc}"
        wrapped_text_box_content_desc = wrap_text(text_box_content_desc)

        for i, line in enumerate(wrapped_text_box_content_desc):
            draw.text((0, FONT_HEIGHT_MAIN * ( 5 + i ) ), line, font=font, fill="#FFFFFF")

    except RuntimeError:
        pass

    disp.image(image)


def disp_lock():
    try:
        disp_title()

        text_state = f"현재 열려있는 상태입니다.."
        text_lock = f"간식 창고를 잠그겠습니다."
        text_target_day = f"{PERIOD_LOCK_SEC / 24 / 60 / 60}일 뒤에 열 수 있습니다."
        text_guard = f"{PERIOD_GUARD_SEC / 60}분 내에는 다시 열 수 있습니다."

        draw.text((0, FONT_HEIGHT_MAIN), text_state, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 2), text_lock, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 3), text_target_day, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 4), text_guard, font=font, fill="#FFFFFF")

    except RuntimeError:
        pass

    disp.image(image)

def disp_record():
    try:
        disp_title()

        text_state = f"잠겨있는 상태입니다.."

        text_food_name = f"현재 간식: {box.content if assistant.user_input == None else assistant.user_input}"
        text_switch_long = "스위치 길게 눌러 간식 업데이트"
        text_switch_short = f"스위치 짧게 눌러 {'돌아가기' if assistant.user_input == None else '확인'}"

        text_switch_on_recording_started = "녹음중... 간식 내용을 말하세요."


        draw.text((0, FONT_HEIGHT_MAIN), text_state, font=font, fill="#FFFFFF")
        
        draw.text((0, FONT_HEIGHT_MAIN * 2), text_food_name, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 3), text_switch_long, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 4), text_switch_short, font=font, fill="#FFFFFF")

        if assistant.recording_started:
            draw.text((0, FONT_HEIGHT_MAIN * 6), text_switch_on_recording_started, font=font, fill="#FFFFFF")


    except RuntimeError:
        pass

    disp.image(image)

def disp_record_confirm():
    try:
        disp_title()

        text_subtitle = f"입력된 간식이름:"
        text_food_name = f"{assistant.user_input}"

        text_switch_long = "스위치 길게 눌러 다시 녹음"
        text_switch_short = "스위치 짧게 확인완료"

        draw.text((0, FONT_HEIGHT_MAIN), text_subtitle, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 2), text_food_name, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 3), text_switch_long, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 4), text_switch_short, font=font, fill="#FFFFFF")

    except RuntimeError:
        pass

    disp.image(image)

def disp_locking():
    try:
        disp_title()

        if box.isOpen == True:  #여는중
            text_locking = f"상자를 여는중입니다."    
        else:   #닫는중
            text_locking = f"상자를 닫는중입니다."

        text_waiting = f"잠시만 기다려주세요."    

        draw.text((0, FONT_HEIGHT_MAIN), text_locking, font=font, fill="#FFFFFF")
        draw.text((0, FONT_HEIGHT_MAIN * 2), text_waiting, font=font, fill="#FFFFFF")

    except RuntimeError:
        pass

    disp.image(image)



def on_switch_main():
    global menu_state
    current_time = datetime.now()

    if pin_switch.value == True:  
        if menu_state == MENU_STATE_BOX_LOCKING:
            print("locking 중입니다.")
            return
              
        if box.isOpen == True:
            box.toggle()    
        else:
            # assistant.run()
            if box.is_unlockable() == True or  box.is_guarding() == True:
                box.toggle()
            else:
                assistant.run()


class FoodAssistant:
    def __init__(self):
        self.client = OpenAI(api_key="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")
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = 5
        self.is_recording = False
        self.recording_started = False
        self.user_input = None

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
        print("record_audio")

        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        
        # print("스위치를 누르고 있는 동안 녹음됩니다. 스위치를 떼면 녹음이 종료됩니다.")

        frames = []
        self.is_recording = False
        switch_press_time = 0
        return_to_main = False
        self.recording_started = False
        self.user_input = None

        disp_record()
        while True:
            # print("녹음 대기 중")
            if len(frames) == 0:
                disp_record()

            # print(f"pin_switch.value:{pin_switch.value}")

            if pin_switch.value:
                if not self.is_recording:
                    self.is_recording = True
                    switch_press_time = time.time()
                
                if self.is_recording:
                    if not self.recording_started and time.time() - switch_press_time >= 0.5:
                        print("녹음 시작...")
                        self.recording_started = True
                        disp_record()
                    data = stream.read(self.CHUNK)
                    frames.append(data)
            else:
                if self.is_recording:
                    self.is_recording = False
                    self.recording_started = False
                    if time.time() - switch_press_time < 0.5:
                        return_to_main = True
                        print("처음으로 돌아가기.")
                        break
                    else:
                        print("녹음 종료")
                        break



        stream.stop_stream()
        stream.close()
        p.terminate()

        if return_to_main:
            return None


        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wf = wave.open(tmp_file.name, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            return tmp_file.name

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
                    6. 160글자를 넘지 않도록 작성해.
                    7. 줄바꿈이나 특수문자를 사용하지 마.
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

    def run(self):
        while True:
            try:
                audio_file = self.record_audio()

                if audio_file is None:
                    return
                
                # debugging 다시 듣기
                data, samplerate = sf.read(audio_file)
                self.play_audio(data, samplerate)

                self.user_input = self.speech_to_text(audio_file)
                os.unlink(audio_file)
                print(f"인식된 텍스트: {self.user_input}")
                print("인식된 텍스트가 맞으면 스위치를 짧게, 다시 녹음하려면 길게 누르세요.")
                
                switch_press_time = 0
                recall = False

                while True:
                    disp_record()

                    if recall == True: break

                    if pin_switch.value:
                        switch_press_time = time.time()
                        while pin_switch.value:
                            # print("pin is pressing")
                            # print(f"time.time() - switch_press_time:{time.time() - switch_press_time}")

                            if time.time() - switch_press_time >= 0.5:
                                print("break wait loop")
                                recall = True
                                break
                            else:                    
                                pass  # 스위치가 눌려있는 동안 대기
                    else:
                        if switch_press_time != 0:
                            break

                if time.time() - switch_press_time < 0.5:
                    if assistant.user_input != None:
                        prompt = f"{self.user_input}에 대해 알려주세요."
                        response = self.get_chatgpt_response(prompt)

                        box.content = assistant.user_input
                        box.content_desc = response

                        print("\nChatGPT 응답:")
                        print(response)
                        print("\n음성으로 응답을 들려드리겠습니다.")
                        self.text_to_speech(response, 1.5)

                    break
            except RuntimeError:
                return



class TimeLockedBox:
    def __init__(self, content, content_desc, unlock_date):
        self.content = content
        self.content_desc = content_desc
        self.isOpen = False
        self.unlock_date = unlock_date
        self.last_closed_time = None
        self.locking_start_time = None

    def toggle(self):
        global menu_state

        current_time = datetime.now()
        self.locking_start_time = current_time
        menu_state = MENU_STATE_BOX_LOCKING

        if self.isOpen:
            print("상자가 닫혔습니다.")
            self.isOpen = False
            self.last_closed_time = current_time
            self.unlock_date = datetime.now() + timedelta(seconds=PERIOD_LOCK_SEC)
        else:
            print("상자가 열렸습니다.")
            self.isOpen = True


    def get_remaining_time(self):
        current_time = datetime.now()

        time_diff = self.unlock_date - current_time
        
        if time_diff <= timedelta():
            return "00일 00시간 00분 00초"
        
        days = time_diff.days
        hours = time_diff.seconds // 3600
        minutes = (time_diff.seconds % 3600) // 60
        seconds = time_diff.seconds % 60
        
        return f"{days:02d}일 {hours:02d}시간 {minutes:02d}분 {seconds:02d}초"
    
    def is_unlockable(self):
        current_time = datetime.now()

        if self.isOpen == False and current_time < self.unlock_date:
            # print("아직 열 수 없습니다.")
            return False
        else:
            # print("열수 있습니다.")
            return True


    def is_guarding(self):
        current_time = datetime.now()

        if self.last_closed_time is None or (current_time - self.last_closed_time) <= timedelta(seconds=PERIOD_GUARD_SEC):
            print("가드타이머 적용중")
            return True
        else:
            print("가드타이머를 벗어남")
            return False


    def display_remaining_time(self):
        current_time = datetime.now()
        if current_time < self.unlock_date:
            remaining_time = self.unlock_date - current_time
            print(f"상자를 열 수 있을 때까지 남은 시간: {remaining_time}")
        else:
            print("상자를 열 수 있습니다.")

unlock_date = datetime.now() + timedelta(seconds=PERIOD_LOCK_SEC)
box = TimeLockedBox("간식", "일이삼사오육111칠팔구십1234567890일이삼사1111오육1칠1팔구십1234567890", unlock_date)
assistant = FoodAssistant()

try:
    while True:
        current_time = datetime.now()

        if menu_state == MENU_STATE_MAIN:
            disp_main()

        elif menu_state == MENU_STATE_BOX_LOCKING:
            disp_locking()

            if (current_time - box.locking_start_time).total_seconds() > PERIOD_LOCKING_SEC:
                menu_state = MENU_STATE_MAIN

        # pin_servo_plus.value = True    
        on_switch_main()

        # time.sleep(0.01)

except KeyboardInterrupt:
    print("\n프로그램이 사용자에 의해 종료되었습니다.")
finally:
    print("프로그램을 정리하고 종료합니다.")