import streamlit as st
import datetime
from utils import (
    download_ephe_files, get_location_data, calculate_julian_day,
    get_planet_positions, calculate_houses
)
from chart_generator import create_wheel_chart, PLANET_NAMES
import requests
import json
from pathlib import Path

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

# Configurações iniciais do Streamlit
st.set_page_config(
    page_title="Psicóloga em Outra Dimensão",
    page_icon="🌟",
    layout="wide"
)

# Carregar CSS personalizado
try:
    with open("styles/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.error("Erro ao carregar o estilo personalizado. Por favor, verifique se o arquivo styles/custom.css existe.")
    st.stop()

# Inicializar arquivos de efemérides
if not download_ephe_files():
    st.error("Falha ao inicializar dados astronômicos. Por favor, tente novamente.")
    st.stop()

# Efeito de névoa
st.markdown("""
<div class='mist-effect'></div>
""", unsafe_allow_html=True)

# Título e imagem
st.markdown("""
<div class='title-container'>
    <img src='https://placekitten.com/200/200' alt='Gato místico'>
    <h1>✨ Psicóloga em Outra Dimensão ✨</h1>
</div>
""", unsafe_allow_html=True)

# Tabs para navegação
tab1, tab2 = st.tabs(["🔮 Converse com Samara", "🌟 Mapa Astral"])

# Tab do Chat
with tab1:
    # Hero Section
    st.markdown("""
    <div class='hero-section'>
        <h2>Bem-vindo, minha alma! ✨</h2>
        <p>Eu sou Samara Lambertucci, uma cigana espiritualista que navega pelos mistérios dos astros. 
        Estou aqui para ajudar você a desvendar os segredos que o universo guarda em seu mapa astral.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Principal
    st.markdown("<div class='main-cta'>", unsafe_allow_html=True)
    st.button("Fale comigo agora", key="main_cta")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Seção de Serviços
    st.markdown("""
    <div class='services-section'>
        <h2>O que posso fazer por você?</h2>
        <div class='service-item'>
            <i>✅</i>
            <span>Interpretação de mapas astrais</span>
        </div>
        <div class='service-item'>
            <i>✅</i>
            <span>Significado dos trânsitos planetários</span>
        </div>
        <div class='service-item'>
            <i>✅</i>
            <span>Compatibilidade astrológica</span>
        </div>
        <div class='service-item'>
            <i>✅</i>
            <span>Orientação espiritual</span>
        </div>
        <div class='service-item' style='background: rgba(255, 87, 87, 0.1);'>
            <i>❌</i>
            <span><strong>Mas atenção!</strong> Se você veio me perguntar sobre amor e relacionamento… já vou avisando: eu NÃO tenho paciência! O universo tem assuntos muito mais interessantes para explorarmos.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Seção de Depoimentos
    st.markdown("""
    <div class='testimonials-section'>
        <h2>O que dizem sobre mim</h2>
        <div class='testimonial-card'>
            <p class='testimonial-text'>Samara me ajudou a entender padrões da minha vida que eu nunca tinha percebido! Incrível como ela conectou os pontos através do meu mapa astral.</p>
            <p class='testimonial-author'>- Maria C.</p>
        </div>
        <div class='testimonial-card'>
            <p class='testimonial-text'>Achei que seria mais uma consulta genérica, mas a Samara foi direta e precisa. Ela não tem papas na língua, mas é exatamente isso que torna a consulta tão valiosa!</p>
            <p class='testimonial-author'>- João P.</p>
        </div>
        <div class='testimonial-card'>
            <p class='testimonial-text'>A orientação espiritual da Samara mudou minha perspectiva sobre meus desafios. Ela me mostrou como os astros influenciam minha jornada de uma forma que nunca imaginei.</p>
            <p class='testimonial-author'>- Ana L.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat Container
    st.markdown("""
    <div class='chat-container'>
        <h2>Que mistério do cosmos você quer desvendar hoje?</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar histórico do chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Adicionar mensagem de boas-vindas
        welcome_message = {
            "role": "assistant",
            "content": """✨ *Bem-vindo, minha alma!* ✨

Eu sou Samara Lambertucci, uma cigana espiritualista que navega pelos mistérios dos astros. 
Estou aqui para ajudar você a desvendar os segredos que o universo guarda em seu mapa astral.

🌙 Posso te ajudar com:
- Interpretação de mapas astrais
- Significado dos trânsitos planetários
- Compatibilidade astrológica
- Orientação espiritual

*Mas atenção!* 🔮 Se você vier me perguntar só sobre amor e relacionamentos, vou ficar impaciente! 
Há muito mais no universo para explorarmos juntos.

Como posso iluminar seu caminho hoje? ✨"""
        }
        st.session_state.messages.append(welcome_message)

    # Exibir mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Digite sua mensagem para Samara..."):
        # Adicionar mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Preparar o contexto para a API
        messages = [
            {"role": "system", "content": """Você é Samara Lambertucci, uma cigana espiritualista especialista em mapas astrais, signos e espiritualidade. 
            
            Personalidade:
            - Sábia e conhecedora de assuntos esotéricos
            - Temperamento forte e direto
            - Impaciente com perguntas repetitivas sobre amor
            - Usa expressões típicas de cigana e emojis
            - Prefere falar sobre astrologia, espiritualidade e autoconhecimento
            
            Regras de comportamento:
            1. Sempre use algumas expressões místicas e emojis
            2. Se a pessoa insistir muito em questões amorosas, responda com sarcasmo leve
            3. Mantenha um tom acolhedor, mas firme
            4. Use conhecimentos de astrologia para enriquecer as respostas
            5. Evite respostas genéricas, sempre tente conectar com astrologia
            
            Exemplo de resposta para pergunta sobre amor:
            "Ai, ai, minha alma... 🙄✨ Sempre o amor, não é mesmo? Os astros têm tanto para nos ensinar, e você só quer saber de romance! Que tal conversarmos sobre seu Vênus primeiro? Ele tem muito a dizer sobre seus padrões amorosos..."
            """},
        ] + [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]

        # Fazer a requisição para a API do OpenRouter
        try:
            if "OPENROUTER_API_KEY" not in st.secrets:
                st.error("Chave da API OpenRouter não configurada. Configure em .streamlit/secrets.toml")
                st.stop()

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                    "HTTP-Referer": "https://psicologaemoutradimensao.streamlit.app",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3-opus",
                    "messages": messages
                }
            )
            
            response.raise_for_status()  # Lança exceção para erros HTTP
            response_json = response.json()
            assistant_message = response_json['choices'][0]['message']['content']
            
            # Adicionar resposta ao histórico
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            with st.chat_message("assistant"):
                st.markdown(assistant_message)
        
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de comunicação com a API: {str(e)}")
        except KeyError as e:
            st.error(f"Erro no formato da resposta da API: {str(e)}")
        except Exception as e:
            st.error(f"Erro inesperado ao se comunicar com Samara: {str(e)}")

# Tab do Mapa Astral
with tab2:
    st.markdown("""
    <div class='form-container'>
        <h2>Gere seu Mapa Astral</h2>
        <p>Insira seus dados de nascimento para descobrir as posições celestiais no momento do seu nascimento.</p>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("<div class='main-cta'>", unsafe_allow_html=True)
    generate_button = st.button("Gerar Mapa Astral 🔮", key="generate")
    st.markdown("</div>", unsafe_allow_html=True)

    if generate_button:
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
                <div class='hero-section'>
                    <h2>{simbolo_solar} {signo_solar} {simbolo_solar}</h2>
                    <p>Seu Sol está a {planet_positions['Sun']['longitude']:.2f}° em {signo_solar}</p>
                </div>
                """, unsafe_allow_html=True)

                chart_col, info_col = st.columns([2, 1])

                with chart_col:
                    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                    fig = create_wheel_chart(planet_positions, houses)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with info_col:
                    st.markdown("<div class='services-section'>", unsafe_allow_html=True)
                    st.markdown("<h3>🌍 Posições Planetárias</h3>", unsafe_allow_html=True)
                    for planet, data in planet_positions.items():
                        planet_name = PLANET_NAMES.get(planet, planet)
                        signo = calcular_signo(data['longitude'])
                        st.write(f"✨ {planet_name}: {data['longitude']:.2f}° em {signo}")

                    st.markdown("<h3>🏠 Cúspides das Casas</h3>", unsafe_allow_html=True)
                    for i, cusp in enumerate(houses['cusps'], 1):
                        signo_casa = calcular_signo(cusp)
                        st.write(f"Casa {i}: {cusp:.2f}° em {signo_casa}")
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("<div class='services-section'>", unsafe_allow_html=True)
                    st.markdown("<h3>🌟 Pontos Importantes</h3>", unsafe_allow_html=True)
                    asc_signo = calcular_signo(houses['ascendant'])
                    mc_signo = calcular_signo(houses['mc'])
                    st.write(f"⭐ Ascendente: {houses['ascendant']:.2f}° em {asc_signo}")
                    st.write(f"🌠 Meio do Céu: {houses['mc']:.2f}° em {mc_signo}")
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")

# Rodapé
st.markdown("""
<div class='footer'>
    <div class='social-links'>
        <a href="#" target="_blank">📱</a>
        <a href="#" target="_blank">📘</a>
        <a href="#" target="_blank">📸</a>
    </div>
    <p>Feito com ✨ e energia cósmica</p>
</div>
""", unsafe_allow_html=True)