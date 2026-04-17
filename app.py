import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 페이지 설정 (브라우저 탭 제목 및 넓은 레이아웃)
st.set_page_config(page_title="지식 저장소", layout="wide")

# Google Sheets API 연동
SHEET_ID = "1Skjg1T9KSeXsn15RJ9iQBgdZM0qTD1gS9CzfuAb1FWc"
SHEET_NAME = "지식저장소"

@st.cache_resource
def get_gsheet_client():
    credentials_dict = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", 
             "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scopes=scope)
    client = gspread.authorize(credentials)
    return client

def get_worksheet():
    client = get_gsheet_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    return spreadsheet.worksheet(SHEET_NAME)

# 데이터 로드 함수
def load_data():
    try:
        worksheet = get_worksheet()
        data = worksheet.get_all_records()
        if data:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame(columns=["날짜", "제목", "내용", "카테고리"])
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
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
            try:
                # 제목이 없을 경우 자동 생성 로직
                if not title.strip():
                    now_str = datetime.now().strftime("%m월 %d일 %H:%M 메모")
                    title = f"📝 {now_str}"
                
                worksheet = get_worksheet()
                new_row = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    title,
                    content,
                    category
                ]
                worksheet.append_row(new_row)
                
                st.success(f"'{title}' 제목으로 저장되었습니다!")
                st.balloons() # 성공 축하 효과
                st.rerun()
            except Exception as e:
                st.error(f"저장 오류: {e}")
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
            try:
                # 선택한 '날짜'를 기준으로 데이터 삭제
                selected_date = selected_option.split(" | ")[0]
                worksheet = get_worksheet()
                
                # 전체 데이터 가져오기
                all_data = worksheet.get_all_values()
                
                # 해당 행 찾아 삭제
                for i, row in enumerate(all_data):
                    if row and row[0] == selected_date:  # 날짜 열 확인
                        worksheet.delete_rows(i + 1)  # Google Sheets의 행 번호는 1부터 시작
                        break
                
                st.success(f"항목이 삭제되었습니다.")
                st.rerun()  # 화면 갱신
            except Exception as e:
                st.error(f"삭제 오류: {e}")
else:
    st.write("아직 저장된 기록이 없습니다. 첫 글을 남겨보세요!")