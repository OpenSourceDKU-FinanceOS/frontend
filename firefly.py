import streamlit as st
import requests
import pandas as pd
import altair as alt

st.title("Firefly III 지출 확인")

user_id = st.text_input("User ID를 입력하세요", "1")
start_date = st.date_input("조회 시작 날짜", pd.to_datetime("today"), key="start")
end_date = st.date_input("조회 종료 날짜", pd.to_datetime("today"), key="end")

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

        df["월"] = pd.to_datetime(df["날짜"], errors='coerce').dt.to_period("M").astype(str)
        monthly_total = df.groupby("월")["금액"].sum().reset_index()
        st.subheader("월별 총 지출")
        st.dataframe(monthly_total)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("CSV로 저장", data=csv, file_name="지출_내역.csv", mime="text/csv")

        try:
            df["날짜"] = pd.to_datetime(df["날짜"], errors='coerce')
            df["월"] = df["날짜"].dt.to_period("M").astype(str)
            df["요일"] = df["날짜"].dt.day_name()

            this_month = pd.to_datetime("today").month
            prev_month = this_month - 1 if this_month > 1 else 12

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

            st.subheader("카테고리별 전월 대비 비교")
            categories = ["식비", "커피", "생활비", "친목비", "교통비"]
            for category in categories:
                this_total = df[(df["카테고리"] == category) & (df["날짜"].dt.month == this_month)]["금액"].sum()
                last_total = df[(df["카테고리"] == category) & (df["날짜"].dt.month == prev_month)]["금액"].sum()
                delta = this_total - last_total

                st.subheader(f"{category} 비교")
                st.success(f"전월 {category}: {last_total:.2f} 원 → 이번 달: {this_total:.2f} 원")
                st.info(f"{'증가' if delta > 0 else '📉 감소'}: {abs(delta):.2f} 원")

        except Exception as e:
            st.error("분석 중 오류 발생")
            st.error(f"{e}")
    else:
        st.warning("해당 기간에 지출 내역이 없습니다.")