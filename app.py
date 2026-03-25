import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장 파일명
DB_FILE = "data.csv"

# 페이지 설정
st.set_page_config(page_title="지식 저장소", layout="wide")

# 데이터 로드 함수 (파일이 없으면 새로 생성)
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["날짜", "제목", "내용", "카테고리"])

st.title("📝 심플 지식 저장소")
st.info("회사나 집, 핸드폰 어디서든 접속해서 메모를 남기세요.")

# 입력 폼
with st.form("input_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("📌 제목", placeholder="오늘의 주제를 적어주세요")
    with col2:
        category = st.selectbox("📂 카테고리", ["일반", "개발", "주식", "여행", "기타"])
    
    content = st.text_area("✍️ 내용", placeholder="나중에 기억해야 할 내용을 적어주세요", height=200)
    
    submitted = st.form_submit_button("💾 저장하기", use_container_width=True)

    if submitted:
        if title and content:
            df = load_data()
            new_row = {
                "날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "제목": title,
                "내용": content,
                "카테고리": category
            }
            # 데이터 추가 후 저장
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("데이터가 안전하게 저장되었습니다!")
            st.balloons() # 저장 성공 시 축하 효과
        else:
            st.error("제목과 내용을 모두 입력해주세요.")

st.divider()

# 저장된 목록 보기
st.subheader("📜 저장된 기록들")
data = load_data()
if not data.empty:
    # 최신순 정렬 후 출력
    st.dataframe(data.sort_values("날짜", ascending=False), use_container_width=True)
else:
    st.write("아직 저장된 기록이 없습니다. 첫 글을 남겨보세요!")