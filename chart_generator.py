import plotly.graph_objects as go
import numpy as np

THEME_COLORS = {
    'dark': {
        'background': 'rgba(28, 28, 28, 0.95)',
        'primary': '#9C27B0',
        'accent': '#FF4081',
        'text': '#FFFFFF',
        'grid': 'rgba(156, 39, 176, 0.2)',
        'line': 'rgba(156, 39, 176, 0.5)'
    },
    'light': {
        'background': 'rgba(255, 255, 255, 0.95)',
        'primary': '#7B1FA2',
        'accent': '#E91E63',
        'text': '#333333',
        'grid': 'rgba(123, 31, 162, 0.2)',
        'line': 'rgba(123, 31, 162, 0.5)'
    }
}

# Dicionário de tradução para os nomes dos planetas
PLANET_NAMES = {
    'Sun': 'Sol',
    'Moon': 'Lua',
    'Mercury': 'Mercúrio',
    'Venus': 'Vênus',
    'Mars': 'Marte',
    'Jupiter': 'Júpiter',
    'Saturn': 'Saturno',
    'Uranus': 'Urano',
    'Neptune': 'Netuno',
    'Pluto': 'Plutão'
}

# Dicionário de símbolos dos signos
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

def calcular_signo(graus):
    """Converte uma posição em graus para o signo correspondente."""
    signos = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", 
              "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]
    grau_normalizado = graus % 360
    indice = int(grau_normalizado // 30)
    return signos[indice]

def create_wheel_chart(planet_positions, houses, theme='dark'):
    """Gera um gráfico interativo do mapa astral usando Plotly."""
    colors = THEME_COLORS[theme]

    # Criar o círculo base
    theta = np.linspace(0, 2*np.pi, 360)
    r = np.ones_like(theta)

    # Criar a figura
    fig = go.Figure()

    # Adicionar o círculo principal
    fig.add_trace(go.Scatterpolar(
        r=r,
        theta=np.degrees(theta),
        mode='lines',
        line=dict(color=colors['primary'], width=2),
        showlegend=False,
        fill='toself',
        fillcolor=colors['background']
    ))

    # Adicionar linhas das casas
    for house in houses['cusps']:
        angle = house
        fig.add_trace(go.Scatterpolar(
            r=[0, 1],
            theta=[angle, angle],
            mode='lines',
            line=dict(color=colors['line'], width=1),
            showlegend=False
        ))

    # Adicionar o signo solar com destaque
    sun_longitude = planet_positions['Sun']['longitude']
    sun_sign = calcular_signo(sun_longitude)
    fig.add_trace(go.Scatterpolar(
        r=[0.9],
        theta=[sun_longitude],
        mode='text',
        text=[f"{sun_sign} {ZODIAC_SYMBOLS[sun_sign]}"],
        textposition="middle center",
        textfont=dict(
            color=colors['text'],
            size=24,
            family="Arial"
        ),
        showlegend=False
    ))


    # Adicionar planetas
    for planet, data in planet_positions.items():
        if planet != 'Sun': #Avoid duplicating Sun
            planet_name = PLANET_NAMES.get(planet, planet)  # Usar nome traduzido
            fig.add_trace(go.Scatterpolar(
                r=[0.8],
                theta=[data['longitude']],
                mode='markers+text',
                name=planet_name,
                text=[planet_name],
                textposition="top center",
                textfont=dict(
                    color=colors['text'],
                    size=16,  # Aumentado o tamanho da fonte
                    family="Arial"  # Fonte mais legível
                ),
                marker=dict(
                    size=18,  # Aumentado o tamanho do marcador
                    color=colors['accent'],
                    symbol='star',
                    line=dict(
                        color=colors['text'],
                        width=1
                    )
                ),
                showlegend=True
            ))

    # Atualizar layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, 1]
            ),
            angularaxis=dict(
                direction="clockwise",
                period=360,
                rotation=90,
                tickmode='array',
                ticktext=['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'],
                tickvals=np.arange(0, 360, 30),
                tickfont=dict(
                    size=24,  # Aumentado o tamanho dos símbolos zodiacais
                    color=colors['text']
                ),
                gridcolor=colors['grid'],
                linecolor=colors['line']
            ),
            bgcolor=colors['background']
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            bgcolor=colors['background'],
            bordercolor=colors['primary'],
            borderwidth=1,
            font=dict(
                color=colors['text'],
                size=14,
                family="Arial"
            ),
            itemsizing='constant',
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.1,
            title=dict(
                text="Planetas",
                font=dict(
                    size=16,
                    family="Arial",
                    color=colors['text']
                )
            )
        ),
        margin=dict(l=20, r=120, t=20, b=20),  # Ajustado para acomodar a legenda
        height=800
    )

    return fig