import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def load_and_clean_data(filepath="./dataset/spotify_songs_clean.csv"):
    df = pd.read_csv(filepath)
    df = preprocess_dates(df)
    return df

def preprocess_dates(df):
    df["track_album_release_date"] = pd.to_datetime(df["track_album_release_date"], errors='coerce') # conversion en datetime
    df = df[df["track_album_release_date"].notna() & (df["track_album_release_date"].dt.month.notna())] 
    df["year_month"] = df["track_album_release_date"].dt.to_period('M')
    df = df[df["year_month"] > '2000-01'] # filtre pour ne garder que les dates après 2000
    df["year_month"] = df["year_month"].astype(str)
    return df

def filter_popular_songs(df):
    popularity_threshold = 50
    features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]

    df["year_month"] = pd.to_datetime(df["year_month"])
    df["year"] = df["year_month"].dt.year
    df["year_group"] = (df["year"] // 3) * 3
    
    df_popular = df[df["track_popularity"] > popularity_threshold].groupby(["year_group", "playlist_genre"])[features].mean().reset_index()
    df_popular["year_group"] = pd.to_datetime(df_popular["year_group"], format='%Y')
    return df_popular.sort_values("year_group")

def calculate_index(df_popular, base_year=1998):
    features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]
    base_values = df_popular[df_popular["year_group"].dt.year == base_year]
    for feature in features:
        for genre in df_popular["playlist_genre"].unique():
            base_value = base_values[base_values["playlist_genre"] == genre][feature].values[0]
            df_popular.loc[(df_popular["playlist_genre"] == genre), f"{feature}_index"] = (
                (df_popular[feature] / base_value) * 100
            ) 
    return df_popular

# data
df = load_and_clean_data("./dataset/spotify_songs_clean.csv")
df_popular = filter_popular_songs(df)
    
min_year = df_popular["year_group"].dt.year.min()
max_year = df_popular["year_group"].dt.year.max()

