import streamlit as st
import pandas as pd


# --- Параметры ---
DATA_PATH = "data/retail_aggregated.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)
        # Числа через запятую -> точки -> float
        numeric_cols = df.select_dtypes(include="object").columns
        for col in numeric_cols:
            if df[col].astype(str).str.contains(",", regex=False).any():
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float, errors="ignore")
        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте, что он лежит в папке `data/` репозитория.")
        st.stop()


df = load_data()


# --- Стиль: лайтовый, плавные анимации, но без пульсации KPI ---
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

    /* Боковая панель */
    .css-1l02zno {
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(4px);
    }

    .css-1d391kg {
        background: rgba(255, 255, 255, 0.92) !important;
    }

    /* Виджеты — лайтовые, с hover*/
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

    /* Метрики — без пульсации, но с hover */
    .stMetric p {
        font-size: 15px;
        color: #444;
    }

    .stMetric div {
        font-size: 22px;
        font-weight: 600;
        color: #1976d2;
    }

    .stMetric:hover {
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
    }

    /* Графики — плавные, без перегруза */
    .plotly-graph-div {
        opacity: 0;
        animation: fadeInGraph 0.6s ease 0.1s forwards;
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

    /* Подсказки */
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


# --- Заголовок ---
st.title("✨ BI‑Дашборд розничной сети (витрина для руководителя)")


# --- Вкладки приложения ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Обзор сети",
    "📉 Динамика по месяцам",
    "📊 Сравнение ТО",
    "🔍 Детализация по ТО",
    "💡 Рекомендации"
])


# --- Фильтры в боковой панели ---
with st.sidebar:
    st.header("⚙️ Фильтры")

    # ТО
    all_stores = sorted(df["ТО"].dropna().unique().tolist())
    selected_stores = st.multiselect("ТО", all_stores, default=all_stores[:3] if all_stores else [])

    # Месяц
    months = sorted(df["Месяц"].dropna().unique().tolist())
    selected_month = st.selectbox("Месяц", ["Все"] + months)

    # Размещение
    placements = sorted(df["Размещение"].dropna().unique().tolist())
    selected_placement = st.selectbox("Размещение", ["Все"] + placements)

    # Тип ТО
    types = sorted(df["Тип ТО"].dropna().unique().tolist())
    selected_type = st.selectbox("Тип ТО", ["Все"] + types)

    st.divider()

    if len(selected_stores) == 0:
        st.warning("Выберите хотя бы одно ТО.")


# --- Функция подсказок по метрикам ---
def generate_insights(df, metric, value, total_avg, store="ТО", threshold=0.8):
    insight = f"<div class='suggestion-box'><div class='suggestion-title'>💡 Рекомендация для ТО: {store}</div>"

    # Рентабельность
    if "Рентабельность 1" in metric or "рентабельность" in metric.lower():
        if value < total_avg * threshold:
            insight += f"Рентабельность ниже средней по сети. Проверьте маржинальность, себестоимость и расходы (ФОТ, логистика, аренда)."
        else:
            insight += "Рентабельность в норме. Следите за динамикой и структурой продаж."

    # Выручка
    elif "Выручка" in metric:
        if value < total_avg * threshold:
            insight += "Выручка ниже средней. Проверьте трафик, конверсию, средний чек и промо‑активность."
        else:
            insight += "Выручка в норме. Следите за маржой и ценовой политикой."

    # ФОТ
    elif "ФОТ" in metric:
        if value > total_avg * 1.2:
            insight += "Доля ФОТ в выручке завышена. Проверьте численность персонала, часы работы и KPI‑магазина."
        else:
            insight += "ФОТ в допустимом диапазоне. Следите за синхронностью роста выручки и ФОТ."

    # Маржа
    elif "Марж" in metric or "маржинальная" in metric.lower():
        if value < total_avg * threshold:
            insight += "Маржинальная прибыль ниже средней. Сравните доли проды, скоропорта и непроды."
        else:
            insight += "Маржинальная прибыль в норме. Следите за списаниями и структурой закупок."

    else:
        insight += "Метрика в норме. Следите за динамикой по месяцам."

    insight += "</div>"
    return insight


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


# --- Вкладка 1: Обзор сети ---
with tab1:
    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        st.markdown("### 📊 Обзор по всей сети (ТО)")
        metrics_list = [
            "Выручка б/НДС",
            "Себестоимость б/ндс",
            "Марж прибыль",
            "Рентабельность 1",
            "Доля ФОТ в выручке, %"
        ]
        total_avg = data[metrics_list[0]].mean()
        total = data[metrics_list[0]].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Суммарная выручка", f"{total:,.2f}")
        col2.metric("Средняя выручка по ТО", f"{total_avg:,.2f}")
        col3.metric("Количество ТО", f"{len(data['ТО'].unique())}")

        # Барчарт
        by_store = data.groupby("ТО", as_index=False)["Выручка б/НДС"].sum()
        st.bar_chart(by_store.set_index("ТО"))


# --- Вкладка 2: Динамика по месяцам ---
with tab2:
    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        st.markdown("### 📈 Динамика по месяцам")
        st.markdown("Выберите метрику:")
        metric = st.selectbox("Метрика", metrics_list, key="dyn_metric")

        by_month = data.groupby("Месяц", as_index=False)[metric].sum()
        st.line_chart(by_month.set_index("Месяц"))


# --- Вкладка 3: Сравнение ТО ---
with tab3:
    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        st.markdown("### 📊 Сравнение выбранных ТО по метрикам")
        selected_metric = st.selectbox("Выберите метрику для сравнения", metrics_list, key="comp_metric")

        by_store = data.groupby("ТО", as_index=False)[selected_metric].sum()
        st.bar_chart(by_store.set_index("ТО"))


# --- Вкладка 4: Детализация по ТО ---
with tab4:
    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        st.markdown("### 🔍 Детализация по одному ТО")

        selected_store = st.selectbox("ТО", all_stores, key="detail_store")

        store_data = data[data["ТО"] == selected_store]
        if len(store_data) == 0:
            st.info("Нет данных для выбранного ТО.")
        else:
            st.dataframe(store_data[["Месяц"] + metrics_list].round(2), height=400)
            st.markdown("---")

            # Подсказки для этого ТО
            total_avg = store_data["Выручка б/НДС"].mean()
            for metric in ["Выручка б/НДС", "Рентабельность 1", "Доля ФОТ в выручке, %", "Марж прибыль"]:
                value = store_data[metric].sum()
                st.markdown(
                    generate_insights(df, metric, value, total_avg, store=selected_store),
                    unsafe_allow_html=True
                )


# --- Вкладка 5: Рекомендации (аналитик) ---
with tab5:
    st.markdown("### 💡 Рекомендации по метрикам")

    if len(selected_stores) == 0:
        st.info("Выберите хотя бы одно ТО в боковой панели.")
    else:
        selected_metric = st.selectbox("Метрика для анализа", metrics_list, key="rec_metric")

        total = data[selected_metric].sum()
        total_avg = data[selected_metric].mean()

        for store in selected_stores:
            store_data = data[data["ТО"] == store]
            value = store_data[selected_metric].sum() if len(store_data) > 0 else 0
            st.markdown(
                generate_insights(df, selected_metric, value, total_avg, store),
                unsafe_allow_html=True
            )
