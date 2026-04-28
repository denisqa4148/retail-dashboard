import streamlit as st
import pandas as pd


# --- Параметры: ПУТЬ к CSV в Google Drive ---
DATA_PATH = "/content/drive/MyDrive/retail_dashboard/data/retail_aggregated.csv"


# --- Загрузка данных ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8")
        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте, что он лежит в Google Drive по указанному пути.")
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
placements = pd.Series(df["Размещение"].dropna()).unique()
if len(placements) > 0:
    selected_placement = st.sidebar.selectbox("Размещение", ["Все"] + sorted(placements))
else:
    selected_placement = "Все"

# Тип ТО
types = pd.Series(df["Тип ТО"].dropna()).unique()
if len(types) > 0:
    selected_type = st.sidebar.selectbox("Тип ТО", ["Все"] + sorted(types))
else:
    selected_type = "Все"

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
    st.subheader(f"{metric} по ТО ({selected_store if selected_store != 'Все' else 'все'})")

    if len(data["ТО"].unique()) == 1:
        st.write("Данные только для одного ТО.")
    else:
        chart_data = data.set_index("ТО")[metric]
        st.bar_chart(chart_data)


    # --- График динамики по месяцам ---
    st.subheader(f"📊 Динамика {metric} по месяцам")

    all_months_data = (
        df.groupby(["Месяц"], as_index=False)[metric]
        .sum()
        .set_index("Месяц")
    )
    st.line_chart(all_months_data)


    # --- Таблица с сырыми данными ---
    st.subheader("📋 Сырые данные (ТО и метрики)")
    st.dataframe(
        data[["ТО", "Размещение", "Тип ТО", "Месяц", metric]],
        height=400
    )
