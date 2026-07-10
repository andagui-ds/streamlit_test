import scipy.stats
import streamlit as st
import time
import pandas as pd

st.header('Lanzar una moneda')

# Inicializamos el gráfico con un DataFrame para asegurar la compatibilidad de add_rows
chart = st.line_chart(pd.DataFrame([0.5], columns=['Media']))

def toss_coin(n): 
    trial_outcomes = scipy.stats.bernoulli.rvs(p=0.5, size=n)

    mean = None
    outcome_no = 0
    outcome_1_count = 0

    for r in trial_outcomes:
        outcome_no += 1
        if r == 1:
            outcome_1_count += 1
        mean = outcome_1_count / outcome_no
        
        # Pasamos el dato nuevo en el mismo formato de DataFrame
        chart.add_rows(pd.DataFrame([mean], columns=['Media']))
        time.sleep(0.05)

    return mean

number_of_trials = st.slider('¿Número de intentos?', 1, 1000, 10)
start_button = st.button('Ejecutar')

if start_button:
    st.write(f'Experimento con {number_of_trials} intentos en curso.')
    mean = toss_coin(number_of_trials)