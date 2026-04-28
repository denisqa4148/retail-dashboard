import streamlit as st
import pandas as pd


# --- Параметры ---
DATA_PATH = "data/retail_aggregated.csv"
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)
        # Если есть столбцы с числами через запятую
        numeric_cols = df.select_dtypes(include="object").columns
        for col in numeric_cols:
            if df[col].astype(str).str.contains(",", regex=False).any():
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float, errors="ignore")
        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте путь в репозитории.")
        st.stop()


df = load_data()


# --- Стиль CSS (делает интерфейс приятнее) ---
st.markdown("""
<style>
    .reportview-container {
        background: #f8f9fa;
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .stMetric p {
        font-size: 16px;
    }
    .stMetric div {
        font-size: 24px !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- Заголовок ---
st.title("🎯 Дашборд розничной сети")
st.markdown("Аналитика по ТО, месяцам и метрикам.")


# --- Вкладки интерфейса ---
tab1, tab2, tab3 = st.tabs([
    "📊 Обзор",
    "🔍 Фильтрация деталей",
    "📈 Сравнение ТО"
])


# --- Фильтры (общие для всех вкладок) ---
with st.sidebar:
    st.header("⚙️ Фильтры")
    
    # ТО
    stores = sorted(df["ТО"].dropna().unique().tolist())
    selected_store = st.selectbox("ТО", ["Все"] + stores)

    # Месяц
    months = sorted(df["Месяц"].dropna().unique().tolist())
    selected_month = st.selectbox("Месяц", ["Все"] + months)

    # Размещение
    placements = sorted(df["Размещение"].dropna().unique().tolist())
    selected_placement = st.selectbox("Размещение", ["Все"] + placements)

    # Тип ТО
    types = sorted(df["Тип ТО"].dropna().unique().tolist())
    selected_type = st.selectbox("Тип ТО", ["Все"] + types)

    # Основная метрика
    core_metrics = [
        "Выручка б/НДС",
        "Себестоимость б/ндс",
        "Марж прибыль",
        "Рентабельность 1",
        "Доля ФОТ в выручке, %"
    ]
    selected_metric = st.selectbox("Основная метрика", core_metrics)

    st.divider()
    st.info(" Фильтры применяются ко всем вкладкам")


# --- Фильтрация данных (для всех вкладок) ---
data = df.copy()
if selected_store != "Все":
    data = data[data["ТО"] == selected_store]
if selected_month != "Все":
    data = data[data["Месяц"] == selected_month]
if selected_placement != "Все":
    data = data[data["Размещение"] == selected_placement]
if selected_type != "Все":
    data = data[data["Тип ТО"] == selected_type]


if len(data) == 0:
    st.info("По выбранным фильтрам нет данных 😅")
else:
    # --- Вкладка 1: Обзор ---
    with tab1:
        st.subheader("📊 Обзор по сети")

        # KPI‑карточки
        col1, col2, col3, col4 = st.columns(4)
        top = data[selected_metric].sum()

        col1.metric("Сумма выбранной метрики", f"{top:,.2f}")
        col2.metric("Среднее значение", f"{data[selected_metric].mean():,.2f}")
        col3.metric("Максимум", f"{data[selected_metric].max():,.2f}")
        col4.metric("Минимум", f"{data[selected_metric].min():,.2f}")

        st.markdown("---")

        # Барчарт по ТО
        st.markdown(f"**{selected_metric} по ТО**")
        if len(data["ТО"].unique()) > 1:
            chart_data = data.groupby("ТО", as_index=False)[selected_metric].sum()
            st.bar_chart(chart_data.set_index("ТО"))
        else:
            st.write("Данные только для одного ТО.")


    # --- Вкладка 2: Детали по одному ТО ---
    with tab2:
        st.subheader("🔍 Детализация по ТО")

        if selected_store == "Все":
            st.info("Выберите один ТО в фильтре, чтобы увидеть детализацию.")
        else:
            st.markdown(f"**ТО: {selected_store}**")

            # Таблица с числовыми метриками
            st.markdown("### 📊 Числовые показатели")
            numeric_cols = data.select_dtypes(include="number").columns.tolist()
            st.dataframe(
                data[["Месяц"] + numeric_cols].round(2),
                height=400
            )

            # Выбор второй метрики для графика
            secondary_metric = st.selectbox("Вторая метрика для графика", numeric_cols)

            st.markdown("### 📈 Динамика по месяцам")
            monthly = data.groupby("Месяц", as_index=False)[secondary_metric].sum()
            st.line_chart(monthly.set_index("Месяц"))


    # --- Вкладка 3: Сравнение нескольких ТО ---
    with tab3:
        st.subheader("📈 Сравнение ТО")

        st.markdown("Выберите несколько ТО для сравнения:")
        all_stores = sorted(df["ТО"].dropna().unique().tolist())
        selected_stores = st.multiselect("ТО", all_stores, default=all_stores[:3])

        if len(selected_stores) == 0:
            st.info("Выберите хотя бы одно ТО для сравнения.")
        else:
            comparison_data = df[df["ТО"].isin(selected_stores)]
            if selected_month != "Все":
                comparison_data = comparison_data[comparison_data["Месяц"] == selected_month]

            st.markdown(f"**{selected_metric} по выбранным ТО**")
            grouped = comparison_data.groupby("ТО", as_index=False)[selected_metric].sum()
            st.bar_chart(grouped.set_index("ТО"))

            st.markdown("---")

            st.markdown(
                "Используйте фильтры в левой панели, чтобы изменить выбранные ТО, месяц или метрику."
            )
