import streamlit as st
from streamlit_chat import message  # streamlit_chat 가져오기
import random
from datetime import datetime
import pytz  # 시간대 처리를 위한 라이브러리
import re  # 정규식 모듈 추가
import folium  # 지도 생성 라이브러리
from streamlit_folium import st_folium

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_interaction" not in st.session_state:
    st.session_state.last_interaction = datetime.now()
if "last_input" not in st.session_state:  # 마지막 입력 추적
    st.session_state.last_input = ""

# 시간대별 인사말
greetings = {
    "morning": [
        "좋은 아침이에요! 삼육대학교 챗봇입니다. 어떤 정보를 도와드릴까요?",
        "안녕하세요! 상쾌한 아침입니다. 학사 일정이나 캠퍼스 시설 정보가 필요하신가요?",
        "좋은 하루의 시작입니다! 셔틀버스 시간표나 맛집 정보를 찾으시나요?",
    ],
    "lunch": [
        "안녕하세요, 삼육대학교 챗봇입니다. 맛있는 점심 드시고 계신가요?",
        "점심시간이에요! 캠퍼스 주변 식당 정보가 필요하신가요?",
        "오늘 점심 메뉴는 정하셨나요? 맛집 추천이 필요하면 말씀해 주세요!",
    ],
    "afternoon": [
        "좋은 오후입니다! 삼육대학교 챗봇이에요. 무엇을 도와드릴까요?",
        "안녕하세요, 남은 하루도 힘내세요! 도서관 이용 시간이나 셔틀 정보가 필요하신가요?",
        "오후도 활기차게! 필요한 정보를 빠르게 찾아드릴게요.",
    ],
    "evening": [
        "좋은 저녁이에요! 삼육대학교 챗봇입니다. 학업 관련 질문이나 캠퍼스 시설 정보를 도와드릴까요?",
        "저녁시간입니다! 오늘 하루 잘 마무리하고 계신가요? 필요한 정보를 알려드릴게요.",
        "안녕하세요! 셔틀버스 막차 시간이나 도서관 운영시간이 궁금하신가요?",
    ],
    "night": [
        "늦은 시간에도 찾아주셔서 감사합니다! 삼육대학교 챗봇입니다. 필요한 정보가 있으시면 말씀해주세요.",
        "안녕하세요! 지금은 늦은 시간이니 셔틀버스 운행 시간은 내일 다시 확인해 주세요.",
        "밤늦게도 제가 도움을 드릴게요. 무엇이든 물어보세요!",
    ],
}

