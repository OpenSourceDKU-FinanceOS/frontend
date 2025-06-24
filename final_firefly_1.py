import streamlit as st
import requests
import pandas as pd
import altair as alt
import datetime
import calendar

today = datetime.date.today()
first_day = today.replace(day=1)

# 주차 계산 함수
def get_week_range(week_num):
    base = first_day
    start = base + datetime.timedelta(days=(week_num - 1) * 7)
    end = start + datetime.timedelta(days=6)
    return start, min(end, today)


# 날짜 초기화
if "start_date" not in st.session_state:
    st.session_state.start_date = today - datetime.timedelta(days=6)
    st.session_state.end_date = today

with st.sidebar:
    st.header("나이대를 선택해주세요")
    
    age_group = st.selectbox(
        "👥 연령대 선택",
        options=["20대", "30대", "40대", "50대"],
        index=0  # 기본값은 20대
    )

# 선택된 연령대에 따라 데이터 처리
st.write(f"선택한 연령대: {age_group}")

# 예시: 연령대별 데이터 처리
if age_group == "20대":
    st.write("20대 데이터를 처리합니다.")
    # 20대에 대한 데이터 처리 로직 추가
elif age_group == "30대":
    st.write("30대 데이터를 처리합니다.")
    # 30대에 대한 데이터 처리 로직 추가
elif age_group == "40대":
    st.write("40대 데이터를 처리합니다.")
    # 40대에 대한 데이터 처리 로직 추가
elif age_group == "50대":
    st.write("50대 데이터를 처리합니다.")
    # 50대에 대한 데이터 처리 로직 추가

with st.sidebar:
    st.header("분석 조건 설정")
    user_id = st.text_input("👤 User ID", "1")
    data_source = st.selectbox("비교할 공공데이터 선택", ["이천시", "서울시"])

    st.markdown("### ⏱️ 빠른 날짜 선택")
    if st.button("📅 하루"):
        st.session_state.start_date = today
        st.session_state.end_date = today
    if st.button("📆 일주일"):
        st.session_state.start_date = today - datetime.timedelta(days=6)
        st.session_state.end_date = today
    if st.button("🗓️ 한 달"):
        st.session_state.start_date = today - datetime.timedelta(days=29)
        st.session_state.end_date = today

    month_selected = st.selectbox(
        "📆 주차를 선택할 월",
        options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        index=datetime.date.today().month - 1
    )
    year_selected = 2025  # 혹은 datetime.date.today().year 도 가능

    # 해당 월의 1일을 기준으로 설정
    first_day_of_month = datetime.date(year_selected, month_selected, 1)

    # 주차 계산 함수: 선택된 월 기준
    def get_week_range(week_num):
        start = first_day_of_month + datetime.timedelta(days=(week_num - 1) * 7)
        end = start + datetime.timedelta(days=6)
        return start, end

    # 주차 버튼 선택
    st.markdown("### 🗓️ 주차 선택")
    for i in range(1, 6):
        if st.button(f"{i}주차"):
            start, end = get_week_range(i)
            st.session_state.start_date = start
            st.session_state.end_date = end

    start_date = st.date_input("조회 시작 날짜", value=st.session_state.start_date)
    end_date = st.date_input("조회 종료 날짜", value=st.session_state.end_date)

    submit = st.button("지출 분석 시작")

