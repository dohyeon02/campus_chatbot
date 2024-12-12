import streamlit as st
from streamlit_chat import message  # streamlit_chat 가져오기
import random
from datetime import datetime
import re  # 정규식 모듈 추가

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_interaction" not in st.session_state:
    st.session_state.last_interaction = datetime.now()

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
    "백주년기념관": "분수대 왼쪽",
    "신학관": "스미스관 맞은편",
    "스미스관": "사무엘관 맞은편",
    "사무엘관": "이종순 기념홀 앞쪽",
    "에덴관": "이종순 기념홀 왼쪽",
    "여학생 생활관": "이종순 기념홀 왼쪽",
    "인성교육관": "에덴관 왼쪽",
    "브니엘관": "살렘관 왼쪽",
    "대학교회": "이종순 기념홀 뒤쪽",
    "살렘관": "생활관 식당 뒤쪽",
    "생활관 식당": "시온관 왼쪽",
    "시온관": "음악관 위쪽",
    "남학생 생활관": "음악관 왼쪽",
    "음악관": "100주년 기념관 위쪽",
    "대강당": "분수대 맞은편",
    "선교70주년 기념관": "분수대 맞은편",
    "제1실습관": "70주년 기념관 뒤쪽",
    "디자인관": "제 1실습관 오른쪽",
    "실험동물실": "디자인관 뒤쪽",
    "온실": "디자인관 오른쪽",
    "아트엔 디자인관": "70주년 기념관 오른쪽",
    "도서관": "100주년 기념관 오른쪽",
    "에스라관": "제1과학관 맞은편",
    "제1과학관": "온실 앞쪽",
    "제2과학관": "에스라관 오른쪽",
    "평생교육원": "후문 어린이집 반대편",
    "제3과학관": "평생교육원 맞은편",
    "뉴스타트센터": "종합경기장 오른쪽",
    "다니엘관": "학생회관 오른쪽",
    "요한관": "학생회관 오른쪽",
    "박물관": "학생회관 오른쪽",
    "바울관": "중앙도서관 맞은편",
    "학생회관": "바울관 뒤쪽",
    "대학 일자리본부": "바울관 뒤쪽",
    "체육관": "종합경기장 왼쪽",
    "종합경기장": "학생회관 뒤쪽",
    "이종순 기념홀": "생활관 식당 왼쪽",
    "평생교육원": "후문 기준 왼쪽",
}


# 주변 데이터 정보
info_data =  {
    "식당": [
        "후문 도보 5분 거리에 위치한 식당입니다.",
        "쇼쿠오쿠\n- 운영시간: 오전 10시 30분 ~ 오후 8시 30분",
        "맛차이나\n- 운영시간: 오전 10시 ~ 오후 7시",
        "토리코코로\n- 운영시간: 오전 10시 ~ 오후 9시",
    ],
    "카페": [
        "후문 도보 5분 거리에 위치한 카페입니다.",
        "카페 공강\n- 운영시간: 오전 10시 ~ 오후 10시 (토요일 휴무)",
        "라비다커피 삼육대점\n- 운영시간: 월~금 오전 8시 30분 ~ 오후 9시, 일요일 오전 11시 ~ 오후 6시 (토요일 휴무)",
        "이디야커피 삼육대점\n- 운영시간: 오전 8시 ~ 오후 9시",
    ],
    "병원": [
        "삼육서울병원\n- 운영시간: 일~목요일 오전 9시 ~ 오후 5시\n금요일 오전 9시 ~ 오후 12시 (토요일 휴진)",
        "위치: 삼육대학교에서 차량으로 약 10분 거리",
    ],
    "pc방": [
        "스타일 PC방\n- 운영시간: 24시간\n- 위치: 삼육대학교 후문 도보 약 7분 거리",
        "아이비스 PC방\n- 운영시간: 24시간\n- 위치: 삼육대학교 후문 도보 약 10분 거리",
    ],
    "셔틀": [
        "학교 >> 석계역",
        "월요일 ~ 목요일:\n12시: 00분, 25분, 50분\n13시: 15분, 40분\n14시: 05분, 30분\n15시: 00분, 20분, 40분\n16시: 00분, 20분, 40분\n17시: 00분, 20분, 40분\n18시: 00분, 15분",
        "금요일:\n12시: 00분, 25분, 50분\n13시: 15분, 40분\n14시: 05분, 30분\n15시: 00분, 20분, 30분",
        "이 내용 이외에 더 이상의 정보가 없습니다.",
    ],
    "도서관 운영시간": [
        "지하 1층\n- 월~목: 오전 9시 ~ 오후 5시\n- 금: 오전 9시 ~ 오후 3시",
        "1층\n- 월~목: 오전 8시 ~ 오후 11시\n- 금: 오전 8시 ~ 오후 5시\n- 토: 오전 9시 ~ 오후 11시",
    ],
}

# 시간대에 맞는 랜덤 인사말 반환
def get_random_greeting():
    now = datetime.now()
    if 5 <= now.hour < 12:
        return random.choice(greetings["morning"])
    elif 12 <= now.hour < 15:
        return random.choice(greetings["lunch"])
    elif 15 <= now.hour < 18:
        return random.choice(greetings["afternoon"])
    elif 18 <= now.hour < 22:
        return random.choice(greetings["evening"])
    else:
        return random.choice(greetings["night"])

# 응답 생성 함수
def generate_response(user_input):
    user_input_no_space = user_input.replace(" ", "")

    # info_data 매칭 (우선 처리)
    for category, details in info_data.items():
        category_no_space = category.replace(" ", "")
        if re.search(category_no_space, user_input_no_space):
            # Markdown 포맷으로 리스트 정리
            return ["\n".join([f"- {line}" if i != 0 else line for i, line in enumerate(details)])]

    # locations 매칭
    for location, description in locations.items():
        location_no_space = location.replace(" ", "")
        if re.search(location_no_space, user_input_no_space):
            return [f"**{location} 위치는 {description}입니다.**"]

    # 기본 응답
    return ["질문을 이해하지 못했어요. 다시 입력해 주세요!"]

# Streamlit 앱
st.title("삼육대 무물보 챗봇")

# 사용자 입력
user_input = st.text_input("궁금한 점을 입력하세요:", "").strip()

if user_input:
    st.session_state.last_interaction = datetime.now()

    st.session_state.messages.append({"role": "user", "text": user_input})

    if "안녕" in user_input:
        response = [get_random_greeting()]
    else:
        response = generate_response(user_input)

    st.session_state.messages.append({"role": "bot", "text": "\n".join(response)})

# 메시지 표시 (streamlit_chat 활용)
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        message(msg["text"], is_user=True, key=f"user_{idx}")
    else:
        message(msg["text"], key=f"bot_{idx}")
