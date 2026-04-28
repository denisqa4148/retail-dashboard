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
        st.error(f"Файл {DATA_PATH} не найден. Проверьте путь в репозитории.")
        st.stop()


df = load_data()


# --- Стиль (лайтовый, полупрозрачный, белый фон) ---
st.markdown("""
<style>
    .stApp {
        background: #ffffff;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    .css-1l02zno { background: rgba(255, 255, 255, 0.85) !important; }
    .css-1d391kg { background: rgba(255, 255, 255, 0.85) !important; }

    .stRadio > div,
    .stSelectbox > div,
    .stMultiSelect > div {
        background: rgba(248, 249, 250, 0.95);
        border-radius: 8px;
        padding: 8px;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
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
        background: rgba(240, 248, 255, 0.75);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 8px 0;
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


# --- Заголовок ---
st.title("✨ Дашборд розничной сети (лайтовый)")

# --- Выбор ТО ---
st.markdown("### 👥 **Сравниваются ТО**")
all_stores = sorted(df["ТО"].dropna().unique().tolist())
selected_stores = st.multiselect(
    "Выберите ТО для сравнения",
    all_stores,
    default=all_stores[:3] if all_stores else []
)

# --- Функция подсказок ---
def generate_insights(df, store, metric, value, total_avg, threshold=0.8):
    insight = "<div class='suggestion-box'><div class='suggestion-title'>💡 Рекомендации для ТО: {0}</div>".format(store)

    if "Рентабельность 1" in metric or "рентабельность" in metric.lower():
        if value < total_avg * threshold:
            insight += f"Рентабельность ниже средней. Проверьте выручку и ФОТ, возможно, расходы завышены."
        else:
            insight += f"Рентабельность в норме. Следите за динамикой."

    elif "Выручка" in metric:
        if value < total_avg * threshold:
            insight += f"Выручка ниже средней. Проверьте трафик и конверсию, возможно, снижение посещений."
        else:
            insight += f"Выручка в норме. Следите за маржой."

    elif "ФОТ" in metric:
        if value > total_avg * 1.2:
            insight += "ФОТ завышен. Проверьте часы работы и состав персонала."
        else:
            insight += "ФОТ в норме."

    elif "Марж" in metric or "маржинальная" in metric.lower():
        if value < total_avg * threshold:
            insight += "Маржинальная прибыль низкая. Сравните проды/скоропорт/непроды."
        else:
            insight += "Маржинальная прибыль в норме. Следите за динамикой."

    else:
        insight += "Метрика в норме. Следите за изменениями по месяцам."

    insight += "</div>"
    return insight


# --- Боковая панель: метрики ---
with st.sidebar:
    st.header("📊 Метрики (в боковой панели)")

    core_metrics = [
        "Выручка б/НДС",
        "Себестоимость б/ндс",
        "Марж прибыль",
        "Рентабельность 1",
        "Доля ФОТ в выручке, %"
    ]

    selected_metric = st.radio("Основная метрика", core_metrics, index=0)
    secondary_metric = st.selectbox("Дополнительная метрика", df.select_dtypes(include="number").columns.tolist())

    st.divider()
    if len(selected_stores) == 0:
        st.warning("Выберите хотя бы одно ТО ↑")


if len(selected_stores) == 0:
    st.info("Пожалуйста, выберите хотя бы одно ТО выше.")
else:
    data = df[df["ТО"].isin(selected_stores)]

    st.markdown("---")
    st.markdown(f"### Сравнение `{selected_metric}` между выбранными ТО")

    # KPI‑карточки
    col1, col2, col3 = st.columns(3)
    total = data[selected_metric].sum()
    avg = data[selected_metric].mean()
    max_val = data[selected_metric].max()

    col1.metric("Сумма по ТО", f"{total:,.2f}")
    col2.metric("Среднее значение", f"{avg:,.2f}")
    col3.metric("Максимум по ТО", f"{max_val:,.2f}")


    # --- Барчарт по ТО ---
    st.markdown("---")
    st.markdown(f"**{selected_metric} по выбранным ТО**")
    by_store = data.groupby("ТО", as_index=False)[selected_metric].sum()
    st.bar_chart(by_store.set_index("ТО"))


    # --- Подсказки для каждого ТО ---
    st.markdown("---")
    st.markdown("### 📌 Подсказки и решения")

    total_avg = data[selected_metric].mean()
    for store in selected_stores:
        store_data = data[data["ТО"] == store]
        value = store_data[selected_metric].sum() if len(store_data) > 0 else 0
        st.markdown(
            generate_insights(df, store, selected_metric, value, total_avg),
            unsafe_allow_html=True
        )


    # --- Динамика по месяцам ---
    st.markdown("---")
    st.markdown(f"**{secondary_metric} по месяцам (все выбранные ТО)**")
    by_month = data.groupby("Месяц", as_index=False)[secondary_metric].sum()
    st.line_chart(by_month.set_index("Месяц"))
