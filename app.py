import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 페이지 설정 (브라우저 탭 제목 및 넓은 레이아웃)
st.set_page_config(page_title="지식 저장소", layout="wide")

# TikTok 개발자 사이트 검증 메타 태그 추가
st.markdown("""
<script>
    var meta = document.createElement('meta');
    meta.name = 'tiktok-developers-site-verification';
    meta.content = 'pAp70tp7LiyNFwnXILKsaEgYxW1nj1w0';
    document.head.appendChild(meta);
</script>
""", unsafe_allow_html=True)

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
    try:
        return spreadsheet.worksheet(SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        # 워크시트가 없으면 생성
        worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=4)
        # 헤더 추가
        worksheet.append_row(["날짜", "제목", "내용", "카테고리"])
        return worksheet

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

# 관리자 인증 (사이드바)
with st.sidebar:
    st.write("**🔐 관리자 인증**")
    admin_password = st.text_input("관리자 비밀번호", type="password", placeholder="비밀번호 입력")
    
    # 비밀번호 확인 (환경변수 또는 st.secrets에서 관리)
    correct_password = st.secrets.get("admin_password", "admin1234")
    
    st.session_state.is_admin = admin_password == correct_password
    
    if st.session_state.is_admin:
        st.success("✅ 관리자 인증됨")
    elif admin_password:
        st.error("❌ 비밀번호가 틀렸습니다")

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
                
                # 저장 확인을 위해 데이터 다시 로드
                updated_data = load_data()
                if not updated_data.empty and any(updated_data["날짜"] == new_row[0]):
                    st.success(f"'{title}' 제목으로 저장되었습니다!")
                    st.balloons() # 성공 축하 효과
                    st.rerun()
                else:
                    st.error("저장되었지만 데이터 확인에 실패했습니다. 시트 권한을 확인하세요.")
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
    sorted_data = data.sort_values("날짜", ascending=False).reset_index(drop=True)
    
    # 날짜 형식 변환 함수
    def format_date(date_str):
        try:
            dt = datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%y%m%d-%H%M")
        except:
            return str(date_str)
    
    # 테이블 헤더
    if st.session_state.is_admin:
        header_col1, header_col2, header_col3, header_col4, header_col5 = st.columns([0.5, 2, 3, 2, 1.2])
        with header_col1:
            st.write("**☑️**")
    else:
        header_col1, header_col2, header_col3, header_col4 = st.columns([2, 3, 2, 1.2])
    
    with header_col2 if st.session_state.is_admin else header_col1:
        st.write("**제목**")
    with header_col3 if st.session_state.is_admin else header_col2:
        st.write("**내용**")
    with header_col4 if st.session_state.is_admin else header_col3:
        st.write("**카테고리**")
    with header_col5 if st.session_state.is_admin else header_col4:
        st.write("**날짜**")
    
    st.divider()
    
    # 각 행에 체크박스 추가
    for idx, row in sorted_data.iterrows():
        if st.session_state.is_admin:
            col1, col2, col3, col4, col5 = st.columns([0.5, 2, 3, 2, 1.2])
            
            with col1:
                # 날짜를 key로 사용하여 안전하게 관리
                checkbox_key = f"select_{row['날짜']}"
                st.checkbox("", value=False, key=checkbox_key)
        else:
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1.2])
        
        with col2 if st.session_state.is_admin else col1:
            st.write(row["제목"])
        with col3 if st.session_state.is_admin else col2:
            # 내용이 길면 일부만 표시
            content_preview = row["내용"][:50] + "..." if len(str(row["내용"])) > 50 else row["내용"]
            st.write(content_preview)
        with col4 if st.session_state.is_admin else col3:
            st.write(row["카테고리"])
        with col5 if st.session_state.is_admin else col4:
            st.write(format_date(row["날짜"]))
    
    st.divider()
    
    # 관리자만 삭제 기능 표시
    if st.session_state.is_admin:
        # 삭제 버튼 레이아웃
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔴 선택 삭제", use_container_width=True):
                # 선택된 항목 찾기 (select_{date} 형식의 key)
                selected_dates = []
                for key, value in st.session_state.items():
                    if key.startswith("select_") and value:
                        date_str = key.replace("select_", "")
                        selected_dates.append(date_str)
                
                if selected_dates:
                    try:
                        worksheet = get_worksheet()
                        
                        # 전체 데이터 가져오기
                        all_data = worksheet.get_all_values()
                        
                        # 역순으로 삭제하여 인덱스 오류 방지
                        for i in range(len(all_data) - 1, 0, -1):
                            if all_data[i] and str(all_data[i][0]) in [str(d) for d in selected_dates]:
                                worksheet.delete_rows(i + 1)
                        
                        st.success(f"{len(selected_dates)}개 항목이 삭제되었습니다.")
                        st.rerun()  # 화면 갱신
                    except Exception as e:
                        st.error(f"삭제 오류: {e}")
                else:
                    st.warning("삭제할 항목을 선택해주세요.")
        
        with col2:
            if st.button("🔴🔴 전체 삭제", use_container_width=True):
                if st.session_state.get("confirm_delete_all", False):
                    try:
                        worksheet = get_worksheet()
                        
                        # 전체 데이터 가져오기
                        all_data = worksheet.get_all_values()
                        
                        # 헤더를 제외한 모든 행 삭제 (역순으로 삭제하여 인덱스 오류 방지)
                        if len(all_data) > 1:  # 헤더가 있으므로 1보다 크면 데이터가 있음
                            for i in range(len(all_data) - 1, 0, -1):
                                worksheet.delete_rows(i + 1)
                        
                        st.success("✅ 모든 기록이 삭제되었습니다.")
                        st.session_state.confirm_delete_all = False
                        st.rerun()  # 화면 갱신
                    except Exception as e:
                        st.error(f"삭제 오류: {e}")
                else:
                    st.session_state.confirm_delete_all = True
                    st.rerun()
        
        # 확인 메시지
        if st.session_state.get("confirm_delete_all", False):
            st.warning("⚠️ 정말로 모든 기록을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다. 다시 클릭해주세요.")
    else:
        st.info("📝 기록을 삭제하려면 사이드바에서 관리자 인증을 해주세요.")
else:
    st.write("아직 저장된 기록이 없습니다. 첫 글을 남겨보세요!")