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


# --- Загрузка данных (глобально) ---
df = None

def load_df():
    global df
    if df is None:
        df = load_data()
    return df


# --- Стиль: лайтовый, «сайтовый» UI ---
st.markdown("""
<style>
    .stApp {
        background: #ffffff;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }

    /* Лендинг‑блок */
    .landing-card {
        background: #f9f9fb;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
        margin-bottom: 24px;
    }

    .landing-title {
        font-size: 38px;
        font-weight: 600;
        color: #1976d2;
        margin-bottom: 10px;
    }

    .landing-subtitle {
        font-size: 18px;
        color: #555;
    }

    .landing-btn {
        background: #1976d2;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-align: center;
        display: inline-block;
        cursor: pointer;
    }

    .landing-btn:hover {
        background: #1565c0;
    }

    /* Панель аналитики */
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

    /* KPI */
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

    /* Карточки подсказок */
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


# --- Страницы приложения ---
if "page" not in st.session_state:
    st.session_state.page = "landing"

if "selected_panel" not in st.session_state:
    st.session_state.selected_panel = "📊 Обзор сети"

if "selected_metric" not in st.session_state:
    st.session_state.selected_metric = "Выручка б/НДС"


# --- Функция генерации подсказок ---
def generate_insights(metric, value, total_avg, store="ТО", threshold=0.8):
    insight = f"<div class='suggestion-box'><div style='font-weight:600; color: #1976d2;'>💡 Рекомендация для ТО: {store}</div>"

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
            insight += "ФОТ в допустимом диапазоне. Следите, чтобы рост выручки не сопровождался быстрым ростом ФОТ."

    elif "Марж" in metric:
        if value < total_avg * threshold:
            insight += "Маржинальная прибыль ниже средней. Сравните доли проды, скоропорта и непроды — возможно, низкомаржинальные группы доминируют."
        else:
            insight += "Маржинальная прибыль в норме. Следите за списаниями и структурой закупок."

    else:
        insight += "Метрика в норме. Следите за динамикой по месяцам."

    insight += "</div>"
    return insight


# === ЛЕНДИНГ ===
if st.session_state.page == "landing":
    st.markdown("""
        <div class='landing-card'>
            <div class='landing-title'>📊 Розничная сеть «ТО»</div>
            <div class='landing-subtitle'>
                Автоматизированная аналитическая платформа для управления выручкой, маржой, рентабельностью и эффективностью торговых объектов.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='landing-card'>
            <h3>🎯 Возможности</h3>
            <p>
                <b>Обзор сети</b>: ключевые KPI по выручке и рентабельности.<br>
                <b>Динамика по месяцам</b>: тренды выручки, маржи и ФОТ.<br>
                <b>Сравнение ТО</b>: выявляйте сильные и слабые точки сети.<br>
                <b>Интеллектуальные рекомендации</b>: советы по улучшению показателей.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='landing-card'>
            <h3>👥 Для кого</h3>
            <p>
                Для руководителей торговых сетей, директоров по анализу и операционным менеджерам.<br>
                Помогает принимать решения по структуре сети, мерчандайзингу, персоналу и маркетингу.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Кнопка входа через Streamlit
    if st.button("🚀 Войти в Analytics", key="nav_analytics"):
        st.session_state.page = "analytics"
        st.rerun()


# === ПАНЕЛЬ АНАЛИТИКИ (с ИИ‑чатом) ===
elif st.session_state.page == "analytics":
    df = load_df()
    metrics_list = ["Выручка б/НДС", "Себестоимость б/ндс", "Марж прибыль", "Рентабельность 1", "Доля ФОТ в выручке, %"]


    # --- Боковая панель: навигация + ИИ‑чат ---
    with st.sidebar:
        st.markdown("<h3 style='color:#1976d2;'>🎯 Панель BI</h3>", unsafe_allow_html=True)

        # Навигация по панелям
        nav_options = ["📊 Обзор сети", "📉 Динамика", "🌍 Сравнение ТО", "💡 Рекомендации"]
        selected_nav = st.radio("**Выберите раздел**", nav_options, index=0)

        # Фильтры
        st.divider()
        st.markdown("### ⚙️ Фильтры", unsafe_allow_html=True)

        all_stores = sorted(df["ТО"].dropna().unique().tolist())
        st.session_state.selected_stores = st.multiselect(
            "ТО",
            all_stores,
            default=all_stores[:3] if all_stores else []
        )

        months = sorted(df["Месяц"].dropna().unique().tolist())
        st.session_state.selected_month = st.selectbox("Месяц", ["Все"] + months)

        placements = sorted(df["Размещение"].dropna().unique().tolist())
        st.session_state.selected_placement = st.selectbox("Размещение", ["Все"] + placements)

        types = sorted(df["Тип ТО"].dropna().unique().tolist())
        st.session_state.selected_type = st.selectbox("Тип ТО", ["Все"] + types)


        # --- ИИ‑Ассистент (словесный) ---
        st.divider()
        st.markdown("### 💬 ИИ‑Ассистент по запросам")

        user_query = st.text_area(
            "Что вы хотите узнать?",
            placeholder="Например: «покажи топ‑3 ТО по выручке» или «ТО с низкой рентабельностью»...",
            value=st.session_state.get("last_query", "")
        )

        if user_query:
            query_low = user_query.lower()
            st.session_state.last_query = user_query

            # Обновляем стейт и панель по запросу
            if "выручка" in query_low and "топ" in query_low:
                st.session_state.selected_panel = "📊 Обзор сети"
                st.session_state.selected_metric = "Выручка б/НДС"
                st.info("↕️ Панель переключена: **Обзор сети** по выручке.")
            elif "рентабельность" in query_low:
                if "низкая" in query_low:
                    st.session_state.selected_panel = "💡 Рекомендации"
                    st.session_state.selected_metric = "Рентабельность 1"
                    st.info("↕️ Панель переключена: **Рекомендации** по рентабельности.")
                else:
                    st.session_state.selected_panel = "📉 Динамика"
                    st.session_state.selected_metric = "Рентабельность 1"
                    st.info("↕️ Панель переключена: **Динамика** по рентабельности.")
            elif "фот" in query_low:
                st.session_state.selected_panel = "🌍 Сравнение ТО"
                st.session_state.selected_metric = "Доля ФОТ в выручке, %"
                st.info("↕️ Панель переключена: **Сравнение ТО** по ФОТ.")
            elif "сравни" in query_low:
                st.session_state.selected_panel = "🌍 Сравнение ТО"
                st.session_state.selected_metric = "Выручка б/НДС"
                st.info("↕️ Панель: **Сравнение ТО** по выручке.")
            else:
                st.info("🌀 Пока не распознан запрос, но данные показаны по текущим фильтрам.")

            st.rerun()


    # --- Фильтрация данных ---
    data = df.copy()
    if "selected_stores" in st.session_state and st.session_state.selected_stores:
        data = data[data["ТО"].isin(st.session_state.selected_stores)]
    if st.session_state.selected_month != "Все":
        data = data[data["Месяц"] == st.session_state.selected_month]
    if st.session_state.selected_placement != "Все":
        data = data[data["Размещение"] == st.session_state.selected_placement]
    if st.session_state.selected_type != "Все":
        data = data[data["Тип ТО"] == st.session_state.selected_type]


    # --- Панель 1: Обзор сети ---
    if st.session_state.selected_panel == "📊 Обзор сети":
        st.markdown("<div class='panel-section'><div class='panel-title'>📊 Обзор сети</div>", unsafe_allow_html=True)

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            metric = st.session_state.selected_metric
            total = data[metric].sum()
            total_avg = data[metric].mean()

            col1, col2, col3 = st.columns(3)
            col1.metric("Суммарная выручка", f"{total:,.2f}")
            col2.metric("Средняя по ТО", f"{total_avg:,.2f}")
            col3.metric("Количество ТО", f"{len(data['ТО'].unique())}")

            st.markdown("---")

            by_store = data.groupby("ТО", as_index=False)[metric].sum()
            st.bar_chart(by_store.set_index("ТО"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 2: Динамика по месяцам ---
    if st.session_state.selected_panel == "📉 Динамика":
        st.markdown("<div class='panel-section'><div class='panel-title'>📈 Динамика по месяцам</div>", unsafe_allow_html=True)

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            metric = st.session_state.selected_metric
            by_month = data.groupby("Месяц", as_index=False)[metric].sum()
            st.line_chart(by_month.set_index("Месяц"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 3: Сравнение ТО ---
    if st.session_state.selected_panel == "🌍 Сравнение ТО":
        st.markdown("<div class='panel-section'><div class='panel-title'>🌍 Сравнение выбранных ТО</div>", unsafe_allow_html=True)

        if len(data) == 0:
            st.info("Нет данных по выбранным фильтрам.")
        else:
            metric = st.session_state.selected_metric
            by_store = data.groupby("ТО", as_index=False)[metric].sum()
            st.bar_chart(by_store.set_index("ТО"))

        st.markdown("</div>", unsafe_allow_html=True)


    # --- Панель 4: Рекомендации ---
    if st.session_state.selected_panel == "💡 Рекомендации":
        st.markdown("<div class='panel-section'><div class='panel-title'>💡 Рекомендации по метрикам</div>", unsafe_allow_html=True)

        if not st.session_state.selected_stores:
            st.info("Выберите хотя бы одно ТО в боковой панели.")
        else:
            metric = st.session_state.selected_metric
            total_avg = data[metric].mean()

            for store in st.session_state.selected_stores:
                store_data = data[data["ТО"] == store]
                value = store_data[metric].sum() if len(store_data) > 0 else 0
                st.markdown(
                    generate_insights(metric, value, total_avg, store),
                    unsafe_allow_html=True
                )

        st.markdown("</div>", unsafe_allow_html=True)
