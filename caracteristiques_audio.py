from dash import Dash, html, dcc, Input, Output, ALL

# Dictionnaire des descriptions des caractéristiques audio avec des exemples de morceaux
explanations = {
    'acousticness': {
        'description': "Acousticness (acousticité) est une mesure de confiance (de 0.0 à 1.0) indiquant si le morceau est acoustique, c’est-à-dire joué principalement avec des instruments non électroniques. Une valeur de 1.0 signifie que le morceau est très probablement acoustique.",
        'high_example_name': "Oh My Love - John Lennon",
        'low_example_name': "Centless Apprentice - Nirvana"
    },
    'danceability': {
        'description': "Danceability (dansant) décrit dans quelle mesure un morceau est adapté à la danse, en se basant sur des éléments comme le tempo, la stabilité du rythme, la force de la pulsation et la régularité globale. Une valeur de 0.0 signifie que le morceau est peu dansant, tandis que 1.0 indique un morceau très dansant.",
        'high_example_name': "Ice Ice Baby - Vanilla Ice",
        'low_example_name': "Blue Ocean Floor - Justin Timberlake"
    },
    'duration_ms': {
        'description': "Duration (durée) mesure la longueur du morceau en millisecondes.",
        'high_example_name': "",
        'low_example_name': ""
    },
    'energy': {
        'description': "Energy (énergie) est une mesure de l'intensité et de l'activité ressenties dans un morceau, sur une échelle de 0.0 à 1.0. Des morceaux à haute énergie paraissent rapides, forts et parfois agressifs.",
        'high_example_name': "When Doves Cry - Prince",
        'low_example_name': "Let Her Go - Passenger"
    },
    'instrumentalness': {
        'description': "Instrumentalness (instrumentalité) prédit l'absence de voix chantée dans un morceau. Plus la valeur se rapproche de 1.0, plus le morceau est susceptible d'être instrumental.",
        'high_example_name': "Veridis Quo - Daft Punk",
        'low_example_name': "Hold Me While You Wait - Lewis Capaldi"
    },
    'liveness': {
        'description': "Liveness (en direct) détecte la présence d'un public dans l'enregistrement. Des valeurs élevées, notamment au-dessus de 0.8, suggèrent fortement que le morceau a été joué en live.",
        'high_example_name': "Silence - Marshmello",
        'low_example_name': "Finesse - Bruno Mars"
    },
    'loudness': {
        'description': "Loudness (intensité) mesure l'intensité sonore globale d'un morceau en décibels (dB). Les valeurs, généralement comprises entre -60 et 0 dB, permettent de comparer le volume relatif des morceaux.",
        'high_example_name': "C.U.B.A. - Calvin Harris",
        'low_example_name': "Englishman in New York - Sting"
    },
    'mode': {
        'description': "Mode (mode) indique la tonalité du morceau. Une valeur de 0 signifie un mode mineur, tandis qu'une valeur de 1 indique un mode majeur.",
        'high_example_name': "Closer - The Chainsmokers",
        'low_example_name': "Scared to be Lonely - Martin Garrix"
    },
    'speechiness': {
        'description': "Speechiness (le parlé) détecte la présence de paroles parlées dans un morceau. Des valeurs proches de 1.0 suggèrent un contenu fortement parlé (comme dans un podcast ou un spoken word), tandis que des valeurs faibles indiquent principalement de la musique.",
        'high_example_name': "Birdboy - NLE Choppa",
        'low_example_name': "The Best of My Love - Eagles"
    },
    'tempo': {
        'description': "Tempo correspond à la vitesse du morceau, exprimée en battements par minute (BPM), et détermine le rythme global du morceau.",
        'high_example_name': "Can't Stop - Red Hot Chili Peppers",
        'low_example_name': "imagine - Ariana Grande"
    },
    'valence': {
        'description': "Valence mesure le caractère émotionnel positif ou négatif d'un morceau sur une échelle de 0.0 à 1.0. Des valeurs élevées indiquent un ton joyeux et positif, tandis que des valeurs faibles évoquent un ton plus triste ou mélancolique.",
        'high_example_name': "Material Girl - Madonna",
        'low_example_name': "hostage - Billie Eilish"
    },
    
}


def get_feature_block(selected_key):
    feature_data = explanations[selected_key]
    explanation_block = [
        html.Div([
            html.P(html.B(selected_key.capitalize() + " :"), style={'marginBottom': '10px'}),
            html.P(feature_data['description'])
        ], style={'flex': '2'})
    ]

    if selected_key != 'duration_ms':
        explanation_block.extend([
            html.Div([
                html.P(html.B(f"Faible {selected_key} :"), style={'color': '#1DB954'}),
                html.P(feature_data['low_example_name']),
                html.Img(
                    src="/assets/icons/play_icon.png",
                    id={'type': 'audio-icon', 'index': f"{selected_key}-low"},
                    style={'width': '30px', 'cursor': 'pointer'}
                ),
                html.Audio(
                    id=f"{selected_key}-low-audio",
                    src=f"/assets/audio/{selected_key}_low.mp3",
                    controls=False,
                    preload="none",
                    loop = True,
                    style={'display': 'none'}
                )
            ], style={'flex': '1', 'textAlign': 'left', 'marginBottom': '5px'}),

            html.Div([
                html.P(html.B(f"Fort·e {selected_key} :"), style={'color': '#1DB954'}),
                html.P(feature_data['high_example_name']),
                html.Img(
                    src="/assets/icons/play_icon.png",
                    id={'type': 'audio-icon', 'index': f"{selected_key}-high"},
                    style={'width': '30px', 'cursor': 'pointer'}
                ),
                html.Audio(
                    id=f"{selected_key}-high-audio",
                    src=f"/assets/audio/{selected_key}_high.mp3",
                    controls=False,
                    preload="none",
                    loop = True,
                    style={'display': 'none'}
                )
            ], style={'flex': '1', 'textAlign': 'left'})
        ])

    return explanation_block


