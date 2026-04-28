import streamlit as st
import pandas as pd


# --- Параметры ---
DATA_PATH = "data/retail_aggregated.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)
        # Приводим столбцы с числами через запятую к float
        numeric_cols = df.select_dtypes(include="object").columns
        for col in numeric_cols:
            if df[col].astype(str).str.contains(",", regex=False).any():
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float, errors="ignore")
        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте, что он лежит в папке `data/` репозитория.")
        st.stop()


df = load_data()


# --- Стиль: лайтовый, полупрозрачный, анимированный ---
st.markdown("""
<style>
    /* Общий фон и типографика */
    .stApp {
        background: #ffffff;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        transition: background 0.3s ease;
    }

    /* Плавное появление всего контента */
    .stApp > div {
        opacity: 0;
        animation: fadeIn 0.8s ease-out forwards;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Боковая панель — лёгкая, полупрозрачная */
    .css-1l02zno {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(4px);
        transition: background 0.2s ease, box-shadow 0.2s ease;
    }

    .css-1d391kg {
        background: rgba(255, 255, 255, 0.92) !important;
    }

    /* Виджеты (selectbox, radio, multiselect) — лайтовые, с hover‑анимацией */
    .stRadio > div,
    .stSelectbox > div,
    .stMultiSelect > div {
        background: rgba(248, 249, 250, 0.97);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .stRadio > div:hover,
    .stSelectbox > div:hover,
    .stMultiSelect > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
        background: rgba(245, 248, 255, 0.97);
    }

    /* Метрики — плавные, с лёгким пульсированием */
    .stMetric p {
        font-size: 16px;
        color: #444;
    }

    .stMetric div {
        font-size: 24px;
        font-weight: 600;
        color: #1976d2;
        animation: pulse 4s infinite ease-in-out;
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.03);
            filter: drop-shadow(0 4px 6px rgba(0, 120, 255, 0.15));
        }
    }

    /* Графики — появляются плавно */
    .plotly-graph-div {
        opacity: 0;
        animation: fadeInGraph 0.7s ease 0.2s forwards;
    }

    @keyframes fadeInGraph {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Подсказки — мягкая анимация появления */
    .suggestion-box {
        background: rgba(240, 248, 255, 0.8);
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 10px 0;
        font-size: 14px;
        color: #333;
        animation: suggestIn 0.6s ease-out;
    }

    @keyframes suggestIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    .suggestion-title {
        font-weight: 600;
        color: #1976d2;
        margin-bottom: 6px;
    }

    /* Лёгкий hover на карточки и подсказки */
    .stMetric, .suggestion-box, .stColumn {
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .stMetric:hover, .suggestion-box:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
    }
</style>
""", unsafe_allow_html=True)


# --- Заголовок ---
st.title("✨ Дашборд розничной сети (лайтовый)")

# Упорядочим столбец "ТО"
st.markdown("### 👥 **Сравниваются ТО**")
all_stores = sorted(df["ТО"].dropna().unique().tolist())
selected_stores = st.multiselect(
    "Выберите ТО для сравнения",
    all_stores,
    default=all_stores[:3] if all_stores else []
)


# --- Логика генерации подсказок с решениями ---
def generate_insights(df, store, metric, value, total_avg, threshold=0.8):
    insight = "<div class='suggestion-box'><div class='suggestion-title'>💡 Рекомендации для ТО: {0}</div>".format(store)

    # Рентабельность
    if "Рентабельность 1" in metric or "рентабельность" in metric.lower():
        if value < total_avg * threshold:
            insight += f"Рентабельность ниже средней по сети. Проверьте выручку, себестоимость и расходы на реализацию (ФОТ, логистика, аренда)."
        else:
            insight += "Рентабельность в норме. Следите за динамикой по месяцам и структурой продаж."

    # Выручка
    elif "Выручка" in metric:
        if value < total_avg * threshold:
            insight += "Выручка ниже средней. Проверьте трафик, конверсию и средний чек, возможно, снизилась посещаемость или промо‑активность."
        else:
            insight += "Выручка в норме. Следите за маржой и структурой товарных групп, чтобы не снижать рентабельность."

    # ФОТ
    elif "ФОТ" in metric:
        if value > total_avg * 1.2:
            insight += "Доля ФОТ в выручке завышена. Проверьте часы работы, оптимальность численности персонала и KPI‑магазина."
        else:
            insight += "ФОТ в допустимом диапазоне. Следите, чтобы при росте выручки он не рос быстрее её."

    # Маржа / маржинальная прибыль
    elif "Марж" in metric or "маржинальная" in metric.lower():
        if value < total_avg * threshold:
            insight += "Маржинальная прибыль ниже средней. Сравните долю проды, скоропорта и непроды; возможно, низкомаржинальные группы доминируют."
        else:
            insight += "Маржинальная прибыль в норме. Следите за списаниями и структурой закупок."

    else:
        insight += "Метрика в норме. Следите за динамикой по месяцам и сравнением с другими ТО."

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

    # Основная метрика — в виде радио‑кнопок
    selected_metric = st.radio("Основная метрика", core_metrics, index=0)

    # Дополнительная метрика — любой числовой столбец
    secondary_metric = st.selectbox(
        "Дополнительная метрика",
        df.select_dtypes(include="number").columns.tolist(),
        index=0
    )

    st.divider()
    if len(selected_stores) == 0:
        st.warning("Выберите хотя бы одно ТО выше.")


if len(selected_stores) == 0:
    st.info("Пожалуйста, выберите хотя бы одно ТО в верхней строке для сравнения.")
else:
    data = df[df["ТО"].isin(selected_stores)]

    # Среднее по метрике для рекомендаций
    total_avg = data[selected_metric].mean()

    # KPI и базовые графики
    st.markdown("---")
    st.markdown(f"### **Сравнение `{selected_metric}` между выбранными ТО**")

    # KPI‑карточки (с анимацией)
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


    # --- Подсказки с решениями ---
    st.markdown("---")
    st.markdown("### 📌 Подсказки и решения по метрикам")

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
