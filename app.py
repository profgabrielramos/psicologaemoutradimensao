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

# Função para o chat com Samara
def chat_with_samara(message):
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Adicionar mensagem de boas-vindas
        welcome_message = {
            "role": "assistant",
            "content": "Olá, sou Samara Lambertucci. Como posso ajudar você hoje?"
        }
        st.session_state.messages.append(welcome_message)
    
    if message:
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": message})
        
        # Preparar o contexto para a API
        messages = [
            {"role": "system", "content": """Você é Samara Lambertucci, uma cigana espiritualista especialista em mapas astrais, signos e espiritualidade. 
            Seja direta e concisa em suas respostas, mantendo-as curtas (máximo 2-3 frases).
            Você tem temperamento forte e é impaciente com perguntas sobre amor."""},
        ] + [
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ]

        # Fazer a requisição para a API do OpenRouter
        try:
            if "OPENROUTER_API_KEY" not in st.secrets:
                return "Erro: API não configurada."

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
            
            response.raise_for_status()
            response_json = response.json()
            assistant_message = response_json['choices'][0]['message']['content']
            
            # Adicionar resposta ao histórico
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            return assistant_message
        
        except Exception as e:
            return f"Erro: {str(e)}"
    
    return None

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

# Título e imagem
st.markdown("""
<div class='title-container'>
    <img src='https://placekitten.com/200/200' alt='Gato místico'>
    <h1>Psicóloga em Outra Dimensão</h1>
</div>
""", unsafe_allow_html=True)

# Tabs para navegação
tab1, tab2 = st.tabs(["🌟 Mapa Astral", "ℹ️ Sobre"])

# Tab do Mapa Astral
with tab1:
    st.markdown("""
    <div class='section'>
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
    generate_button = st.button("Gerar Mapa Astral", key="generate")
    st.markdown("</div>", unsafe_allow_html=True)

    if generate_button:
        try:
            with st.spinner("Calculando posições celestiais..."):
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

                st.markdown(f"""
                <div class='section'>
                    <h2>{simbolo_solar} Seu Sol está em {signo_solar}</h2>
                    <p>Posição exata: {planet_positions['Sun']['longitude']:.2f}°</p>
                </div>
                """, unsafe_allow_html=True)

                chart_col, info_col = st.columns([2, 1])

                with chart_col:
                    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                    fig = create_wheel_chart(planet_positions, houses)
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                with info_col:
                    st.markdown("<div class='section'>", unsafe_allow_html=True)
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

                    st.markdown("<div class='section'>", unsafe_allow_html=True)
                    st.markdown("<h3>🌟 Pontos Importantes</h3>", unsafe_allow_html=True)
                    asc_signo = calcular_signo(houses['ascendant'])
                    mc_signo = calcular_signo(houses['mc'])
                    st.write(f"⭐ Ascendente: {houses['ascendant']:.2f}° em {asc_signo}")
                    st.write(f"🌠 Meio do Céu: {houses['mc']:.2f}° em {mc_signo}")
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")

# Tab Sobre
with tab2:
    st.markdown("""
    <div class='section'>
        <h2>Sobre o Projeto</h2>
        <p>Este é um visualizador de mapas astrais que permite aos usuários gerar e explorar seus mapas astrais com base em sua data, hora e local de nascimento.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='section'>
        <h2>Serviços</h2>
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
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='section'>
        <h2>Depoimentos</h2>
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

# Popup da Samara
if "popup_open" not in st.session_state:
    st.session_state.popup_open = False
    
if "popup_message" not in st.session_state:
    st.session_state.popup_message = ""
    
# JavaScript para controlar o popup
js_code = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Criar o popup
    const popup = document.createElement('div');
    popup.className = 'samara-popup';
    popup.innerHTML = '🔮';
    document.body.appendChild(popup);
    
    // Criar o conteúdo do popup
    const popupContent = document.createElement('div');
    popupContent.className = 'samara-popup-content';
    popupContent.innerHTML = `
        <div class="samara-popup-close">×</div>
        <div class="samara-popup-header">
            <img src="https://placekitten.com/100/100" alt="Samara">
            <h3>Samara Lambertucci</h3>
        </div>
        <div class="samara-popup-messages" id="samara-messages">
            <div class="chat-message assistant-message">
                Olá, sou Samara Lambertucci. Como posso ajudar você hoje?
            </div>
        </div>
        <div class="samara-popup-input">
            <input type="text" id="samara-input" placeholder="Digite sua mensagem...">
            <button id="samara-send">Enviar</button>
        </div>
    `;
    document.body.appendChild(popupContent);
    
    // Adicionar eventos
    popup.addEventListener('click', function() {
        popupContent.classList.toggle('active');
    });
    
    document.querySelector('.samara-popup-close').addEventListener('click', function(e) {
        e.stopPropagation();
        popupContent.classList.remove('active');
    });
    
    // Função para enviar mensagem
    function sendMessage() {
        const input = document.getElementById('samara-input');
        const message = input.value.trim();
        
        if (message) {
            // Adicionar mensagem do usuário
            const messagesContainer = document.getElementById('samara-messages');
            messagesContainer.innerHTML += `
                <div class="chat-message user-message">
                    ${message}
                </div>
            `;
            
            // Limpar input
            input.value = '';
            
            // Rolar para o final
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            // Enviar para o backend via Streamlit
            const messageInput = document.createElement('input');
            messageInput.type = 'hidden';
            messageInput.id = 'samara-message-input';
            messageInput.value = message;
            document.body.appendChild(messageInput);
            
            // Disparar evento para o Streamlit
            const event = new Event('samaraMessage');
            document.dispatchEvent(event);
            
            // Mostrar indicador de digitação
            messagesContainer.innerHTML += `
                <div class="chat-message assistant-message" id="typing-indicator">
                    <em>Digitando...</em>
                </div>
            `;
        }
    }
    
    // Evento de envio
    document.getElementById('samara-send').addEventListener('click', sendMessage);
    document.getElementById('samara-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Receber resposta do Streamlit
    window.addEventListener('message', function(event) {
        const data = event.data;
        
        if (data.type === 'samaraResponse') {
            const messagesContainer = document.getElementById('samara-messages');
            
            // Remover indicador de digitação
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Adicionar resposta
            messagesContainer.innerHTML += `
                <div class="chat-message assistant-message">
                    ${data.message}
                </div>
            `;
            
            // Rolar para o final
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    });
});

// Função para verificar mensagens do usuário
function checkSamaraMessage() {
    const messageInput = document.getElementById('samara-message-input');
    if (messageInput) {
        const message = messageInput.value;
        messageInput.remove();
        
        // Enviar para o Streamlit
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: message
        }, '*');
        
        return message;
    }
    return null;
}

// Verificar periodicamente
setInterval(checkSamaraMessage, 500);
</script>
"""

st.markdown(js_code, unsafe_allow_html=True)

# Componente para receber mensagens do JavaScript
popup_message = st.empty()

# Processar mensagem se houver
if st.session_state.popup_message:
    response = chat_with_samara(st.session_state.popup_message)
    
    # Enviar resposta de volta para o JavaScript
    if response:
        st.markdown(
            f"""
            <script>
            window.parent.postMessage({{
                type: 'samaraResponse',
                message: '{response.replace("'", "\\'")}'
            }}, '*');
            </script>
            """,
            unsafe_allow_html=True
        )
    
    # Limpar a mensagem
    st.session_state.popup_message = ""