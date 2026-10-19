import numpy as np
import pandas as pd
import plotly.express as px
import scipy.stats
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Configuración de la Aplicación
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Simulador: Ley de los Grandes Números",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos personalizados para mejorar el diseño de tarjetas de métricas
st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. Inicialización de Session State
# -----------------------------------------------------------------------------
if "experiment_no" not in st.session_state:
    st.session_state["experiment_no"] = 0

if "experiment_history" not in st.session_state:
    st.session_state["experiment_history"] = []

# -----------------------------------------------------------------------------
# 3. Barra Lateral (Parámetros y Controles)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Controles")

    st.subheader("Configuración")
    number_of_trials = st.slider(
        "Número de lanzamientos",
        min_value=10,
        max_value=10000,
        value=500,
        step=50,
        help="Selecciona cuántas veces se lanzará la moneda en este experimento.",
    )

    animate = st.checkbox(
        "Mostrar animación",
        value=True,
        help="Desactiva para renderizar instantáneamente cuando Uses más de 1,000 lanzamientos.",
    )

    st.markdown("---")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        start_button = st.button(
            "🚀 Ejecutar", type="primary", use_container_width=True
        )
    with col_btn2:
        clear_button = st.button("🗑️ Limpiar", use_container_width=True)

    if clear_button:
        st.session_state["experiment_no"] = 0
        st.session_state["experiment_history"] = []
        st.rerun()

# -----------------------------------------------------------------------------
# 4. Encabezado Principal
# -----------------------------------------------------------------------------
st.title("🪙 Simulación: Ley de los Grandes Números")
st.markdown(
    """
Esta aplicación demuestra de manera interactiva cómo la **frecuencia relativa** de un evento (lanzamiento de una moneda justa) 
converge hacia su **probabilidad teórica ($p = 0.5$)** a medida que se incrementa el número de repeticiones.
"""
)

chart_placeholder = st.empty()


# -----------------------------------------------------------------------------
# 5. Función de Simulación Optimizada
# -----------------------------------------------------------------------------
def run_coin_simulation(n: int, show_animation: bool):
    # Generación vectorizada rápida con Bernoulli
    outcomes = scipy.stats.bernoulli.rvs(p=0.5, size=n)

    # Cálculo acumulativo de la media en una sola operación
    cumulative_means = np.cumsum(outcomes) / np.arange(1, n + 1)
    df_trials = pd.DataFrame(
        {
            "Lanzamiento": np.arange(1, n + 1),
            "Media Acumulada": cumulative_means,
        }
    )

    def create_plotly_figure(data: pd.DataFrame):
        fig = px.line(
            data,
            x="Lanzamiento",
            y="Media Acumulada",
            title="Convergencia de la Media Acumulada hacia 0.5",
            labels={
                "Lanzamiento": "Número de Lanzamientos",
                "Media Acumulada": "Proporción de Soles / Águilas",
            },
        )
        # Línea de referencia teórica p = 0.5
        fig.add_hline(
            y=0.5,
            line_dash="dash",
            line_color="red",
            annotation_text="Probabilidad Teórica (0.5)",
            annotation_position="bottom right",
        )
        fig.update_yaxes(range=[0, 1])
        fig.update_layout(
            template="plotly_white",
            height=420,
            margin=dict(l=20, r=20, t=40, b=20),
        )
        return fig

    # Animación fluida por bloques para evitar sobrecargar el navegador
    if show_animation and n <= 2000:
        step_size = max(1, n // 40)
        for i in range(1, n + 1, step_size):
            chart_placeholder.plotly_chart(
                create_plotly_figure(df_trials.iloc[:i]),
                use_container_width=True,
            )

    # Renderizado final completo
    chart_placeholder.plotly_chart(
        create_plotly_figure(df_trials), use_container_width=True
    )

    return float(cumulative_means[-1])


# Estado gráfico inicial si aún no se ha ejecutado nada
if not start_button and len(st.session_state["experiment_history"]) == 0:
    df_init = pd.DataFrame({"Lanzamiento": [1], "Media Acumulada": [0.5]})
    fig_init = px.line(
        df_init,
        x="Lanzamiento",
        y="Media Acumulada",
        title="Convergencia de la Media Acumulada hacia 0.5",
    )
    fig_init.add_hline(y=0.5, line_dash="dash", line_color="red")
    fig_init.update_yaxes(range=[0, 1])
    fig_init.update_layout(template="plotly_white", height=420)
    chart_placeholder.plotly_chart(fig_init, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. Lógica de Ejecución y Registro
# -----------------------------------------------------------------------------
if start_button:
    st.session_state["experiment_no"] += 1

    with st.spinner("Ejecutando simulación..."):
        final_mean = run_coin_simulation(
            number_of_trials, show_animation=animate
        )

    # Guardar en el historial de sesión (usando lista de diccionarios)
    st.session_state["experiment_history"].append(
        {
            "Experimento #": st.session_state["experiment_no"],
            "Lanzamientos": number_of_trials,
            "Media Final": round(final_mean, 4),
            "Diferencia vs 0.5": round(abs(0.5 - final_mean), 4),
        }
    )

# -----------------------------------------------------------------------------
# 7. Dashboard y Tarjetas de Métricas
# -----------------------------------------------------------------------------
if st.session_state["experiment_history"]:
    st.markdown("---")
    st.subheader("📊 Resumen del Historial")

    df_history = pd.DataFrame(st.session_state["experiment_history"])

    # Tarjetas de métricas rápidas
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.metric(label="Experimentos Evaluados", value=len(df_history))

    with col_m2:
        ultima_media = df_history["Media Final"].iloc[-1]
        st.metric(
            label="Última Media Obtendida",
            value=ultima_media,
            delta=round(ultima_media - 0.5, 4),
        )

    with col_m3:
        promedio_global = round(df_history["Media Final"].mean(), 4)
        st.metric(
            label="Media Global Promedio",
            value=promedio_global,
            delta=round(promedio_global - 0.5, 4),
        )

    with col_m4:
        total_lanzamientos = df_history["Lanzamientos"].sum()
        st.metric(
            label="Total Lanzamientos Acumulados",
            value=f"{total_lanzamientos:,}",
        )

    # Tabla interactiva ordenada por el más reciente
    st.dataframe(
        df_history.sort_values(by="Experimento #", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