#layout
layout = html.Div([
    html.H1("Évolution des caractéristiques musicales pour tous les genres"),

    html.Div([
        dcc.RadioItems(
            id='genre-selector',
            options=[{'label': 'Tous', 'value': 'all'}] + [{'label': genre.capitalize(), 'value': genre} for genre in df_popular['playlist_genre'].unique()],
            value='all',
            labelStyle={
                'display': 'inline-block',  # Ensure buttons are displayed inline
                'marginRight': '10px',
                'marginLeft': '10px',
                'padding': '6px 10px',  # Ensure consistent left and right padding
                'border': 'none',
                'backgroundColor': '#1DB954',  # Default selected color
                'color': '#1e1e1e',  # Default selected text color
                'cursor': 'pointer',
                'borderRadius': '5px',
                'fontWeight': 'bold',
                'transition': 'all 0.3s ease-in-out',
                'whiteSpace': 'nowrap',
            },
            inputStyle={
      
                'appearance': 'none',
                'width': '0',
                'height': '0'
            }
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),  # Center align the buttons

    html.Div(id="analysis-text-container", style={  
        'color': 'white', 
        'padding': '20px',
        'textAlign': 'center',
        'fontSize': '18px'
    }),
    html.Div(id='graphs-container'),
    
    html.Div(
        html.H4("Sélectionnez l'année de référence :"),
        style={
            'textAlign': 'center',
            'color': 'white',
            'marginTop': '20px',
            'fontSize': '16px'
        }
    ),
    
    html.Div(
        dcc.Slider(
            id='base-year-slider',
            min=min_year,
            max=max_year,
            value=min_year,
            marks={str(year): str(year) for year in range(min_year, max_year + 1, 3)},
            step=3
        ),
        style={'width': '60%', 'margin': '0 auto'}  
    ),

])


def register_callbacks(app):
    analyses = {
        "tous": "Sélectionnez un genre pour afficher une analyse spécifique.",
        "edm": "L'EDM a évolué vers une esthétique sonore plus émotionnelle et nuancée. La baisse de la **valence** traduit une tendance vers des ambiances mélancoliques, tandis que la diminution de la **speechiness** suggère un recul des éléments vocaux au profit d’une instrumentation plus immersive. L’augmentation marquée de la **liveness**, unique parmi les genres, indique une intégration accrue d’enregistrements live. Enfin, la baisse de la **loudness** témoigne d’une recherche de subtilité et de finesse sonore.",
        "latin": "Le genre latin s’oriente vers des sonorités plus dynamiques et expressives. L’augmentation constante de la **danceability** illustre son adaptation aux pistes de danse et une popularité croissante. La **energy**, également en hausse, reflète des productions plus intenses, tandis que la montée de la **speechiness** souligne l’importance du vocal dans ce style. La **valence**, bien que légèrement en déclin, conserve un caractère majoritairement positif. Quant à la **loudness**, elle montre un léger recul suivi d’une stabilisation, traduisant une évolution en phase avec les préférences contemporaines.",
        "pop": "La pop a progressivement adopté une production plus maîtrisée, tout en gagnant en profondeur émotionnelle. La **danceability** reste élevée, confirmant sa vocation grand public. Légèrement en baisse, la **energy** reflète un équilibre recherché entre intensité et accessibilité. La hausse de la **speechiness** révèle une place croissante pour des paroles narratives ou expressives. La **valence** en recul témoigne d’une orientation vers des atmosphères plus introspectives, tandis que la **loudness**, stable, assure une continuité dans l’impact sonore.",
        "r&b": "Le R&B a connu une transformation marquée par une exploration plus variée des émotions. Les fluctuations de la **valence** traduisent une diversité de tonalités. L’augmentation de la **energy**, combinée à une baisse de la **loudness**, montre une évolution vers des productions à la fois plus intenses et plus raffinées. La **speechiness**, en légère hausse, confirme l’importance des paroles et du storytelling dans ce genre.",
        "rap": "Depuis 1998, le rap maintient une **speechiness** élevée, soulignant l’importance constante du texte et du récit. La baisse continue de la **valence** suggère une tendance vers des thématiques plus graves ou introspectives. Bien que la **energy** diminue, la **loudness** reste forte, traduisant un impact sonore toujours puissant, caractéristique du genre, malgré une adaptation à des sonorités plus actuelles.",
        "rock": "Le rock montre une orientation progressive vers des ambiances plus introspectives, comme en témoigne la baisse régulière de la **valence**. La **loudness** et la **danceability**, bien que relativement stables, demeurent en deçà de leurs niveaux passés, évoquant un adoucissement du genre. L’augmentation de la **speechiness** pourrait signaler un retour à une plus grande présence vocale dans les compositions récentes."
    }




    @app.callback(
    Output('analysis-text-container', 'children'),
    Output('graphs-container', 'children'),
    Input('base-year-slider', 'value'),
    Input('genre-selector', 'value')
    )
    
    

    def update_graphs(base_year, selected_genre):
        
        selected_key = selected_genre if selected_genre in analyses else "tous"
        analysis_text = analyses[selected_key]
        
        df_popular_updated = calculate_index(df_popular, base_year=base_year)
        features = ["danceability", "energy", "speechiness", "liveness", "valence", "loudness"]
        genres_couleurs = {
            "rock": "#FF0000",       # Rouge
            "latin": "#FFA500",      # Orange
            "edm": "#f542f5",        # Rose
            "rap": "#800080",        # Violet
            "r&b": "#008000",        # Vert
            "pop": "#ADD8E6"         # Bleu clair
        }
        
        feature_emojis = {
            "danceability": "💃",
            "energy": "⚡",
            "speechiness": "🗣️",
            "liveness": "🎤",
            "valence": "😊",
            "loudness": "🔊"
        }
        
        #subplots
        fig = make_subplots(
            rows=2, 
            cols=3,
            subplot_titles=[
                f"{feature_emojis[feature]} Évolution de {feature.capitalize()}" 
                for feature in features
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        #traces
        for i, feature in enumerate(features):
            row = (i // 3) + 1
            col = (i % 3) + 1
            
            for genre in df_popular_updated["playlist_genre"].unique():
                genre_df = df_popular_updated[df_popular_updated["playlist_genre"] == genre]
                
                opacity = 1.0 if selected_genre == 'all' or genre == selected_genre else 0.25

                fig.add_trace(
                    go.Scatter(
                        x=genre_df["year_group"],
                        y=genre_df[f"{feature}_index"],
                        name=genre,
                        legendgroup=genre,
                        showlegend=True if i == 0 else False,
                        hovertemplate=f"<b>{genre}</b>: %{{y:.2f}}<extra></extra>",
                        line=dict(width=2, color=genres_couleurs.get(genre, "#FFFFFF")),
                        opacity=opacity
                    ),
                    row=row,
                    col=col
                )
            
            # horizontal line
            fig.add_hline(
                y=100,
                line_dash="dash",
                line_color="gray",
                row=row,
                col=col
            )
        
        
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                title_text="Genres:",
                font=dict(color="white") 
            ),
            dragmode=False,
            height=800,
            margin=dict(t=50, b=50),
            hovermode="x unified",
            plot_bgcolor='#121212',  
            paper_bgcolor='#121212',  
            font=dict(color="white") 
        )
        
        for i, feature in enumerate(features):
            row = (i // 3) + 1
            col = (i % 3) + 1
            fig.update_yaxes(
                title_text=f"{feature.capitalize()} (%)", 
                title_font=dict(color="white"),  
                tickfont=dict(color="white"), 
                showgrid=False, 
                row=row, 
                col=col
            )
            fig.update_xaxes(
                title_text="Année", 
                title_font=dict(color="white"), 
                tickfont=dict(color="white"),  
                showgrid=False,  
                tickmode="array", 
                tickvals=df_popular_updated["year_group"].dt.year.unique(),  
                ticktext=[str(year) for year in df_popular_updated["year_group"].dt.year.unique()], 
                row=row, 
                col=col
            )
            
        return dcc.Markdown(analysis_text), html.Div([dcc.Graph(figure=fig, style={'width': '100%', 'height': '800px'})])