# 장소 정보 정의
locations = {
    "백주년기념관": ("정문에서 가까운 위치에 있습니다.", 37.6430, 127.1046),
    "100주년기념관": ("정문에서 가까운 위치에 있습니다.", 37.6430, 127.1046),
    "100주년 기념관": ("정문에서 가까운 위치에 있습니다.", 37.6430, 127.1046),
    "도서관": ("100주년 기념관 옆에 위치해 있습니다.", 37.6427, 127.1048),
    "신학관": ("백주년기념관 근처에 있습니다.", 37.6429, 127.1043),
    "스미스관": ("사무엘관 근처에 위치해 있습니다.", 37.6432, 127.1040),
    "사무엘관": ("교회 맞은편에 위치해 있습니다.", 37.6436, 127.1036),
    "에덴관": ("이종순 기념홀 인근에 위치해 있습니다.", 37.6439, 127.1028),
    "여학생 생활관": ("에덴관과 같은 건물입니다.", 37.6439, 127.1028),
    "인성교육관": ("브니엘관과 연결된 건물입니다.", 37.6445, 127.1023),
    "브니엘관": ("에덴관 뒤쪽에 위치해 있습니다.", 37.6447, 127.1020),
    "교회": ("캠퍼스 서쪽에 깊숙하게 위치해 있습니다.", 37.6452, 127.1016),
    "살렘관": ("생활관 식당 뒤쪽에 위치해 있습니다.", 37.6457, 127.1013),
    "생활관 식당": ("이종순 기념홀 근처에 위치해 있습니다.", 37.6449, 127.1020),
    "시온관": ("남학생 생활관으로도 불립니다.", 37.6462, 127.1009),
    "음악관": ("백주년기념관 위쪽에 위치해 있습니다.", 37.6456, 127.1024),
    "대강당": ("분수대 맞은편에 위치해 있습니다.", 37.6431, 127.1044),
    "선교70주년 기념관": ("분수대 옆쪽에 위치합니다.", 37.6429, 127.1045),
    "제1실습관": ("70주년 기념관 뒤편에 위치합니다.", 37.6428, 127.1047),
    "디자인관": ("제1실습관 오른쪽에 있습니다.", 37.6427, 127.1049),
    "온실": ("디자인관 오른쪽에 위치해 있습니다.", 37.6425, 127.1052),
    "에스라관": ("제1과학관 근처에 있습니다.", 37.6428, 127.1050),
    "제1과학관": ("온실 근처에 위치해 있습니다.", 37.6427, 127.1052),
    "제2과학관": ("에스라관 오른쪽에 위치해 있습니다.", 37.6429, 127.1053),
    "평생교육원": ("후문 근처에 위치해 있습니다.", 37.6426, 127.1054),
    "제3과학관": ("평생교육원 맞은편에 위치합니다.", 37.6425, 127.1055),
    "뉴스타트센터": ("종합경기장 오른쪽에 위치해 있습니다.", 37.6426, 127.1057),
    "다니엘관": ("학생회관 오른쪽에 있습니다.", 37.6433, 127.1054),
    "요한관": ("학생회관 근처에 있습니다.", 37.6434, 127.1053),
    "박물관": ("학생회관 근처에 위치해 있습니다.", 37.6435, 127.1052),
    "바울관": ("도서관 맞은편에 있습니다.", 37.6437, 127.1050),
    "학생회관": ("바울관 뒤쪽에 위치해 있습니다.", 37.6438, 127.1048),
    "체육관": ("종합경기장 근처에 있습니다.", 37.6431, 127.1056),
    "종합경기장": ("학생회관 뒤편에 위치합니다.", 37.6430, 127.1054),
    "이종순 기념홀": ("사무엘관 인근에 있습니다.", 37.6435, 127.1027),
    "주차장": ("다양한곳에 위치하고 있습니다. 신학관 주차장이 주차 공간이 널널합니다. ", 37.6431, 127.1056),
}


