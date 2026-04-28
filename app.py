import streamlit as st
import pandas as pd


# --- Параметры ---
DATA_PATH = "data/retail_aggregated.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)
        numeric_cols = df.select_dtypes(include="object").columns
        for col in numeric_cols:
            if df[col].astype(str).str.contains(",", regex=False).any():
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float, errors="ignore")
        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте, что он лежит в папке `data/` репозитория.")
        st.stop()


# --- Стиль: сайт‑подобный, лайтовый, минималистично ---
st.markdown("""
<style>
    body {
        margin: 0;
        padding: 0;
    }

    .stApp {
        background: #ffffff;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    /* Лендинг-заголовок */
    .landing-title {
        font-size: 40px;
        font-weight: 600;
        color: #1976d2;
        margin-bottom: 10px;
    }

    .landing-subtitle {
        font-size: 18px;
        color: #555;
        margin-bottom: 30px;
    }

    .landing-card {
        background: #f9f9fb;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        margin-bottom: 24px;
    }

    .landing-btn {
        background: #1976d2;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        cursor: pointer;
        display: flex;
        justify-content: center;
        margin: 10px auto;
        width: 240px;
    }

    .landing-btn:hover {
        background: #1565c0;
    }

    /* Панельный блок */
    .panel-section {
        background: #f9f9fb;
        border-radius: 12px;
        padding: 20px;
        margin: 24px 0;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    }

    .panel-title {
        font-size: 20px;
        margin-bottom: 16px;
        color: #1976d2;
    }

    /* KPI и метрики */
    .stMetric p {
        font-size: 15px;
        color: #444;
    }

    .stMetric div {
        font-size: 22px;
        font-weight: 600;
        color: #1976d2;
    }

    /* Графики */
    .plotly-graph-div {
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)


# --- Загрузка данных (глобально) ---
df = None

def load_df():
    global df
    if df is None:
        df = load_data()
    return df


# --- Страницы приложения ---
if "page" not in st.session_state:
    st.session_state.page = "landing"


# --- Функция подсказок ---
def generate_insights(metric, value, total_avg, store="ТО", threshold=0.8):
    insight = f"<div class='landing-card'><div style='font-weight:600;color:#1976d2;'>💡 Рекомендация для ТО: {store}</div>"

    if "Рентабельность 1" in metric or "рентабельность" in metric.lower():
        if value < total_avg * threshold:
            insight += "Рентабельность ниже средней. Проверьте себестоимость и расходы на реализацию (ФОТ, логистика, аренда)."
        else:
            insight += "Рентабельность в норме. Следите за динамикой и структурой продаж."

    elif "Выручка" in metric:
        if value < total_avg * threshold:
            insight += "Выручка ниже средней. Проверьте трафик, конверсию и средний чек, возможно, снижение посещений или промо‑активности."
        else:
            insight += "Выручка в норме. Следите за маржой и ценовой политикой, чтобы не снижать рентабельность."

    elif "ФОТ" in metric:
        if value > total_avg * 1.2:
            insight += "Доля ФОТ в выручке завышена. Проверьте численность персонала, часы работы и KPI‑магазина."
        else:
            insight += "ФОТ в допустимом диапазоне. Следите, чтобы расходы росли не быстрее выручки."

    elif "Марж" in metric:
        if value < total_avg * threshold:
            insight += "Маржинальная прибыль ниже средней. Сравните доли проды, скоропорта и непроды — возможно, низкомаржинальные группы доминируют."
        else:
            insight += "Маржинальная прибыль в норме. Следите за списаниями и структурой закупок."

    else:
        insight += "Метрика в норме. Следите за динамикой по месяцам и сравнением с другими ТО."

    insight += "</div>"
    return insight


# === ЛЕНДИНГ ===
if st.session_state.page == "landing":
    st.markdown("""
        <div class='landing-card'>
            <div class='landing-title'>📊 Розничная сеть «ТО»</div>
            <div class='landing-subtitle'>
                Анализ выручки, маржи, рентабельности и эффективности торговых объектов в одной панели
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='landing-card'>
            <h3>🎯 Ключевые возможности</h3>
            <p>
                <b>Обзор сети:</b> выручка, маржа и рентабельность по сети в целом.<br>
                <b>Динамика по месяцам:</b> изменения важнейших метрик по времени.<br>
                <b>Сравнение ТО:</b> выявляйте лучшие и проблемные торговые объекты.<br>
                <b>Интеллектуальные рекомендации:</b> предлагаем направления улучшения по каждому показателю.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='landing-card'>
            <h3>👥 Для кого это</h3>
            <p>
                Для руководителей торговых сетей, руководителей регионов и директоров по аналитике.<br>
                Помогает принимать решения по структуре сети, мерчандайзингу, персоналу и маркетингу.
            </p>
        </div>
    """, unsafe_allow_html=True)


    # --- Кнопка Войти в Analytics ===
    st.markdown("""
        <div style='text-align:center; margin-top:40px;'>
            <div class='landing-btn' onclick='location.reload()' style='cursor:pointer;' id='btn-analyze'>Войти в Analytics</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("➡️ Войти в Analytics (Streamlit‑кнопка)", key="nav_analytics"):
        st.session_state.page = "analytics"
        st.rerun()


# === АНАЛИТИЧЕСКИЙ ПАНЕЛЬНЫЙ ИНТЕРФЕЙС ===
elif st.session_state.page == "analytics":
    df = load_df()
    metrics_list = ["Выручка б/НДС", "Себестоимость б/ндс", "Марж прибыль", "Рентабельность 1", "Доля ФОТ в выручке, %"]


    # --- Боковая панель — как навигация сайта ---
    with st.sidebar:
        st.markdown("<h3 style='color:#1976d2;'>🎯 Панель BI</h3>", unsafe_allow_html=True)
        nav_options = ["📊 Обзор сети", "📉 Динамика", "🌍 Сравнение ТО", "💡 Рекомендации"]
        selected_nav = st.radio("Раздел", nav_options)

        st.divider()
        st.markdown("### ⚙️ Фильтры", unsafe_allow_html=True)

        all_stores = sorted(df["ТО"].dropna().unique().tolist())
        selected_stores = st.multiselect("ТО", all_stores, default=all_stores[:3] if all_stores else [])

        months = sorted(df["Месяц"].dropna().unique().tolist())
        selected_month = st.selectbox("Месяц", ["Все"] + months)

        placements = sorted(df["Размещение"].dropna().unique().tolist())
        selected_placement = st.selectbox("Размещение", ["Все"] + placements)

        types = sorted(df["Тип ТО"].dropna().unique().tolist())
        selected_type = st.selectbox("Тип ТО", ["Все"] + types)

        # Кнопка назад
        if st.button("⬅️ Назад на лендинг", key="back_to_landing"):
            st.session_state.page = "landing"
            st.rerun()


    # --- Фильтрация данных ---
    data = df.copy()
    if len(selected_stores) > 0:
        data = data[data["ТО"].isin(selected_stores)]
    if selected_month != "Все":
        data = data[data["Месяц"] == selected_month]
    if selected_placement != "Все":
        data = data[data["Размещение"] == selected_placement]
    if selected_type != "Все":
        data = data[data["Тип ТО"] == selected_type]


    # --- Панель 1: Обзор сети ---
    if selected_nav == "📊 Обзор сети":
        st.markdown("<div class='panel-section'><div class='panel-title'>📊 Обзор сети</div>", unsafe_allow_html=True)

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            total = data[metrics_list[0]].sum()
            total_avg = data[metrics_list[0]].mean()

            col1, col2, col3 = st.columns(3)
            col1.metric("Суммарная выручка", f"{total:,.2f}")
            col2.metric("Средняя выручка на ТО", f"{total_avg:,.2f}")
            col3.metric("Количество ТО", f"{len(data['ТО'].unique())}")

            st.markdown("---")

            by_store = data.groupby("ТО", as_index=False)[metrics_list[0]].sum()
            st.bar_chart(by_store.set_index("ТО"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 2: Динамика по месяцам ---
    if selected_nav == "📉 Динамика":
        st.markdown("<div class='panel-section'><div class='panel-title'>📈 Динамика по месяцам</div>", unsafe_allow_html=True)

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            metric = st.selectbox("Метрика", metrics_list, key="dyn_metric")
            by_month = data.groupby("Месяц", as_index=False)[metric].sum()
            st.line_chart(by_month.set_index("Месяц"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 3: Сравнение ТО ---
    if selected_nav == "🌍 Сравнение ТО":
        st.markdown("<div class='panel-section'><div class='panel-title'>🗺️ Сравнение выбранных ТО</div>", unsafe_allow_html=True)

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            selected_metric = st.selectbox("Метрика", metrics_list, key="comp_metric")
            by_store = data.groupby("ТО", as_index=False)[selected_metric].sum()
            st.bar_chart(by_store.set_index("ТО"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 4: Рекомендации ---
    if selected_nav == "💡 Рекомендации":
        st.markdown("<div class='panel-section'><div class='panel-title'>💡 Рекомендации по метрикам</div>", unsafe_allow_html=True)

        if len(selected_stores) == 0:
            st.info("Выберите хотя бы одно ТО в боковой панели.")
        else:
            selected_metric = st.selectbox("Метрика", metrics_list, key="rec_metric")
            total_avg = data[selected_metric].mean()

            for store in selected_stores:
                store_data = data[data["ТО"] == store]
                value = store_data[selected_metric].sum() if len(store_data) > 0 else 0
                st.markdown(
                    generate_insights(selected_metric, value, total_avg, store),
                    unsafe_allow_html=True
                )

        st.markdown("</div>", unsafe_allow_html=True)