FIREBASE_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZGY1NDRmYjEwNmE5ODEwN2I4Zjg0YzgyMTI2YWQ2ZGRiMjQ3ZTcyMDU0Mjk4YzQ0Y2U1YjA0MDY0NGE2MGJiZTBjZmU5NjZkOGI0NjFkZWQiLCJpYXQiOjE3NDYxNzg5MDguMjAwNDgzLCJuYmYiOjE3NDYxNzg5MDguMjAwNDg3LCJleHAiOjE3Nzc3MTQ5MDguMDQ1NzE4LCJzdWIiOiIxIiwic2NvcGVzIjpbXX0.gpQnOtMbItqQsnGN7Gg3caN39q8dNBzjw1exSVGP-rpyDy9xfyJ41qZpZ8LE2O25dxQmzuC3SwEtRnrvreugMl5pdZN3sLF2kQcY8iZajTjTTxalnbKvAvADDVmaWqtlKFk6fVUXKbsmbLlMszyTOkt8kNQLpx9JtJBeA2Eq0euFt0gGWF8wC5mugDQIAppXhoulpvZuVNxmVdcjLzFgR-vAvYdKz1ErTAKylaS-iIsr6q1uPy9HXOOdulcpuoeAooJUSUqXlnXr6-eBy9VxyLiYtDq5P83rSV8ubGr4iNvBNHnkdJCEkEpY3T4ZOaXRKRrneZVH7K68tvFuDpQlOIiQ4zZLTvTeJiyQV517B20DixO8nQ9AssauccZXXXSLbNqmVPBY1byLwp9n0y9paPtL73ABSOOjxX89ZLT4LzHAtsydZhx5fAcMErMmgqAXmxu2tO8tl1TMcglJWxVAy04QW0XtUXC_48dZ-FmEgSFtYhDtX7qGTlBuA7xmLLyA6VTMUWgJ_gggfUcR5akCZi50CswG49ErRXCVgicus2ArKyOxNHQ479pt6VXkTGHKhtIY_eFmH-Z6epWH2anA5_kJ0wIa_GUL8WjtAGNBfKznwXDabut3idOwmRYCr7AYV3ZiFI01UlpbLBDqrjuO95b6KnFbeby5amEKD85P9eg"
FIREFLY_API_URL = "http://localhost:8080"

