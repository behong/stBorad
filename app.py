import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장 파일명
DB_FILE = "data.csv"

# 페이지 설정 (브라우저 탭 제목 및 넓은 레이아웃)
st.set_page_config(page_title="지식 저장소", layout="wide")

# 데이터 로드 함수 (파일이 없으면 빈 데이터프레임 반환)
def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            return pd.DataFrame(columns=["날짜", "제목", "내용", "카테고리"])
    return pd.DataFrame(columns=["날짜", "제목", "내용", "카테고리"])

st.title("📝 심플 지식 저장소")
st.info("회사나 집, 핸드폰 어디서든 접속해서 메모를 남기세요.")

# 입력 폼 (저장 시 입력창 초기화)
with st.form("input_form", clear_on_submit=True):
    # 컬럼 개수를 2개로 명시하여 버전 오류 해결
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("📌 제목", placeholder="비워두면 오늘 날짜로 자동 생성됩니다")
    with col2:
        category = st.selectbox("📂 카테고리", ["일반", "개발", "주식", "여행", "기타"])
    
    content = st.text_area("✍️ 내용", placeholder="나중에 기억해야 할 내용을 적어주세요", height=200)
    
    submitted = st.form_submit_button("💾 저장하기", use_container_width=True)

    if submitted:
        if content: # 내용은 필수
            # 제목이 없을 경우 자동 생성 로직
            if not title.strip():
                now_str = datetime.now().strftime("%m월 %d일 %H:%M 메모")
                title = f"📝 {now_str}"
            
            df = load_data()
            new_row = {
                "날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "제목": title,
                "내용": content,
                "카테고리": category
            }
            
            # 데이터 추가 및 CSV 저장
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            
            st.success(f"'{title}' 제목으로 저장되었습니다!")
            st.balloons() # 성공 축하 효과
        else:
            st.error("내용을 입력해주세요.")

st.divider()

# 저장된 목록 보기
st.subheader("📜 저장된 기록들 (최신순)")
data = load_data()

if not data.empty:
    # 날짜 기준 내림차순 정렬하여 최신글이 위로 오게 함
    sorted_data = data.sort_values("날짜", ascending=False)
    st.dataframe(sorted_data, use_container_width=True)
    
    # 삭제 기능 추가
    with st.expander("🗑️ 기록 삭제하기"):
        # 삭제할 항목을 선택하기 쉽게 '날짜 | 제목' 형식으로 표시
        delete_options = data["날짜"] + " | " + data["제목"]
        selected_option = st.selectbox("삭제할 항목을 선택하세요:", delete_options)
        
        if st.button("🔴 선택한 항목 삭제", use_container_width=True):
            # 선택한 '날짜'를 기준으로 데이터 삭제 (날짜는 유니크하다고 가정)
            selected_date = selected_option.split(" | ")[0]
            new_df = data[data["날짜"] != selected_date]
            new_df.to_csv(DB_FILE, index=False)
            st.success(f"항목이 삭제되었습니다.")
            st.rerun() # 화면 갱신
else:
    st.write("아직 저장된 기록이 없습니다. 첫 글을 남겨보세요!")