import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px
from dash import State
from dash import callback_context as ctx
from dash import ctx, no_update



# dataset et caractéristiques audio
dataset_path = "./dataset/spotify_songs_clean.csv"
carac_audio = [
    "danceability", "energy", "key", "loudness", "mode", 
    "speechiness", "acousticness", "instrumentalness", "liveness", "valence"
]

def preprocess_data():
    df = pd.read_csv(dataset_path)
    
    # Release date -> datetime et extract year
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], errors="coerce")
    df["year"] = df["track_album_release_date"].dt.year
    
    # Garder les données après 1970
    df = df[df["year"] >= 1970]
    
    # Moyenne de popularite par an pour chaque caracteristique audio
    grouped_df = df.groupby("year")[["track_popularity"] + carac_audio].mean().reset_index()
    
    # On groupe par genre et par année
    grouped_df_genre = df.groupby(["year", "playlist_genre"])[["track_popularity"] + carac_audio].mean().reset_index()

    return grouped_df,grouped_df_genre

grouped_df,grouped_df_genre = preprocess_data()

def filter_df(year_range, genre):
    start_year, end_year = year_range
    if genre == "all":
        return grouped_df[(grouped_df["year"] >= start_year) & (grouped_df["year"] <= end_year)]
    else:
        filtered = grouped_df_genre[(grouped_df_genre["playlist_genre"] == genre)]
        return filtered[(filtered["year"] >= start_year) & (filtered["year"] <= end_year)]

layout = html.Div([
    html.H1("Évolution des caractéristiques audio et leur impact sur la popularité"),
    html.Label("Sélectionnez un genre :"),
    dcc.Dropdown(
        id='genre-dropdown',
        options=[{'label': 'Tous les genres', 'value': 'all'}] + [
            {'label': genre, 'value': genre} for genre in sorted(grouped_df_genre['playlist_genre'].dropna().unique())
        ],
        value='all',
        
        clearable=False,
        style={"width": "35%", "margin-bottom": "10px"},
        className="custom-dropdown",
    ),
    html.Label("Sélectionnez l'intervalle de temps :"),
    dcc.RangeSlider(
        id="year-slider",
        min=grouped_df["year"].min(),
        max=grouped_df["year"].max(),
        value=[1970, 2020],
        marks={str(year): str(year) for year in range(grouped_df["year"].min(), grouped_df["year"].max()+1, 10)},
        step=10,
    ),

                # Boutons centrés au-dessus du graphique
                html.Div([
                    html.Button("← Précédent", id="prev-button-q1", n_clicks=0, className='custom-button'),
                    html.Button("Suivant →", id="next-button-q1", n_clicks=0, className='custom-button'),
                    html.Div(id="page-indicator-q1", style={"padding": "0 20px", "color": "white"}),
                ], style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'gap': '20px',
                    'marginTop': '20px',
                    'marginBottom': '20px'
                }),
            # Analyse et texte
            html.Div(
                id="analysis-text-q1",
                style={
                    'color': 'white',
                    'fontSize': '16px',
                    'marginTop': '20px',
                    'textAlign': 'center'
                },
                children="Pour les caractéristiques audio on remarque une très faible corrélation entre leur variations et celles de la popularité indiquant un rôle faible dans la popularité de la musique."
            ),
                
                
    html.Div(id="charts-container", style={"display": "grid", "grid-template-columns": "repeat(3, 1fr)", "gap": "20px"}),
    dcc.Store(id='story-page-q1', data=1),
    dcc.Store(id="features-store", data=carac_audio),

    
])