# 주변 데이터 정보
info_data = {
    # 기존 데이터 유지
    "식당": [
        "후문 도보 5분 거리에 위치한 식당입니다.",
        "쇼쿠오쿠\n- 운영시간: 오전 10시 30분 ~ 오후 8시 30분\n- 주소: 서울특별시 노원구 화랑로 815\n",
        "맛차이나\n- 운영시간: 오전 10시 ~ 오후 7시\n- 주소: 서울특별시 노원구 화랑로 817\n",
        "토리코코로\n- 운영시간: 오전 10시 ~ 오후 9시\n- 주소: 서울특별시 노원구 화랑로 819\n",
        "아마도식당\n- 운영시간: 오전 11시 ~ 오후 9시\n- 주소: 서울특별시 노원구 화랑로 831\n",
        "삼육정육식당\n- 운영시간: 오전 11시 ~ 오후 10시\n- 주소: 서울특별시 노원구 화랑로 833\n",
        "뚝배기집\n- 운영시간: 오전 10시 ~ 오후 9시\n- 주소: 서울특별시 노원구 화랑로 835\n",
        "밥은먹고다니냐?\n- 운영시간: 오전 11시 30분 ~ 오후 9시\n- 주소: 서울특별시 노원구 화랑로 837\n",
        "고기천국 삼육대점\n- 운영시간: 오전 11시 ~ 오후 11시\n- 주소: 서울특별시 노원구 화랑로 839\n",
        "참치마을\n- 운영시간: 오전 11시 ~ 오후 10시\n- 주소: 서울특별시 노원구 화랑로 841\n",
        "청년다방 삼육대점\n- 운영시간: 오전 10시 ~ 오후 10시\n- 주소: 서울특별시 노원구 화랑로 843\n",
        "마라탕짱\n- 운영시간: 오전 11시 ~ 오후 10시\n- 주소: 서울특별시 노원구 화랑로 845\n",
    ],
    "대중교통": [
        "삼육대학교로 오는 대중교통 안내입니다.",
        "**지하철**\n- 6호선 화랑대역 2번 출구 하차 후 도보 약 10분 소요\n- 1호선 석계역 하차 후 셔틀버스 이용 (출발 시간표는 '셔틀' 항목 참고)\n",
        "**버스**\n- 정류장: 삼육대학교 입구 또는 삼육대 정문\n- 일반버스: 105번, 146번, 202번\n- 마을버스: 노원10번, 노원12번\n",
        "**자가용**\n- 네비게이션 주소: 서울특별시 노원구 화랑로 815 삼육대학교\n- 주차장: 교내 주차장 이용 가능 (유료)\n",
    ],
    "문구점": [
        "후문 도보 10분 거리에 위치한 문구점입니다.",
        "다이소 삼육대점\n- 운영시간: 오전 9시 ~ 오후 10시\n- 주소: 서울특별시 노원구 화랑로 847\n",
        "행복문구\n- 운영시간: 오전 9시 ~ 오후 8시\n- 주소: 서울특별시 노원구 화랑로 849\n",
        "화랑문구\n- 운영시간: 오전 9시 ~ 오후 9시\n- 주소: 서울특별시 노원구 화랑로 851\n",
    ],
    "카페": [
        "후문 도보 5분 거리에 위치한 카페입니다.",
        "카페 공강\n- 운영시간: 오전 10시 ~ 오후 10시 (토요일 휴무)\n- 주소: 서울특별시 노원구 화랑로 821\n",
        "라비다커피 삼육대점\n- 운영시간: 월~금 오전 8시 30분 ~ 오후 9시\n  일요일 오전 11시 ~ 오후 6시 (토요일 휴무)\n- 주소: 서울특별시 노원구 화랑로 823\n",
        "이디야커피 삼육대점\n- 운영시간: 오전 8시 ~ 오후 9시\n- 주소: 서울특별시 노원구 화랑로 825\n",
        "커피빈 삼육대점\n- 운영시간: 오전 8시 ~ 오후 9시\n- 주소: 서울특별시 노원구 화랑로 855\n",
        "아이스팩토리\n- 운영시간: 오전 9시 ~ 오후 10시\n- 주소: 서울특별시 노원구 화랑로 857\n",
        "빈브라더스 삼육대점\n- 운영시간: 오전 10시 ~ 오후 10시\n- 주소: 서울특별시 노원구 화랑로 859\n",
        "탐앤탐스 삼육대점\n- 운영시간: 오전 9시 ~ 오후 11시\n- 주소: 서울특별시 노원구 화랑로 861\n",
    ],
    "셔틀": [
        "학교 >> 석계역\n",
        "월요일 ~ 목요일:",
        "12시: 00분, 25분, 50분\n13시: 15분, 40분\n14시: 05분, 30분\n"
        "15시: 00분, 20분, 40분\n16시: 00분, 20분, 40분\n17시: 00분, 20분, 40분\n"
        "18시: 00분, 15분\n",
        "금요일: ",
        "12시: 00분, 25분, 50분\n13시: 15분, 40분\n14시: 05분, 30분\n15시: 00분, 20분, 30분\n",
        "이 내용 이외에 더 이상의 정보가 없습니다.",
    ],
    "도서관 운영시간": [
        "지하 1층\n- 월~목: 오전 9시 ~ 오후 5시\n- 금: 오전 9시 ~ 오후 3시\n",
        "1층\n- 월~목: 오전 8시 ~ 오후 11시\n- 금: 오전 8시 ~ 오후 5시\n- 토: 오전 9시 ~ 오후 11시\n",
        "2층\n- 월~목: 오전 8시 ~ 오후 11시\n- 금: 오전 8시 ~ 오후 5시\n- 토: 오전 9시 ~ 오후 11시\n",
        "3층\n- 월~목: 오전 8시 ~ 오후 11시\n- 금: 오전 8시 ~ 오후 5시\n- 토: 오전 9시 ~ 오후 11시\n",
    ],
    "편의시설": [
        "교내에 다양한 편의시설이 있습니다.",
        "세븐일레븐 삼육대점\n- 운영시간: 24시간\n- 위치: 서울특별시 노원구 화랑로 830\n",
        "교내 서점\n- 운영시간: 월~금 오전 9시 ~ 오후 6시\n- 위치: 학생회관 1층\n",
    ],
    "체육시설": [
        "삼육대학교 내 다양한 체육시설이 있습니다.",
        "체육관\n- 위치: 종합경기장 근처\n- 이용시간: 오전 6시 ~ 오후 10시\n",
        "야외운동장\n- 위치: 종합경기장\n- 개방시간: 상시 이용 가능\n",
    ],
}

