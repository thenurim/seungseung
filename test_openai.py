import os
import wave
import pyaudio
import tempfile
from openai import OpenAI
import soundfile as sf
import numpy as np
import warnings

# 숫자키입력제어
from pynput import keyboard
import time

# 버퍼 비우기
import sys
import platform

warnings.filterwarnings("ignore", category=DeprecationWarning)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key="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")

# 오디오 설정
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

def flush_input():
    """플랫폼에 따라 입력 버퍼를 비웁니다."""
    if platform.system() == "Windows":
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("숫자 키 1을 누르고 있는 동안 녹음됩니다. 키를 떼면 녹음이 종료됩니다.")
    print("1을 짧게 한 번만 누르면 프로그램이 종료됩니다.")

    frames = []
    is_recording = False
    key_press_time = 0
    program_exit = False
    recording_started = False

    def on_press(key):
        nonlocal is_recording, key_press_time
        if key == keyboard.KeyCode.from_char('1'):
            if not is_recording:
                is_recording = True
                key_press_time = time.time()

    def on_release(key):
        nonlocal is_recording, key_press_time, program_exit, recording_started

        if key == keyboard.KeyCode.from_char('1'):
            is_recording = False
            if time.time() - key_press_time < 0.5:  # 0.5초 미만으로 눌렀다 뗐을 경우
                program_exit = True
                print("프로그램을 종료합니다.")
            else:
                print("녹음 종료")
            return False  # 리스너 중지

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    while listener.running:
        if is_recording:
            if not recording_started and time.time() - key_press_time >= 0.5:
                print("녹음 시작...")
                recording_started = True
            data = stream.read(CHUNK)
            frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    if program_exit:
        return None

    # WAV 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        wf = wave.open(tmp_file.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return tmp_file.name

def speech_to_text(audio_file):
    with open(audio_file, "rb") as file:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=file, language="ko")
    return transcript.text

def get_chatgpt_response(prompt):
    try:
        response = client.chat.completions.create(
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

def play_audio(data, samplerate):
    p = pyaudio.PyAudio()
    
    # float32 데이터를 int16으로 변환
    data_int16 = (data * 32767).astype(np.int16)
    
    stream = p.open(format=pyaudio.paInt16,
                    channels=CHANNELS,
                    rate=samplerate,
                    output=True)

    # 데이터를 청크 단위로 스트림에 쓰기
    for i in range(0, len(data_int16), CHUNK):
        chunk = data_int16[i:i+CHUNK]
        stream.write(chunk.tobytes())

    stream.stop_stream()
    stream.close()
    p.terminate()

def adjust_speed(data, speed):
    # 리샘플링을 통한 속도 조절
    length = len(data)
    new_length = int(length / speed)
    return np.interp(np.linspace(0, length, new_length), np.arange(length), data)


def text_to_speech(text, speed=1.0):
    tmp_file_name = "./output.wav"

    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text,
    )

    response.stream_to_file(tmp_file_name)

    # 오디오 파일 열기 및 속도 조절
    data, samplerate = sf.read(tmp_file_name)
    
    # 속도 조절
    if speed != 1.0:
        data = adjust_speed(data, speed)

    # 조절된 오디오 재생
    play_audio(data, samplerate)

    # 임시 파일 삭제
    os.unlink(tmp_file_name)
        
def main():
    while True:
        print("음식 이름을 말씀해주세요. (종료하려면 '종료'라고 말씀하세요)")

        while True:
            audio_file = record_audio()
            
            if audio_file is None:  # 프로그램 종료 신호
                return
            
            user_input = speech_to_text(audio_file)
            os.unlink(audio_file)  # 임시 파일 삭제

            print(f"인식된 텍스트: {user_input}")

            flush_input()  # 입력 버퍼를 비웁니다

            
            confirmation = input("인식된 텍스트가 맞습니까? (y/n): ").lower()
            if confirmation == 'y':
                break
            else:
                print("다시 녹음해 주세요.")

        prompt = f"{user_input}에 대해 알려주세요."
        response = get_chatgpt_response(prompt)
        print("\nChatGPT 응답:")
        print(response)
        print("\n음성으로 응답을 들려드리겠습니다.")
        text_to_speech(response, 1.5)

if __name__ == "__main__":
    main()