# Register callbacks with the main app.
def register_callbacks(app):
    @app.callback(
        Output("story-page-q1", "data"),
        Input("next-button-q1", "n_clicks"),
        Input("prev-button-q1", "n_clicks"),
        State("story-page-q1", "data"),
        prevent_initial_call=True
    )
    def update_story_page(n_next, n_prev, current):
        triggered = ctx.triggered_id
        if triggered == "next-button-q1":
            return 1 if current == 7 else current + 1
        elif triggered == "prev-button-q1":
            return 7 if current == 1 else current - 1
        return current

    @app.callback(
        Output("analysis-text-q1", "children"),
        Output("year-slider", "value"),
        Output("genre-dropdown", "value"),
        Output("page-indicator-q1", "children"),
        Output("features-store", "data"), 
        Input("story-page-q1", "data"),
    )
    def display_story(page):
        text = ""
        genre = "all"
        year_range = [1970, 2020]
        features = carac_audio.copy()

        if page == 1:
            text = html.Span([
                "En observant les graphiques, on remarque une très faible corrélation entre les variations des caractéristiques energy, loudness, danceability et celles de la popularité.",
                html.Br(),
                "Pour les autres caractéristiques, il n’existe pas de relation directe et systématique entre la valeur d’une caractéristique audio et la popularité d’une chanson,",
                html.Br(),
                "ce qui indique que les caractéristiques audio jouent un rôle limité dans la popularité de la musique."
            ])

        elif page == 2:
            text = html.Span([
                "Même en filtrant par genres, dans ce cas le “pop”, on n’observe pas une forte corrélation entre les caractéristiques audio et la popularité d’une chanson au sein de genres spécifiques.",
                html.Br(),
                "Vous pouvez aussi explorer les données pour un genre de votre choix en utilisant le filtre par genre."
            ])
            genre = "pop"
        elif page == 3:
            text = "Les musiques anciennes présentent un mode, valence et loudness élevés"
            year_range = [1970, 2010]
            features = ["mode", "valence", "loudness"]
        elif page == 4:
            text = "Alors que les musique récentes présentent un mode, valence et loudness plus faibles"
            year_range = [2010, 2020]
            features = ["mode", "valence", "loudness"]
        elif page == 5:
            text = html.Span([
                "Ce qui indique que les musiques récentes présentent des caractéristiques audio différentes, avec une tendance vers des morceaux plus mélancoliques,",
                html.Br(),
                "moins puissants et davantage influencés par des éléments instrumentaux et vocaux."
            ])
        elif page == 6:
            text = "Les caractéristiques audio exceptées key et liveness présentent des tendances et des évolutions notables au fil du temps"
            features = [f for f in carac_audio if f not in ["key", "liveness"]]
        elif page == 7:
            text = html.Span([
                "Alors que les caractéristiques Key et Liveness restent relativement stables au fil du temps et intemporelles, suggérant que ni la répartition des tonalités musicales",
                html.Br(),
                "ni la présence d'effets de public en direct dans les chansons populaires n'ont significativement évolué au fil des années."
            ])
            features = ["key", "liveness"]

        return text, year_range, genre, f"{page}/7", features

    @app.callback(
        Output("charts-container", "children"),
        Input("year-slider", "value"),
        Input("genre-dropdown", "value"),
        Input("features-store", "data")
    )
    def update_charts(year_range, selected_genre, features):
        filtered_df = filter_df(year_range, selected_genre)
        charts = []
        total_features = len(features)
        charts_per_row = 3
        if len(features) == 2:
            charts_per_row = 2
        for i, feature in enumerate(features):
            # getting index of last subchart in row
            show_colorbar = ((i + 1) % charts_per_row == 0) or (i == len(features) - 1)
            fig = px.scatter(
                filtered_df.copy(),
                x=feature,
                y="track_popularity",
                size=[20]*len(filtered_df),
                color="year",
                color_continuous_scale="Viridis",
                labels={"track_popularity": "Popularité Moyenne", feature: feature.capitalize(), "year": "Année"},
                title=f"{feature.capitalize()} vs Popularity"
            )
            fig.update_traces(
                marker=dict(opacity=0.95),
                hovertemplate=(
                    f"{feature.capitalize()}: %{{x:.6f}}<br>"
                    "Popularité Moyenne: %{y:.5f}<br>"
                    "Année: %{marker.color}"
                )
            )
            if not show_colorbar:
                fig.update_coloraxes(showscale=False)
            fig.update_layout(
                title_x=0.5, 
                yaxis_title="Popularity", 
                xaxis_title=feature.capitalize(),
                title_font_color='white',
                xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
                yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
                coloraxis_colorbar=dict(
                tickfont=dict(color='white'),
                title=dict(font=dict(color='white'))
                ),
                plot_bgcolor='#121212', 
                paper_bgcolor='#121212',
                height=350,
                showlegend=True  
                )
            # centering last row
            remaining = total_features % 3
            is_last = i == total_features - 1
            needs_centering = remaining == 1 and is_last
            style = {"width": "100%", "textAlign": "center"}
            if needs_centering:
                style["gridColumn"] = "2 / 3"  # center in the second column of 3
            charts.append(html.Div(dcc.Graph(figure=fig), style=style))
            
        return charts






        