# get_random_greeting 함수 (수정된 부분만)
def get_random_greeting(user_input):
    user_input_no_space = user_input.replace(" ", "").lower()  # 입력을 소문자로 변환 및 공백 제거
    now = datetime.now(pytz.timezone('Asia/Seoul'))

    if 5 <= now.hour < 12:
        return random.choice(greetings["morning"])
    elif 12 <= now.hour < 15:
        return random.choice(greetings["lunch"])
    elif 15 <= now.hour < 18:
        return random.choice(greetings["afternoon"])
    elif 18 <= now.hour < 22:
        return random.choice(greetings["evening"])
    else:
        # info_data 매칭 (부분 일치 허용)
        for category, details in info_data.items():
            if category.lower() in user_input_no_space:
                return "\n".join(details)

        # locations 매칭 (부분 일치 허용)
        for location, (description, lat, lon) in locations.items():
            if location.lower() in user_input_no_space:
                return f"**{location} 위치는 {description}입니다.**"

        return random.choice(greetings["night"])

# 지도 생성 함수
def generate_map(location_name, latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=17)
    return m

# 응답 생성 함수 수정
def generate_response(user_input):
    user_input_no_space = user_input.replace(" ", "").lower()  # 입력 정리

    # 1. "운영시간"이 입력에 포함된 경우 info_data의 특정 항목 반환
    if "운영시간" in user_input_no_space:
        if "map" in st.session_state:  # 지도 제거
            del st.session_state["map"]
        for category, details in info_data.items():
            if category.replace(" ", "").lower() in user_input_no_space:
                return "\n".join(details), None  # 운영시간 반환

    # 2. 다른 info_data 항목 확인 (일반 키워드 매칭)
    for category, details in info_data.items():
        if category.replace(" ", "").lower() in user_input_no_space:
            if "map" in st.session_state:  # 지도 제거
                del st.session_state["map"]
            return "\n".join(details), None  # 일반 정보 반환

    # 3. 위치 정보 확인 (locations)
    for location, (description, lat, lon) in locations.items():
        if location.replace(" ", "").lower() in user_input_no_space:
            # 지도 객체를 생성하고 세션 상태에 저장
            map_obj = generate_map(location, lat, lon)
            st.session_state["map"] = map_obj
            return f"**{location} 위치는 {description}입니다.**", map_obj

    # 4. 기본 응답
    if "map" in st.session_state:  # 지도 제거
        del st.session_state["map"]
    return "질문을 이해하지 못했어요. 다시 입력해 주세요!", None

# 키워드 추출 함수
def extract_keyword(user_input):
    for location in locations.keys():
        if location in user_input:
            return location
    for category in info_data.keys():
        if category in user_input:
            return category
    return None



# 사용자 입력 처리
st.title("삼육대 캠퍼스 관련 무물보 챗봇")

# 사용자 입력값을 저장
user_input = st.text_input("'안녕'으로 반갑게 인사해주세요! 질문하실때는 정확한 위치 포함해서 질문해주세요!", placeholder="\n 예시: 체육관 위치가 어디에요?").strip()

if user_input and user_input != st.session_state.last_input:  # 중복 입력 방지
    st.session_state.last_input = user_input  # 마지막 입력값 저장
    st.session_state.messages.append({"role": "user", "text": user_input})  # 사용자 메시지 추가

    # 봇 응답 생성
    if "안녕" in user_input:
        response_text = get_random_greeting(user_input)
        st.session_state.messages.append({"role": "bot", "text": response_text})
    else:
        response_text, map_obj = generate_response(user_input)
        st.session_state.messages.append({"role": "bot", "text": response_text})

# 메시지 출력
for idx, msg in enumerate(st.session_state.messages[::-1]):
    if msg["role"] == "user":
        message(msg["text"], is_user=True, key=f"user_{idx}")
    else:
        message(msg["text"], key=f"bot_{idx}")

# 세션 상태에 저장된 지도 객체를 표시
if "map" in st.session_state:
    st_folium(st.session_state["map"], width=700, height=500)
