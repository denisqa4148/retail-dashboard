import streamlit as st
import pandas as pd


# --- Параметры ---
DATA_PATH = "data/retail_aggregated.csv"  # путь в репозитории, не Google Drive


# --- Загрузка данных ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)
        # Если есть число с запятой в колонке, заменяем её на точку и в float
        # Пример: выручка, рентабельность, маржа и т.п.
        # Нужно только для колонок, где реально число через запятую
        numeric_cols = df.select_dtypes(include="object").columns
        for col in numeric_cols:
            # Проверяем, есть ли в колонке хотя бы одно число через запятую
            if df[col].astype(str).str.contains(",", regex=False).any():
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float, errors="ignore")

        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте, что он лежит в папке `data/` репозитория.")
        st.stop()


df = load_data()


# --- Страница ---
st.title("📊 Дашборд розничной сети (ТО)")


# --- Фильтры ---
st.sidebar.header("🔍 Фильтрация")

# Фильтр по ТО
stores = sorted(df["ТО"].dropna().unique().tolist())
selected_store = st.sidebar.selectbox("ТО", ["Все"] + stores)

# Фильтр по Месяцу
months = sorted(df["Месяц"].dropna().unique().tolist())
selected_month = st.sidebar.selectbox("Месяц", ["Все"] + months)

# Фильтр по Размещение (Жилой дом / ТЦ и т.п.)
placements = sorted(df["Размещение"].dropna().unique().tolist())
selected_placement = st.sidebar.selectbox("Размещение", ["Все"] + placements)

# Тип ТО
types = sorted(df["Тип ТО"].dropna().unique().tolist())
selected_type = st.sidebar.selectbox("Тип ТО", ["Все"] + types)

# Выбор метрики из числовых столбцов
numeric_cols = df.select_dtypes(include="number").columns.tolist()
metric = st.sidebar.selectbox("Метрика", numeric_cols)


# --- Фильтрация данных ---
data = df.copy()

if selected_store != "Все":
    data = data[data["ТО"] == selected_store]
if selected_month != "Все":
    data = data[data["Месяц"] == selected_month]
if selected_placement != "Все":
    data = data[data["Размещение"] == selected_placement]
if selected_type != "Все":
    data = data[data["Тип ТО"] == selected_type]


# Если нет данных — показываем предупреждение
if len(data) == 0:
    st.info("По выбранным фильтрам нет данных 😓")
else:
    # --- KPI‑карточки ---
    st.subheader("📈 Основные показатели")

    col1, col2, col3 = st.columns(3)
    col1.metric("Среднее значение", f"{data[metric].mean():,.2f}")
    col2.metric("Максимум", f"{data[metric].max():,.2f}")
    col3.metric("Минимум", f"{data[metric].min():,.2f}")


    # --- График по ТО ---
    st.subheader(f"{metric} по ТО")

    if len(data["ТО"].unique()) == 1:
        st.write("Данные только для одного ТО.")
    else:
        chart_data = data.set_index("ТО")[metric]
        st.bar_chart(chart_data)


    # --- График динамики по месяцам ---
    st.subheader("📊 Динамика по месяцам")
    monthly_data = (
        df.groupby("Месяц", as_index=False)[metric]
        .sum()
        .set_index("Месяц")
    )
    st.line_chart(monthly_data)


    # --- Таблица с данными ---
    st.subheader("📋 Сырые данные (ТО и метрики)")
    st.dataframe(
        data[["ТО", "Размещение", "Тип ТО", "Месяц", metric]],
        height=400
    )
