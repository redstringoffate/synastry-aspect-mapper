import streamlit as st
import pandas as pd

# 별자리 매핑
ZODIAC_SIGNS = {
    "♈": "Aries", "♉": "Taurus", "♊": "Gemini", "♋": "Cancer",
    "♌": "Leo", "♍": "Virgo", "♎": "Libra", "♏": "Scorpio",
    "♐": "Sagittarius", "♑": "Capricorn", "♒": "Aquarius", "♓": "Pisces"
}
SIGN_KEYS = list(ZODIAC_SIGNS.values())

# 오브 범위 (분 단위)
ORB_RANGES = {
    "Conjunction": 480, "Opposition": 480,
    "Trine1": 360, "Trine2": 360,
    "Square1": 360, "Square2": 360,
    "Quintile1": 120, "Quintile2": 120,
    "Bi-quintile1": 120, "Bi-quintile2": 120,
    "Sextile1": 240, "Sextile2": 240,
    "Septile1": 60, "Septile2": 60,
    "Bi-septile1": 60, "Bi-septile2": 60,
    "Tri-septile1": 60, "Tri-septile2": 60,
    "Octile1": 180, "Octile2": 180,
    "Sesquiquadrate1": 180, "Sesquiquadrate2": 180,
    "Novile1": 60, "Novile2": 60,
    "Bi-novile1": 60, "Bi-novile2": 60,
    "Decile1": 90, "Decile2": 90,
    "Tri-decile1": 90, "Tri-decile2": 90,
    "Undecile1": 30, "Undecile2": 30,
    "Bi-undecile1": 30, "Bi-undecile2": 30,
    "Tri-undecile1": 30, "Tri-undecile2": 30,
    "Quad-undecile1": 30, "Quad-undecile2": 30,
    "Quin-undecile1": 30, "Quin-undecile2": 30,
    "Semi-sextile1": 120, "Semi-sextile2": 120,
    "Quincunx1": 180, "Quincunx2": 180,
}

# 위치값 파싱 (예: ♊ 10°46′ → 분 단위)
def parse_position(value):
    if not isinstance(value, str):
        return None
    try:
        parts = value.strip().split()
        sign_symbol = parts[0]
        degree_part, minute_part = parts[1].split("°")
        degree = int(degree_part)
        minute = int(minute_part.replace("'", "").replace("′", ""))
        sign_index = list(ZODIAC_SIGNS.keys()).index(sign_symbol)
        return sign_index * 1800 + degree * 60 + minute
    except Exception:
        return None

# Aspects 시트 로드
@st.cache_data
def load_aspects():
    df = pd.read_excel("Aspects.xlsx", sheet_name="Aspects")
    for col in df.columns[3:]:
        df[col] = df[col].apply(parse_position)
    return df

df_aspects = load_aspects()

# 행 → 분 단위 변환
def to_row_index(sign, degree, minute):
    sign_index = SIGN_KEYS.index(sign)
    return sign_index * 1800 + degree * 60 + minute

# Streamlit UI
st.title("💞 Synastry Aspect Mapper (Lookup Ver.)")
st.caption("두 사람의 위치를 기반으로 Aspect를 lookup 방식으로 계산합니다.")

# 세션 초기화
for key in ["A_points", "B_points"]:
    if key not in st.session_state:
        st.session_state[key] = []

colA, colB = st.columns(2)

# --- A 입력 ---
with colA:
    st.subheader("🩷 Person A")
    with st.form("A_form", clear_on_submit=True):
        label = st.text_input("Label (예: Sun)", key="A_label")
        sign = st.selectbox("Sign", SIGN_KEYS, key="A_sign")
        degree = st.number_input("Degree", 0, 29, 0, key="A_deg")
        minute = st.number_input("Minute", 0, 59, 0, key="A_min")
        if st.form_submit_button("➕ 등록"):
            if label:
                idx = to_row_index(sign, degree, minute)
                st.session_state.A_points.append((label, idx))
                st.success(f"{label} — {sign} {degree}°{minute}′ 등록 완료")

    st.markdown("**📋 등록된 포인트:**")
    for i, (label, row) in enumerate(st.session_state.A_points):
        s = SIGN_KEYS[row // 1800]
        d = (row % 1800) // 60
        m = row % 60
        cols = st.columns([4, 1])
        cols[0].write(f"• **{label}** — {s} {d}°{m}′")
        if cols[1].button("🗑️", key=f"delA_{i}"):
            st.session_state.A_points.pop(i)
            st.rerun()

# --- B 입력 ---
with colB:
    st.subheader("💙 Person B")
    with st.form("B_form", clear_on_submit=True):
        label = st.text_input("Label (예: Moon)", key="B_label")
        sign = st.selectbox("Sign", SIGN_KEYS, key="B_sign")
        degree = st.number_input("Degree", 0, 29, 0, key="B_deg")
        minute = st.number_input("Minute", 0, 59, 0, key="B_min")
        if st.form_submit_button("➕ 등록"):
            if label:
                idx = to_row_index(sign, degree, minute)
                st.session_state.B_points.append((label, idx))
                st.success(f"{label} — {sign} {degree}°{minute}′ 등록 완료")

    st.markdown("**📋 등록된 포인트:**")
    for i, (label, row) in enumerate(st.session_state.B_points):
        s = SIGN_KEYS[row // 1800]
        d = (row % 1800) // 60
        m = row % 60
        cols = st.columns([4, 1])
        cols[0].write(f"• **{label}** — {s} {d}°{m}′")
        if cols[1].button("🗑️", key=f"delB_{i}"):
            st.session_state.B_points.pop(i)
            st.rerun()

st.divider()

# --- Synastry 계산 ---
if st.button("🔍 Synastry Aspect 계산"):
    results = []
    for labelA, rowA in st.session_state.A_points:
        for labelB, rowB in st.session_state.B_points:
            diff = abs(rowA - rowB)
            diff = min(diff, 21600 - diff)  # 원형 순환 고려

            # Conjunction 처리
            if diff <= ORB_RANGES["Conjunction"]:
                orb_val = diff / 60
                results.append({
                    "A": labelA, "B": labelB,
                    "Aspect": "Conjunction",
                    "Orb": f"{orb_val:.2f}°"
                })
                continue

            # Lookup 방식
            for aspect, orb in ORB_RANGES.items():
                if aspect not in df_aspects.columns:
                    continue
                target_row = df_aspects.loc[rowA, aspect]
                if pd.isna(target_row):
                    continue

                # 🎯 단순 row 위치 비교 — 물리적 lookup 전용
                delta = abs(rowB - target_row)
                delta = min(delta, 21600 - delta)

                if delta <= orb:
                    orb_val = delta / 60
                    clean_aspect = ''.join([c for c in aspect if not c.isdigit()])
                    if any(r for r in results if {r["A"], r["B"]} == {labelA, labelB} and r["Aspect"] == clean_aspect):
                        continue
                    results.append({
                        "A": labelA, "B": labelB,
                        "Aspect": clean_aspect,
                        "Orb": f"{orb_val:.2f}°"
                    })

    if results:
        st.success("✅ Synastry 계산 완료!")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results, use_container_width=True)
        csv = df_results.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 결과 CSV 다운로드", csv, file_name="synastry_results.csv")
    else:
        st.warning("⚠️ 성립되는 Synastry Aspect가 없습니다.")