layout = html.Div([
    html.Div(
        id='feature-tabs',
        children=[
            html.Button(
                feature.capitalize(),
                id={'type': 'feature-tab', 'index': feature},
                n_clicks_timestamp=1 if feature == 'acousticness' else 0,
                className='custom-button',
                style={
                    'marginRight': '4px',
                    'padding': '2px 5px',
                    'border': 'none',
                    'backgroundColor': '#1DB954' if feature == 'acousticness' else '#1e1e1e',
                    'color': '#1e1e1e' if feature == 'acousticness' else '#1DB954',
                    'cursor': 'pointer',
                    'borderRadius': '3px',
                    'fontWeight': 'bold',
                    'transition': 'all 0.3s ease-in-out',
                    'whiteSpace': 'nowrap',
                    'flexShrink': 1,
                }
            )
            for feature in explanations
        ],
        style={'marginBottom': '20px', 'display': 'flex', 'flexWrap': 'nowrap', 'justifyContent': 'center', 'gap': '3px'}
    ),

    html.Div(
        id='feature-explanation',
        children=get_feature_block('danceability'),
        style={
            'backgroundColor': '#1e1e1e',
            'padding': '15px',
            'borderRadius': '8px',
            'color': 'white',
            'fontSize': '14px',
            'lineHeight': '1.4',
            'display': 'flex',
            'justifyContent': 'space-between',
            'gap': '40px'
        }
    ),

    dcc.Store(id="dummy-store-audio")
], style={'padding': '30px', 'backgroundColor': '#1e1e1e'})

def register_callbacks(app):
    @app.callback(
        Output('feature-explanation', 'children'),
        Output({'type': 'feature-tab', 'index': ALL}, 'style'),
        Input({'type': 'feature-tab', 'index': ALL}, 'n_clicks_timestamp')
    )

    def update_feature(n_clicks_timestamps):
        if not n_clicks_timestamps or all(ts == 0 for ts in n_clicks_timestamps):
            selected_key = 'danceability'
        else:
            selected_idx = n_clicks_timestamps.index(max(n_clicks_timestamps))
            selected_key = list(explanations.keys())[selected_idx]

        explanation_block = get_feature_block(selected_key)

        styles = []
        for i, key in enumerate(explanations.keys()):
            if key == selected_key:
                styles.append({
                    'marginRight': '10px',
                    'padding': '6px 10px',
                    'border': 'none',
                    'backgroundColor': '#1DB954',
                    'color': '#1e1e1e',
                    'cursor': 'pointer',
                    'borderRadius': '5px',
                    'fontWeight': 'bold',
                    'transition': 'all 0.3s ease-in-out'
                })
            else:
                styles.append({
                    'marginRight': '10px',
                    'padding': '6px 10px',
                    'border': 'none',
                    'backgroundColor': '#1e1e1e',
                    'color': '#1DB954',
                    'cursor': 'pointer',
                    'borderRadius': '5px',
                    'fontWeight': 'bold',
                    'transition': 'all 0.3s ease-in-out'
                })

        return explanation_block, styles


    app.clientside_callback(
        """
        function(n1) {
            const ctx = dash_clientside.callback_context;
            if (!ctx.triggered.length) return "";

            const trigger = ctx.triggered[0];
            if (trigger.value === null) return "";

            const id = ctx.triggered[0].prop_id.split('.')[0];
            const index = JSON.parse(id).index;
            const audioId = index + "-audio";
            const audioEl = document.getElementById(audioId);
            const iconEl = document.querySelector(`[id*='${index}']`);

            if (!audioEl || !iconEl) return "";

            // Pause all other audio and reset icons
            document.querySelectorAll("audio").forEach(a => {
                if (a.id !== audioId) a.pause();
            });
            document.querySelectorAll("img[id*='audio-icon']").forEach(img => {
                img.src = "/assets/icons/play_icon.png";
            });

            if (audioEl.paused) {
                audioEl.play();
                iconEl.src = "/assets/icons/stop_icon.png";
            } else {
                audioEl.pause();
                iconEl.src = "/assets/icons/play_icon.png";
            }

            return "";
        }
        """,
        Output("dummy-store-audio", "data"),
        Input({'type': 'audio-icon', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )


