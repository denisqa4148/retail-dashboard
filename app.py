import streamlit as st
import pandas as pd


# --- Параметры ---
DATA_PATH = "data/retail_aggregated.csv"
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)
        # Числа с запятой → точка → float
        numeric_cols = df.select_dtypes(include="object").columns
        for col in numeric_cols:
            if df[col].astype(str).str.contains(",", regex=False).any():
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float, errors="ignore")
        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте, что он лежит в папке `data/` репозитория.")
        st.stop()


df = load_data()


# --- Стиль (лёгкий «современный») ---
st.markdown("""
<style>
    .stApp {
        background: #f9f9fb;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    .big-font {
        font-size: 20px;
        font-weight: 600;
    }
    .stMetric p {
        font-size: 16px;
        color: #444;
    }
    .stMetric div {
        font-size: 24px;
        font-weight: 600;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


# --- Заголовок ---
st.title("✨ Дашборд розничной сети")

# Верхняя строка — сравниваемые ТО
st.markdown("### 👥 **Сравниваются ТО**")
all_stores = sorted(df["ТО"].dropna().unique().tolist())
selected_stores = st.multiselect(
    "Выберите ТО для сравнения",
    all_stores,
    default=all_stores[:3] if all_stores else []
)


# --- Боковая панель: метрики ---
with st.sidebar:
    st.header("📊 Метрики")

    # Список «ключевых» метрик в боковой панели
    core_metrics = [
        "Выручка б/НДС",
        "Себестоимость б/ндс",
        "Марж прибыль",
        "Рентабельность 1",
        "Доля ФОТ в выручке, %"
    ]

    # Можно сделать как радио или selectbox
    selected_metric = st.radio(
        "Основная метрика",
        core_metrics,
        index=0
    )

    # Опционально: вторая метрика
    secondary_metric = st.selectbox(
        "Дополнительная метрика",
        df.select_dtypes(include="number").columns.tolist()
    )

    st.divider()

    if len(selected_stores) == 0:
        st.warning("Выберите хотя бы одно ТО для сравнения.")


# Если ничего не выбрано
if len(selected_stores) == 0:
    st.info("Пожалуйста, выберите хотя бы одно ТО в верхней строке.")
else:
    # Фильтрация по выбранным ТО
    data = df[df["ТО"].isin(selected_stores)]

    # Вверху — итоги по выбранным ТО
    st.markdown("---")
    st.markdown(f"### **Сравнение метрики `{selected_metric}` между выбранными ТО**")

    # Крупные KPI‑карточки
    col1, col2, col3 = st.columns(3)

    total = data[selected_metric].sum()
    avg = data[selected_metric].mean()
    max_val = data[selected_metric].max()

    col1.metric("Сумма по ТО", f"{total:,.2f}")
    col2.metric("Среднее значение", f"{avg:,.2f}")
    col3.metric("Максимум по ТО", f"{max_val:,.2f}")


    # --- График барчарт по ТО ---
    st.markdown("---")
    st.markdown(f"**{selected_metric} по выбранным ТО**")
    by_store = data.groupby("ТО", as_index=False)[selected_metric].sum()
    st.bar_chart(by_store.set_index("ТО"))


    # --- Второй график: динамика по месяцам ---
    st.markdown("---")
    st.markdown(f"**{secondary_metric} по месяцам (все выбранные ТО)**")
    by_month = data.groupby("Месяц", as_index=False)[secondary_metric].sum()
    st.line_chart(by_month.set_index("Месяц"))

    # --- Таблица (опционально, можно скрыть или убрать в expand) ---
    st.markdown("---")
    with st.expander("Показать детали по выбранным ТО", expanded=False):
        st.dataframe(data[["ТО", "Размещение", "Тип ТО", "Месяц"] + [selected_metric, secondary_metric]].round(2))
