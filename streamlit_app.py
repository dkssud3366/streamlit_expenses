import streamlit as st
from utils import connect_redis
import streamlit_authenticator as stauth

# 반드시 첫 번째로 실행
st.set_page_config(page_title="收支表", layout="centered")

rds = connect_redis()

@st.cache_data
def get_user_data():
    try:
        pipe = rds.pipeline()
        keys_ = rds.keys("usernames:*")
        
        if keys_:
            for i in keys_:
                pipe.hgetall(i)
            usernames = pipe.execute()
        else:
            # Redis에 데이터가 없을 경우 기본값
            usernames = [{"username": "admin", "password": "0313", "email": "abc@gmail.com"}]
        
        config = {
            "credentials": {
                "usernames": {
                    user['username']: {
                        "name": user['username'],
                        "password": user['password'],  # 실제 운영 시 해싱 필요
                        "email": user['email'],
                    } for user in usernames
                },
            },
            "cookie": {
                "expiry_days": 30,
                "key": "erp_streamlit",
                "name": "erp_streamlit_expenses",
            }
        }
        return config
    except Exception as e:
        st.error(f"사용자 데이터 로드 실패: {e}")
        return None

config = get_user_data()

if config is None:
    st.stop()

# 레이아웃 구성
main_box = st.container()
submain = main_box.container()

# 디버그용 (운영 시 제거 권장)
st.sidebar.write(st.session_state)

# 페이지 네비게이션 설정
show_exp = st.Page("sidebar/show_exp.py", title="列表")
todo = st.Page("sidebar/todo.py", title="日程管理")
pg = st.navigation([show_exp,todo])

# 로그인 폼
with submain:
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

    fields = {
        "Form name": "로그인",
        "Username": "사용자 이름",
        "Password": "비밀번호",
        "Login": "로그인"
    }

    try:
        authenticator.login(location="main", fields=fields)
    except Exception as e:
        st.error(f"로그인 오류: {e}")

# 인증 상태에 따른 처리
if st.session_state.get("authentication_status"):
    with st.sidebar:
        authenticator.logout("로그아웃", "main")
    pg.run()
elif st.session_state.get("authentication_status") is False:
    submain.error("아이디 또는 비밀번호가 올바르지 않습니다")
elif st.session_state.get("authentication_status") is None:
    submain.warning("로그인 아이디와 비밀번호를 입력하세요")