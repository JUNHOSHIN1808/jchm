# jchm/control.py
from PIL import Image
import math, os, urllib.request, random
from IPython.display import display

# ─────────────────────────────
# 전역 상태
# ─────────────────────────────
state = {
    'x': 250.0,
    'y': 330.0,
    'heading': -90.0,
    'steering_front_left': 0.0,
    'steering_rear_right': 0.0
}

# 이미지 경로
car_img_url = "https://i.imgur.com/xq4bBx7.png"
front_left_wheel_url = "https://i.imgur.com/2FD5w3C.png"
rear_right_wheel_url = "https://i.imgur.com/2FD5w3C.png"

track_options = {
    "직진": "https://i.imgur.com/W9LednO.png",
    "좌회전": "https://i.imgur.com/VmqFiwp.png",
    "우회전": "https://i.imgur.com/CL75uCI.png"
}

# 이미지 로드 함수
def load_image(url, path, size=None):
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    img = Image.open(path).convert("RGBA")
    return img.resize(size) if size else img

# 이미지 초기화
car_img = load_image(car_img_url, "/content/car.png", (100, 50))
front_left_wheel_img = load_image(front_left_wheel_url, "/content/front_left.png", (20, 20))
rear_right_wheel_img = load_image(rear_right_wheel_url, "/content/rear_right.png", (20, 20))

# 트랙 초기화
track_img = Image.new("RGBA", (500, 500), (255, 255, 255, 255))
def set_track(direction=None):
    global track_img
    if direction is None:
        direction = random.choice(list(track_options.keys()))
        print(f"🎲 무작위 트랙 선택됨: {direction}")
    else:
        print(f"🔧 사용자 설정 트랙: {direction}")
    url = track_options.get(direction, track_options["직진"])
    track_img = load_image(url, "/content/track.png", (500, 500))

set_track()  # 시작 시 무작위 배경

# ─────────────────────────────
# set_motor 함수
# ─────────────────────────────
def set_motor(left, right, speed):
    global state, car_img, front_left_wheel_img, rear_right_wheel_img, track_img

    # 1. 조향 각도 저장
    state['steering_front_left'] = left * 2
    state['steering_rear_right'] = right * 2

    # 2. 이동 방향 계산 (간단화: 평균 조향각 사용)
    avg_steering = (left + right) / 2 * 2
    heading_rad = math.radians(state['heading'] + avg_steering)
    move = speed * 0.5
    dx = math.cos(heading_rad) * move
    dy = math.sin(heading_rad) * move
    state['x'] += dx
    state['y'] += dy

    # 회전
    if speed != 0:
        state['heading'] += math.sin(math.radians(avg_steering)) * move * 0.1

    # 3. 배경 이미지
    bg = track_img.copy()
    car_rot = car_img.rotate(-state['heading'], expand=True)
    car_w, car_h = car_rot.size
    cx = int(state['x'] - car_w / 2)
    cy = int(state['y'] - car_h / 2)
    bg.paste(car_rot, (cx, cy), car_rot)

    # 4. 바퀴 두 개 (좌상단 앞, 우하단 뒤) 출력
    heading_base = math.radians(state['heading'])

    # 바퀴 상대 위치 (사용자가 조정할 수 있도록 안내)
    FL_offset_fwd = 25  # 앞바퀴 앞으로 25
    FL_offset_side = -15  # 왼쪽
    RR_offset_back = -25
    RR_offset_side = 15   # 오른쪽

    # 왼쪽 앞바퀴 위치
    fl_x = int(state['x'] + math.cos(heading_base)*FL_offset_fwd + math.sin(heading_base)*FL_offset_side)
    fl_y = int(state['y'] + math.sin(heading_base)*FL_offset_fwd - math.cos(heading_base)*FL_offset_side)
    fl_rot = front_left_wheel_img.rotate(-state['steering_front_left'], expand=True)
    bw, bh = fl_rot.size
    bg.paste(fl_rot, (fl_x - bw//2, fl_y - bh//2), fl_rot)

    # 오른쪽 뒷바퀴 위치
    rr_x = int(state['x'] + math.cos(heading_base)*RR_offset_back + math.sin(heading_base)*RR_offset_side)
    rr_y = int(state['y'] + math.sin(heading_base)*RR_offset_back - math.cos(heading_base)*RR_offset_side)
    rr_rot = rear_right_wheel_img.rotate(-state['steering_rear_right'], expand=True)
    bw2, bh2 = rr_rot.size
    bg.paste(rr_rot, (rr_x - bw2//2, rr_y - bh2//2), rr_rot)

    # 5. 출력
    display(bg)
