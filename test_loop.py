import time
from datetime import datetime, timedelta

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

while True:
    action = input("동작을 선택하세요 (1: 버튼 누르기, 2: 남은 시간 확인, q: 종료): ")
    if action == '1':
        box.toggle()
    elif action == '2':
        box.display_remaining_time()
    elif action.lower() == 'q':
        break
    else:
        print("잘못된 입력입니다. 다시 시도해주세요.")