def get_user_spending(user_id, start_date, end_date):
    url = f"{FIREFLY_API_URL}/api/v1/transactions?start={start_date.isoformat()}&end={end_date.isoformat()}&limit=1000"
    headers = {
        "Authorization": f"Bearer {FIREBASE_API_KEY}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"
    except Exception as e:
        st.error("API 요청 중 오류 발생")
        st.error(f"{e}")
        return [], 0

    if response.status_code != 200:
        st.error(f"API 요청 실패: {response.status_code}")
        return [], 0

    data = response.json()
    transactions = data.get("data", [])
    records = []
    total_spent = 0

    for tx in transactions:
        attr = tx.get("attributes", {})
        for detail in attr.get("transactions", []):
            try:
                amount = abs(float(detail["amount"]))
                total_spent += amount
                category = detail.get("category_name") or detail.get("category_id") or "미분류"
                records.append({
                    "날짜": detail.get("date", ""),
                    "금액": amount,
                    "설명": detail.get("description", ""),
                    "카테고리": category
                })
            except Exception as e:
                st.warning("항목 오류:")
                st.error(detail)
                st.error(f"에러 메시지: {e}")

    return records, total_spent

if st.button("지출 조회"):
    records, total = get_user_spending(user_id, start_date, end_date)

    st.subheader(f"총 지출: {total:.2f} 원")

    if records:
        df = pd.DataFrame(records)
        st.dataframe(df)

        df["날짜"] = pd.to_datetime(df["날짜"], errors='coerce')
        df["월"] = df["날짜"].dt.to_period("M").astype(str)
        df["요일"] = df["날짜"].dt.day_name()

        st.subheader("월별 총 지출")
        monthly_total = df.groupby("월")["금액"].sum().reset_index()
        st.dataframe(monthly_total)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV로 저장", data=csv, file_name="지출_내역.csv", mime="text/csv")

        st.subheader("요일별 지출")
        weekday_summary = df.groupby("요일")["금액"].sum()
        st.bar_chart(weekday_summary)

        st.subheader("월별 소비 추이")
        month_summary = df.groupby("월")["금액"].sum().reset_index()
        line_chart = alt.Chart(month_summary).mark_line(point=True).encode(x="월", y="금액")
        st.altair_chart(line_chart, use_container_width=True)

        st.subheader("카테고리별 비율")
        pie_data = df.groupby("카테고리")["금액"].sum().reset_index()
        pie = alt.Chart(pie_data).mark_arc().encode(
            theta="금액",
            color="카테고리",
            tooltip=["카테고리", "금액"]
        )
        st.altair_chart(pie, use_container_width=True)

        this_month = pd.to_datetime("today").month
        prev_month = this_month - 1 if this_month > 1 else 12

        st.subheader("카테고리별 전월 대비 비교")
        categories = df["카테고리"].unique()
        for category in categories:
            this_total = df[(df["카테고리"] == category) & (df["날짜"].dt.month == this_month)]["금액"].sum()
            last_total = df[(df["카테고리"] == category) & (df["날짜"].dt.month == prev_month)]["금액"].sum()
            delta = this_total - last_total
            st.subheader(f"{category} 비교")
            st.success(f"전월 {category}: {last_total:.2f} 원 → 이번 달: {this_total:.2f} 원")
            st.info(f"{'증가' if delta > 0 else '감소'}: {abs(delta):.2f} 원")

        category_mapping = {
            "식비": "식비", "커피": "커피", "생활비": "생활비", "친목비": "친목비", "교통비": "교통비", "기타":"기타",
            "식사": "식비", "한식": "식비", "외식식": "식비", "중식": "식비", "패스트푸드": "식비", "편의점": "생활비",
            "숙박": "생활비", "종합소매점": "생활비", "휴게소/대형업체": "생활비",
            "지하철": "교통비", "버스": "교통비", "택시": "교통비",
            "카페": "커피", "스타벅스": "커피", "이디야": "커피", "커피/음료": "커피",
            "회식": "친목비", "문화": "친목비", "간이주점": "친목비", "선물/완구": "친목비",
            "생활구매": "생활비", "기타용품": "생활비", "화장품소매": "생활비",
            "여가": "생활비", "생활": "생활비", "인터넷쇼핑": "생활비", "인테리어/가정용품": "생활비"
        }
        st.write("사용자 지출 내 카테고리 목록:", df["카테고리"].unique())
        df["대분류"] = df["카테고리"].map(category_mapping).fillna("기타")

        file_mapping = {
            "이천시": "데이터1.xlsx",
            "서울시": "데이터2.xlsx"
        }

        # 사용자 선택에 따른 시트 이름
        selected_file = file_mapping.get(data_source, "데이터1.xlsx")

        try:
            df_excel = pd.read_excel(selected_file)
            df_excel["Date"] = pd.to_datetime(df_excel["Date"], errors='coerce')
            df_excel["Date"] = df_excel["Date"].apply(lambda d: d.replace(year=2025) if pd.notnull(d) else d)
            df_excel["대분류"] = df_excel["Category"].map(category_mapping).fillna("기타")
            df_excel["일자"] = pd.to_datetime(df_excel["Date"], errors='coerce').dt.date
            df["일자"] = df["날짜"].dt.date

            debug_df = df.groupby(["일자", "대분류"])["금액"].sum().reset_index()
            combined = pd.merge(
                debug_df.rename(columns={"금액": "내지출"}),
                df_excel.groupby(["일자", "대분류"])["AvgAmount"].mean().reset_index().rename(columns={"AvgAmount": "공공지출"}),
                on=["일자", "대분류"], how="outer"
            ).fillna(0)

            combined["차이"] = combined["내지출"] - combined["공공지출"]
            combined["내지출"] = (combined["내지출"] // 100 * 100).astype(int)
            combined["공공지출"] = (combined["공공지출"] // 100 * 100).astype(int)
            combined["차이"] = (combined["차이"] // 100 * 100).astype(int)

            # ✅ 날짜 비교 안정성 확보
            start = start_date if isinstance(start_date, datetime.date) else start_date.date()
            end = end_date if isinstance(end_date, datetime.date) else end_date.date()

            mask = (combined["일자"] >= start) & (combined["일자"] <= end)
            combined = combined[mask]
            st.subheader("일자별 대분류 내 지출 vs 공공 평균 비교")
            st.dataframe(combined.sort_values("일자"))

            st.subheader("선택한 기간 대분류별 내 지출 vs 20대 평균 지출 합계")

            df_excel["Date_naive"] = df_excel["Date"]
            # 1) 일자별 평균을 먼저 계산
            daily_avg = df_excel[
                (df_excel["Date_naive"] >= pd.to_datetime(start)) & (df_excel["Date_naive"] <= pd.to_datetime(end))
            ].groupby(["일자", "대분류"])["AvgAmount"].mean().reset_index()

            # 2) 다시 대분류 기준으로 평균 합계 계산
            public_monthly = daily_avg.groupby("대분류")["AvgAmount"].sum().reset_index().rename(columns={"AvgAmount": "공공지출합계"})
            user_monthly = df[
                (df["일자"] >= start) & (df["일자"] <= end)
            ].groupby("대분류")["금액"].sum().reset_index().rename(columns={"금액": "내지출합계"})

            adjustment_factors = {
                "식비": 0.8, "생활비": 0.4, "취미": 0.6, "커피": 0.1,
                "친목비": 0.7, "기타": 0.8, "교통비": 0.1
            }
            public_monthly["공공지출합계"] = public_monthly.apply(
                lambda row: row["공공지출합계"] * adjustment_factors.get(row["대분류"], 1.0),
                axis=1
            )            
            all_categories = list(category_mapping.values()) + ["기타"]
            all_categories = list(set(all_categories))

            user_monthly = user_monthly.set_index("대분류").reindex(all_categories, fill_value=0).reset_index()
            public_monthly = public_monthly.set_index("대분류").reindex(all_categories, fill_value=0).reset_index()
            monthly_comparison = pd.merge(user_monthly, public_monthly, on="대분류", how="outer").fillna(0)
            monthly_comparison["차이"] = monthly_comparison["내지출합계"] - monthly_comparison["공공지출합계"]

            monthly_comparison["내지출합계"] = (monthly_comparison["내지출합계"] // 100 * 100).astype(int)
            monthly_comparison["공공지출합계"] = (monthly_comparison["공공지출합계"] // 100 * 100).astype(int)
            monthly_comparison["차이"] = (monthly_comparison["차이"] // 100 * 100).astype(int)

            st.dataframe(monthly_comparison)

            for _, row in monthly_comparison.iterrows():
                status = "많이 씀" if row["차이"] > 0 else "절약함"
                st.write(f"📌 {row['대분류']} 항목에서 평균보다 {abs(row['차이']):,}원 {status}")

            st.subheader("📈 대분류별 내 지출 vs 공공 지출 (막대 그래프)")
            bar_df = monthly_comparison.melt(
                id_vars="대분류", value_vars=["내지출합계", "공공지출합계"],
                var_name="구분", value_name="금액"
            )

            bar_df = monthly_comparison.melt(
                id_vars="대분류", 
                value_vars=["내지출합계", "공공지출합계"],
                var_name="구분", 
                value_name="금액"
            )

            bar_chart = alt.Chart(bar_df).mark_bar().encode(
                x=alt.X("대분류:N", title="대분류"),
                xOffset="구분:N",
                y=alt.Y("금액:Q", title="금액"),
                color=alt.Color("구분:N", title="구분"),
                tooltip=["대분류", "구분", "금액"]
            ).properties(width=600)

            st.altair_chart(bar_chart, use_container_width=True)


        except Exception as e:
            st.error("엑셀 비교 분석 중 오류 발생")
            st.error(f"{e}")
    else:
        st.warning("해당 기간에 지출 내역이 없습니다.")

