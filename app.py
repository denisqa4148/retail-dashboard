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


# --- Стиль — лайтовый, «сайт‑подобный» ---
st.markdown("""
<style>
    .stApp {
        background: #ffffff;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    .section-block {
        opacity: 0;
        animation: fadeInSection 0.8s ease-out 0.1s forwards;
    }

    @keyframes fadeInSection {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .logo {
        font-size: 36px;
        font-weight: 600;
        margin-bottom: 20px;
        color: #1976d2;
    }

    .subtitle {
        font-size: 18px;
        color: #555;
        margin-bottom: 30px;
    }

    .stMetric p {
        font-size: 15px;
        color: #444;
    }

    .stMetric div {
        font-size: 22px;
        font-weight: 600;
        color: #1976d2;
    }

    .suggestion-box {
        background: rgba(240, 248, 255, 0.8);
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 10px 0;
        font-size: 14px;
        color: #333;
    }

    .suggestion-title {
        font-weight: 600;
        color: #1976d2;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)


# --- Загрузка данных (вызываться только в Dashboard) ---
df = None

def load_df():
    global df
    if df is None:
        df = load_data()
    return df

load_data_for_sidebar = df is None


# --- Структура: Landing vs Dashboard ---
st.markdown("<div class='main-container'>", unsafe_allow_html=True)


if "page" not in st.session_state:
    st.session_state.page = "landing"


# --- Лендинг (страница 1) ---
if st.session_state.page == "landing":
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("<div class='logo'>📊 Розничная сеть «ТО»</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Автоматизированная аналитическая платформа для управления торговой сетью</div>", unsafe_allow_html=True)

    st.markdown("### Возможности:")
    st.write("""
    - **Обзор сети** по выручке, марже и рентабельности  
    - **Динамика по месяцам**  
    - **Сравнение ТО** и **детализация по конкретному магазину**  
    - **Интеллектуальные рекомендации** по метрикам
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.button("👉 Войти в дашборд", key="to_dashboard", on_click=lambda: st.session_state.update(page="dashboard"))

    with col2:
        st.button("📩 Связаться с аналитиком", key="to_contact")
        if st.session_state.get("to_contact"):
            st.write("Свяжитесь с коммерческим/маркетинговым отделом для доступа к системе.")

    st.markdown("</div>", unsafe_allow_html=True)


# --- Dashboards (страница 2) ---
elif st.session_state.page == "dashboard":
    df = load_df()

    # --- Выбор панели (как в сайтовой навигации) ---
    st.sidebar.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.sidebar.markdown("### 🎯 Панель данных")
    panel_options = [
        "📈 Обзор сети",
        "📉 Динамика по месяцам",
        "📊 Сравнение ТО",
        "🔍 Детализация по ТО",
        "💡 Рекомендации"
    ]
    selected_panel = st.sidebar.radio("**Выберите раздел**", panel_options, index=0)

    # --- Фильтры ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Фильтры", unsafe_allow_html=True)

    all_stores = sorted(df["ТО"].dropna().unique().tolist())
    selected_stores = st.sidebar.multiselect("ТО", all_stores, default=all_stores[:3] if all_stores else [])

    months = sorted(df["Месяц"].dropna().unique().tolist())
    selected_month = st.sidebar.selectbox("Месяц", ["Все"] + months)

    placements = sorted(df["Размещение"].dropna().unique().tolist())
    selected_placement = st.sidebar.selectbox("Размещение", ["Все"] + placements)

    types = sorted(df["Тип ТО"].dropna().unique().tolist())
    selected_type = st.sidebar.selectbox("Тип ТО", ["Все"] + types)

    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # --- Фильтрация ---
    data = df.copy()
    if len(selected_stores) > 0:
        data = data[data["ТО"].isin(selected_stores)]
    if selected_month != "Все":
        data = data[data["Месяц"] == selected_month]
    if selected_placement != "Все":
        data = data[data["Размещение"] == selected_placement]
    if selected_type != "Все":
        data = data[data["Тип ТО"] == selected_type]


    # --- Функция подсказок ---
    def generate_insights(metric, value, total_avg, store="ТО", threshold=0.8):
        insight = f"<div class='suggestion-box'><div class='suggestion-title'>💡 Рекомендация для ТО: {store}</div>"

        if "Рентабельность 1" in metric or "рентабельность" in metric.lower():
            if value < total_avg * threshold:
                insight += "Рентабельность ниже средней. Проверьте себестоимость и расходы."
            else:
                insight += "Рентабельность в норме. Следите за динамикой."

        elif "Выручка" in metric:
            if value < total_avg * threshold:
                insight += "Выручка ниже средней. Проверьте трафик и конверсию."
            else:
                insight += "Выручка в норме. Следите за маржой."

        elif "ФОТ" in metric:
            if value > total_avg * 1.2:
                insight += "ФОТ завышен. Проверьте численность персонала и часы работы."
            else:
                insight += "ФОТ в допустимом диапазоне."

        elif "Марж" in metric:
            if value < total_avg * threshold:
                insight += "Маржинальная прибыль ниже средней. Сравните структуру товарных групп."
            else:
                insight += "Маржинальная прибыль в норме."

        else:
            insight += "Метрика в норме. Следите за динамикой."

        insight += "</div>"
        return insight


    # --- Панель 1: Обзор сети ---
    if selected_panel == "📈 Обзор сети":
        st.markdown("<div class='section-block'>", unsafe_allow_html=True)
        st.markdown("### 📊 Обзор сети по выбранным ТО")

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            metrics = ["Выручка б/НДС", "Себестоимость б/ндс", "Марж прибыль", "Рентабельность 1", "Доля ФОТ в выручке, %"]
            total = data[metrics[0]].sum()
            total_avg = data[metrics[0]].mean()

            col1, col2, col3 = st.columns(3)
            col1.metric("Суммарная выручка", f"{total:,.2f}")
            col2.metric("Средняя по ТО", f"{total_avg:,.2f}")
            col3.metric("Количество ТО", f"{len(data['ТО'].unique())}")

            by_store = data.groupby("ТО", as_index=False)[metrics[0]].sum()
            st.bar_chart(by_store.set_index("ТО"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 2: Динамика по месяцам ---
    if selected_panel == "📉 Динамика по месяцам":
        st.markdown("<div class='section-block'>", unsafe_allow_html=True)
        st.markdown("### 📈 Динамика по месяцам")

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            metric = st.selectbox("Метрика", metrics, key="dyn_metric")
            by_month = data.groupby("Месяц", as_index=False)[metric].sum()
            st.line_chart(by_month.set_index("Месяц"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 3: Сравнение ТО ---
    if selected_panel == "📊 Сравнение ТО":
        st.markdown("<div class='section-block'>", unsafe_allow_html=True)
        st.markdown("### 📊 Сравнение выбранных ТО")

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            selected_metric = st.selectbox("Метрика", metrics, key="comp_metric")
            by_store = data.groupby("ТО", as_index=False)[selected_metric].sum()
            st.bar_chart(by_store.set_index("ТО"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 4: Детализация по ТО ---
    if selected_panel == "🔍 Детализация по ТО":
        st.markdown("<div class='section-block'>", unsafe_allow_html=True)
        st.markdown("### 🔍 Детализация по одному ТО")

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            selected_store = st.selectbox("ТО", all_stores, key="detail_store")
            store_data = data[data["ТО"] == selected_store]

            if len(store_data) == 0:
                st.info("Нет данных для этого ТО.")
            else:
                st.dataframe(store_data[["Месяц"] + metrics].round(2), height=400)

                st.markdown("---")

                total_avg = store_data["Выручка б/НДС"].mean()
                for metric in ["Выручка б/НДС", "Рентабельность 1", "Марж прибыль"]:
                    value = store_data[metric].sum()
                    st.markdown(
                        generate_insights(metric, value, total_avg, selected_store),
                        unsafe_allow_html=True
                    )

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 5: Рекомендации ---
    if selected_panel == "💡 Рекомендации":
        st.markdown("<div class='section-block'>", unsafe_allow_html=True)
        st.markdown("### 💡 Рекомендации по метрикам")

        if len(selected_stores) == 0:
            st.info("Выберите хотя бы одно ТО.")
        else:
            metric = st.selectbox("Метрика", metrics, key="rec_metric")
            total_avg = data[metric].mean()

            for store in selected_stores:
                store_data = data[data["ТО"] == store]
                value = store_data[metric].sum() if len(store_data) > 0 else 0
                st.markdown(
                    generate_insights(metric, value, total_avg, store),
                    unsafe_allow_html=True
                )

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
