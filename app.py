import streamlit as st
import pandas as pd


# --- Параметры ---
DATA_PATH = "data/retail_aggregated.csv"

@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH, encoding="utf-8", low_memory=False)
        # Числа с запятой -> точки -> float
        numeric_cols = df.select_dtypes(include="object").columns
        for col in numeric_cols:
            if df[col].astype(str).str.contains(",", regex=False).any():
                df[col] = df[col].astype(str).str.replace(",", ".").astype(float, errors="ignore")
        return df
    except FileNotFoundError:
        st.error(f"Файл {DATA_PATH} не найден. Проверьте, что он лежит в папке `data/` репозитория.")
        st.stop()


df = load_data()


# --- Стиль: лайтовый, плавные анимации, без пульсации KPI ---
st.markdown("""
<style>
    /* Общий фон и типографика */
    .stApp {
        background: #ffffff;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        transition: background 0.3s ease;
    }

    /* Плавное появление блоков */
    .section-block {
        opacity: 0;
        animation: fadeInSection 0.8s ease-out 0.1s forwards;
    }

    @keyframes fadeInSection {
        from {
            opacity: 0;
            transform: translateY(12px);
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

    /* Виджеты — лайтовые, с hover */
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

    /* Метрики — без анимации, но hover */
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

    /* Графики — плавное появление */
    .plotly-graph-div {
        opacity: 0;
        animation: fadeInGraph 0.7s ease 0.1s forwards;
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
st.title("✨ BI‑Дашборд розничной сети (панельный режим)")


# --- Функция подсказок ---
def generate_insights(df, metric, value, total_avg, store="ТО", threshold=0.8):
    insight = f"<div class='suggestion-box'><div class='suggestion-title'>💡 Рекомендация для ТО: {store}</div>"

    # Рентабельность
    if "Рентабельность 1" in metric or "рентабельность" in metric.lower():
        if value < total_avg * threshold:
            insight += "Рентабельность ниже средней. Проверьте себестоимость, расходы и маржинальность."
        else:
            insight += "Рентабельность в норме. Следите за динамикой."

    # Выручка
    elif "Выручка" in metric:
        if value < total_avg * threshold:
            insight += "Выручка ниже средней. Проверьте трафик и конверсию."
        else:
            insight += "Выручка в норме. Следите за маржой и ценовой политикой."

    # ФОТ
    elif "ФОТ" in metric:
        if value > total_avg * 1.2:
            insight += "ФОТ завышен. Проверьте численность персонала и часы работы."
        else:
            insight += "ФОТ в норме. Следите, чтобы рос с выручкой и не превышал допустимый уровень."

    # Маржа
    elif "Марж" in metric or "маржинальная" in metric.lower():
        if value < total_avg * threshold:
            insight += "Маржинальная прибыль ниже средней. Сравните структуру товарных групп."
        else:
            insight += "Маржинальная прибыль в норме. Следите за списаниями."

    else:
        insight += "Метрика в норме. Следите за динамикой по месяцам."

    insight += "</div>"
    return insight


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


# --- Список секций (как панели) ---
panel_options = [
    "📈 Обзор сети",
    "📉 Динамика по месяцам",
    "📊 Сравнение ТО",
    "🔍 Детализация по ТО",
    "💡 Рекомендации"
]

# --- Выбор панели ─ как навигация между страницами/панелями ---
selected_panel = st.sidebar.radio(
    "Выберите панель",
    panel_options,
    key="panel_selector"
)

# --- Секция 1: Обзор сети ---
if selected_panel == "📈 Обзор сети":
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("### 📊 Обзор сети")

    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        core_metrics = [
            "Выручка б/НДС",
            "Себестоимость б/ндс",
            "Марж прибыль",
            "Рентабельность 1",
            "Доля ФОТ в выручке, %"
        ]
        total = data[core_metrics[0]].sum()
        total_avg = data[core_metrics[0]].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("Суммарная выручка", f"{total:,.2f}")
        col2.metric("Средняя выручка по ТО", f"{total_avg:,.2f}")
        col3.metric("Количество ТО", f"{len(data['ТО'].unique())}")

        by_store = data.groupby("ТО", as_index=False)[core_metrics[0]].sum()
        st.bar_chart(by_store.set_index("ТО"))

    st.markdown("</div>", unsafe_allow_html=True)


# --- Секция 2: Динамика по месяцам ---
if selected_panel == "📉 Динамика по месяцам":
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("### 📈 Динамика по месяцам")

    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        metric = st.selectbox("Метрика", [
            "Выручка б/НДС",
            "Себестоимость б/ндс",
            "Марж прибыль",
            "Рентабельность 1",
            "Доля ФОТ в выручке, %"
        ], key="dyn_metric")

        by_month = data.groupby("Месяц", as_index=False)[metric].sum()
        st.line_chart(by_month.set_index("Месяц"))

    st.markdown("</div>", unsafe_allow_html=True)


# --- Секция 3: Сравнение ТО ---
if selected_panel == "📊 Сравнение ТО":
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("### 📊 Сравнение выбранных ТО")

    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        selected_metric = st.selectbox("Метрика", [
            "Выручка б/НДС",
            "Себестоимость б/ндс",
            "Марж прибыль",
            "Рентабельность 1",
            "Доля ФОТ в выручке, %"
        ], key="comp_metric")

        by_store = data.groupby("ТО", as_index=False)[selected_metric].sum()
        st.bar_chart(by_store.set_index("ТО"))

    st.markdown("</div>", unsafe_allow_html=True)


# --- Секция 4: Детализация по ТО ---
if selected_panel == "🔍 Детализация по ТО":
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("### 🔍 Детализация по одному ТО")

    if len(data) == 0:
        st.info("Нет данных по выбранным фильтрам.")
    else:
        selected_store = st.selectbox("ТО", all_stores, key="detail_store")

        store_data = data[data["ТО"] == selected_store]
        if len(store_data) == 0:
            st.info("Нет данных для выбранного ТО.")
        else:
            st.dataframe(store_data[["Месяц"] + [
                "Выручка б/НДС",
                "Себестоимость б/ндс",
                "Марж прибыль",
                "Рентабельность 1",
                "Доля ФОТ в выручке, %"
            ]].round(2), height=400)

            st.markdown("---")

            # Подсказки по метрикам для этого ТО
            total_avg = store_data["Выручка б/НДС"].mean()
            for metric in ["Выручка б/НДС", "Рентабельность 1", "Марж прибыль"]:
                value = store_data[metric].sum()
                st.markdown(
                    generate_insights(df, metric, value, total_avg, store=selected_store),
                    unsafe_allow_html=True
                )

    st.markdown("</div>", unsafe_allow_html=True)


# --- Секция 5: Рекомендации (Аналитик) ---
if selected_panel == "💡 Рекомендации":
    st.markdown("<div class='section-block'>", unsafe_allow_html=True)
    st.markdown("### 💡 Рекомендации по метрикам")

    if len(selected_stores) == 0:
        st.info("Выберите хотя бы одно ТО в боковой панели.")
    else:
        selected_metric = st.selectbox("Метрика для анализа", [
            "Выручка б/НДС",
            "Себестоимость б/ндс",
            "Марж прибыль",
            "Рентабельность 1",
            "Доля ФОТ в выручке, %"
        ], key="rec_metric")

        total_avg = data[selected_metric].mean()

        for store in selected_stores:
            store_data = data[data["ТО"] == store]
            value = store_data[selected_metric].sum() if len(store_data) > 0 else 0
            st.markdown(
                generate_insights(df, selected_metric, value, total_avg, store),
                unsafe_allow_html=True
            )

    st.markdown("</div>", unsafe_allow_html=True)
