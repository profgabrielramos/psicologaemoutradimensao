import streamlit as st
import datetime
from utils import (
    download_ephe_files, get_location_data, calculate_julian_day,
    get_planet_positions, calculate_houses
)
from chart_generator import create_wheel_chart, PLANET_NAMES

# Símbolos e nomes dos signos do zodíaco
ZODIAC_SYMBOLS = {
    "Áries": "♈",
    "Touro": "♉",
    "Gêmeos": "♊",
    "Câncer": "♋",
    "Leão": "♌",
    "Virgem": "♍",
    "Libra": "♎",
    "Escorpião": "♏",
    "Sagitário": "♐",
    "Capricórnio": "♑",
    "Aquário": "♒",
    "Peixes": "♓"
}

def calcular_signo(longitude):
    signo = ""
    if 0 <= longitude < 30:
        signo = "Áries"
    elif 30 <= longitude < 60:
        signo = "Touro"
    elif 60 <= longitude < 90:
        signo = "Gêmeos"
    elif 90 <= longitude < 120:
        signo = "Câncer"
    elif 120 <= longitude < 150:
        signo = "Leão"
    elif 150 <= longitude < 180:
        signo = "Virgem"
    elif 180 <= longitude < 210:
        signo = "Libra"
    elif 210 <= longitude < 240:
        signo = "Escorpião"
    elif 240 <= longitude < 270:
        signo = "Sagitário"
    elif 270 <= longitude < 300:
        signo = "Capricórnio"
    elif 300 <= longitude < 330:
        signo = "Aquário"
    elif 330 <= longitude < 360:
        signo = "Peixes"
    return signo

# Configuração da página
st.set_page_config(
    page_title="Visualizador de Mapa Astral",
    page_icon="🌟",
    layout="wide"
)

# Carregar CSS personalizado
with open("styles/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicializar arquivos de efemérides
if not download_ephe_files():
    st.error("Falha ao inicializar dados astronômicos. Por favor, tente novamente.")
    st.stop()

# Título e descrição
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 class='glow-text'>✨ Visualizador de Mapa Astral ✨</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='cosmic-card'>
    <p style='text-align: center; font-size: 1.2rem;'>
        Descubra seu mapa astral através deste visualizador interativo.<br>
        Insira seus dados de nascimento abaixo para revelar as posições celestiais no momento do seu nascimento.
    </p>
</div>
""", unsafe_allow_html=True)

# Formulário de entrada
st.markdown("<div class='cosmic-card'>", unsafe_allow_html=True)
with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        birth_date = st.date_input(
            "Data de Nascimento",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
            help="Selecione sua data de nascimento"
        )

    with col2:
        birth_time = st.time_input(
            "Hora de Nascimento",
            help="Insira o horário mais preciso possível"
        )

    with col3:
        birth_place = st.text_input(
            "Local de Nascimento",
            placeholder="Ex: São Paulo, Brasil",
            help="Digite a cidade e país de nascimento"
        )

if st.button("✨ Gerar Mapa Astral ✨", key="generate"):
    try:
        with st.spinner("🌟 Calculando posições celestiais..."):
            location_data = get_location_data(birth_place)
            jd = calculate_julian_day(birth_date, birth_time, location_data['timezone'])
            planet_positions = get_planet_positions(jd)
            houses = calculate_houses(
                jd,
                location_data['latitude'],
                location_data['longitude']
            )

            # Calcular signo solar
            signo_solar = calcular_signo(planet_positions['Sun']['longitude'])
            simbolo_solar = ZODIAC_SYMBOLS[signo_solar]

            st.markdown("<div style='text-align: center;'><h2 class='glow-text'>Seu Mapa Astral</h2></div>", unsafe_allow_html=True)

            # Destaque do Signo Solar
            st.markdown(f"""
            <div class='cosmic-card signo-solar-card'>
                <div class='signo-symbol'>{simbolo_solar}</div>
                <h2 class='signo-nome'>{signo_solar}</h2>
                <p class='signo-grau'>{planet_positions['Sun']['longitude']:.2f}°</p>
            </div>
            """, unsafe_allow_html=True)

            chart_col, info_col = st.columns([2, 1])

            with chart_col:
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                fig = create_wheel_chart(planet_positions, houses)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with info_col:
                st.markdown("<div class='cosmic-card'>", unsafe_allow_html=True)
                st.markdown("<h3>🌍 Posições Planetárias</h3>", unsafe_allow_html=True)
                for planet, data in planet_positions.items():
                    planet_name = PLANET_NAMES.get(planet, planet)  # Usar nome traduzido
                    st.write(f"✨ {planet_name}: {data['longitude']:.2f}°")

                st.markdown("<h3>🏠 Cúspides das Casas</h3>", unsafe_allow_html=True)
                for i, cusp in enumerate(houses['cusps'], 1):
                    st.write(f"Casa {i}: {cusp:.2f}°")
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='cosmic-card'>", unsafe_allow_html=True)
                st.markdown("<h3>🌟 Pontos Importantes</h3>", unsafe_allow_html=True)
                st.write(f"⭐ Ascendente: {houses['ascendant']:.2f}°")
                st.write(f"🌠 Meio do Céu: {houses['mc']:.2f}°")
                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocorreu um erro: {str(e)}")

# Rodapé
st.markdown("""
<div class='cosmic-card' style='text-align: center; margin-top: 2rem;'>
    <p>Feito com ✨ e energia cósmica</p>
</div>
""", unsafe_allow_html=True)