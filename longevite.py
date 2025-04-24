import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

file_path = "./dataset/spotify_songs_clean.csv"
data = pd.read_csv(file_path)

data["track_album_release_date"] = pd.to_datetime(data["track_album_release_date"], errors='coerce')
data["year"] = data["track_album_release_date"].dt.year
data["decade"] = (data["year"] // 10) * 10

div_pop_df = data.groupby("track_artist").agg(nb_decennie=("decade", "nunique"))\
                 .query("nb_decennie >= 3").reset_index()

features = ["track_popularity", "danceability", "energy", "valence", "tempo"]

def generate_line_chart(selected_feature):
    data_filtered = data[data["year"] >= 1970]

    long_career_artists = div_pop_df["track_artist"]
    data_long = data_filtered[data_filtered["track_artist"].isin(long_career_artists)]
    data_short = data_filtered[~data_filtered["track_artist"].isin(long_career_artists)]

    long_data = data_long.groupby("year")[selected_feature].mean().reset_index()
    long_count = data_long.groupby("year").size().reset_index(name='track_count')

    short_data = data_short.groupby("year")[selected_feature].mean().reset_index()
    short_count = data_short.groupby("year").size().reset_index(name='track_count')

    fig = px.line()

    fig.add_scatter(
    x=long_data["year"], 
    y=long_data[selected_feature], 
    mode='lines+markers', 
    name="Artistes actifs plus que 3 décennies", 
    line=dict(color='green'),
    text=long_count['track_count']
    )

    fig.add_scatter(
        x=short_data["year"], 
        y=short_data[selected_feature], 
        mode='lines+markers', 
        name="Les autres artistes ", 
        line=dict(color='blue'),
        text=short_count['track_count']
    )


    fig.update_traces(hovertemplate=(
        '<b>Année: </b>%{x}<br>' +
        '<b>Valeur moyenne: </b>%{y:.2f}<br>' +
        '<b>Nombre de morceaux: </b>%{text}<br>' +
        '<extra></extra>'
    ))

    if selected_feature == "energy":
        title = f"Évolution de l'{selected_feature} selon la longévité artistique"
    elif selected_feature == "tempo":
        title = f"Évolution du {selected_feature} selon la longévité artistique"
    else:
        title = f"Évolution de la {selected_feature} selon la longévité artistique"

    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color='white')),
        xaxis_title="Année",
        yaxis_title=selected_feature,
        xaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white')),
        legend=dict(font=dict(color='white')),
        legend_title=dict(font=dict(color='white')),
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        height=600,
    )

    return fig


narrative_q13 = html.Div(
    [
        dcc.Markdown("""  

        Il est fascinant d'observer la manière dont les artistes à longue carrière évoluent à travers les décennies.  
        Malgré le temps qui les sépare des artistes plus récents, leurs trajectoires musicales se montre étonnamment similaires.

        *Comment l’expliquer ?* 
                     
        Ces artistes semblent intégrer les tendances musicales modernes sans jamais perdre ce qui fait leur identité.  
        Leur adaptation est **progressive**, **maîtrisée**, et souvent plus nuancée : ils suivent les mouvements sans jamais s'y fondre complètement.

        On remarque par exemple que leur style reste plus stable sur certains aspects, comme la **valence**, où ils conservent une teinte plus positive alors que les artistes récents adoptent un ton plus introspectif.

        En somme, leur longévité ne repose pas seulement sur le talent, mais sur cette capacité à **rester en mouvement**, à **absorber le changement sans se diluer**, et à proposer une musique qui évolue avec son époque tout en restant fidèle à son essence.
        """)
    ],
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px'}
)

layout = html.Div([
    html.H1("Évolution des caractéristiques musicales des artistes", style={"textAlign": "left"}),
    narrative_q13,
    html.Label("Sélectionnez une caractéristique musicale:"),
    dcc.Dropdown(
        id='feature-dropdown-q13',
        options=[{'label': feature.capitalize(), 'value': feature} for feature in features],
        value='track_popularity',
        className='custom-dropdown'
    ),
    dcc.Graph(id='line_chart-q13')
])

def register_callbacks(app):
    @app.callback(
        Output('line_chart-q13', 'figure'),
        [Input('feature-dropdown-q13', 'value')]
    )
    def update_chart(selected_feature):
        return generate_line_chart(selected_feature)
