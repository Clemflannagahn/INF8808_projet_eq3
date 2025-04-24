import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

def convert_date(date):
    try:
        #Format complet : "%Y-%m-%d"
        return pd.to_datetime(date, format="%Y-%m-%d")
    except ValueError:
        try:
            #Année seulement : "%Y", completed with "-01-01"
            return pd.to_datetime(date, format="%Y") + pd.offsets.DateOffset(months=0, days=0)
        except ValueError:
            return pd.NaT


def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = data["track_album_release_date"].apply(convert_date)
    # Conserver uniquement des dates supérieures à 1970
    data = data[data["track_album_release_date"].dt.year >= 1970]
    return data

def get_color_map():
    """
    Récupération de certaines couleurs pour faire correspondre les sous-genres des artistes à ceux du graphe des sou-genres
    
    """
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    color_sequence = ['rgb(27,158,119)','rgb(117,112,179)','rgb(102,166,30)','rgb(166,118,29)']

    color_map = {}
    for genre in sorted(data["playlist_genre"].unique()) :
        subgenres_genre = data[data["playlist_genre"] == genre]["playlist_subgenre"].unique()
        color_map.update({subgenre: color_sequence[i % len(color_sequence)] for i, subgenre in enumerate(subgenres_genre)})
    return color_map

color_map = get_color_map()


def data_preprocess(path, filter_type, artist=None):
    """
    Fonction pour preprocess les données

    Args
    ----
    path : str
        Chemin du fichier CSV
    filter_type : str
        Type de filtre à appliquer :
            - "artist" pour filtrer par artiste avec le nom de l'artiste dans l'argument artist
            - "genre" pour grouper par genres
            - "edm", "latin", "pop", "r&b", "rap", "rock" pour filtrer par genre (et donc grouper par ses sous-genres)
    artist : str, optional
        Nom de l'artiste à filtrer si filter_type est "artist"

    Returns
    -------
    pd.DataFrame
        Données preprocess pour le graph
    
    """
    data = get_dataframe(path)
    data["year"] = data["track_album_release_date"].dt.year
    data["decennie"] = (data["year"] // 10) * 10  # Calcul de la décénnie

    if filter_type == "artist":
        data = data[data["track_artist"] == artist]
        group_by_column = "playlist_subgenre"
    elif filter_type in ["edm", "latin", "pop", "r&b", "rap", "rock"]:
        data = data[data["playlist_genre"] == filter_type]
        group_by_column = "playlist_subgenre"
    else:
        group_by_column = "playlist_genre"

    genre_data = data.groupby(["decennie", group_by_column]).size().reset_index(name="count")
    genre_data = genre_data.pivot(index="decennie", columns=group_by_column, values="count").fillna(0)
 
    genre_data = (genre_data.div(genre_data.sum(axis=1), axis=0) * 100).reset_index()
    genre_data = genre_data.melt(id_vars="decennie", var_name=group_by_column, value_name="percentage")

    return genre_data

def data_preprocess_artist_cumulative(path, artist, genre_filter):
    """
    Preprocess des données pour les artistes avec les pourcentages cumulatifs par sous-genre

    Args
    ----
    path : str
        Chemin du fichier CSV des données
    artist : str
        Nom de l'artiste à filtrer
    genre_filter : str
        Genre à filtrer

    Returns
    -------
    pd.DataFrame
        Données preprocess pour le graph
    """
    data = get_dataframe(path)
    data = data[(data["track_artist"] == artist) & (data["playlist_genre"] == genre_filter)] # Filtrage pour l'artiste et le genre
    data["formatted_date"] = pd.to_datetime(data["track_album_release_date"]).dt.strftime("%Y-%m-%d")
    
    grouped = data.groupby(["formatted_date", "playlist_subgenre"]).size().reset_index(name="count")
    pivot = grouped.pivot(index="formatted_date", columns="playlist_subgenre", values="count").fillna(0).sort_index()
    
    cum = pivot.cumsum() # Cumulatif par sous-genre
    total_cum = cum.sum(axis=1) # Total cumulatif par date
    cum_percent = cum.div(total_cum, axis=0) * 100 # % cumulatif par sous-genre
    
    # Repasser en format "long" pour la suite
    cum_percent = cum_percent.reset_index().melt(id_vars="formatted_date", var_name="playlist_subgenre", value_name="percentage")
    cum_percent["formatted_date"] = pd.to_datetime(cum_percent["formatted_date"]).sort_values()
    
    return cum_percent


def data_preprocess_custom(path,genre_filter, bins=10, start_date=None, end_date=None):
    """
    Preprocess des données avec des dates personnalisées et des bins

    Args
    ----
    path : str
        Chemin du fichier CSV des données
    genre_filter : str
        Genre à filtrer
    bins : int
        Nombre de bins à utiliser
    start_date : pd.Timestamp
        Date de début
    end_date : pd.Timestamp
        Date de fin

    Returns
    -------
    pd.DataFrame
        Données preprocess pour le graph
    tuple
        Dates de début et de fin
    """
    data = get_dataframe(path)
    
    data = data[data["playlist_genre"] == genre_filter]
    
    # Dates de début et de fin
    min_date = start_date or data["track_album_release_date"].min()
    max_date = end_date or data["track_album_release_date"].max()

    # S'il n'y a qu'une date, on rajoute un jour
    if min_date == max_date:
        max_date = min_date + pd.Timedelta(days=1)
        
    # Création des bins
    bin_edges = pd.date_range(start=min_date, end=max_date, periods=bins+1)
    bin_midpoints = [bin_edges[i] + (bin_edges[i+1] - bin_edges[i]) / 2 for i in range(len(bin_edges)-1)]
    
    # Filtrage des données et assignation des chansons aux bins
    data = data[(data["track_album_release_date"] >= min_date) & (data["track_album_release_date"] <= max_date)]
    data["time_bin"] = pd.cut(data["track_album_release_date"], bins=bin_edges, labels=bin_midpoints, include_lowest=True)
    
    # Calcul des pourcentages
    genre_data = data.groupby(["time_bin", "playlist_subgenre"]).size().reset_index(name="count")
    genre_data = genre_data.pivot(index="time_bin", columns="playlist_subgenre", values="count").fillna(0)
    genre_data = (genre_data.div(genre_data.sum(axis=1), axis=0) * 100).reset_index()
    genre_data = genre_data.melt(id_vars="time_bin", var_name="playlist_subgenre", value_name="percentage")
    
    return genre_data, (min_date, max_date)


def get_figure_genre():
    genres_couleurs = {
        "rock": "#FF0000",       # Rouge
        "latin": "#FFA500",      # Orange
        "edm": "#f542f5",        # Rose
        "rap": "#800080",        # Violet
        "r&b": "#008000",        # Vert
        "pop": "#ADD8E6"         # Bleu clair
    }
    genre_data = data_preprocess("./dataset/spotify_songs_clean.csv", "playlist_genre", "playlist_genre")
    fig = px.area(genre_data, x="decennie", y="percentage", color="playlist_genre", line_group="playlist_genre", hover_data=["playlist_genre"],
                  color_discrete_map=genres_couleurs)
    fig.update_layout(
                height=500,
                legend_title_text="Genre",
                plot_bgcolor='#121212', 
                paper_bgcolor='#121212',
                legend=dict(font=dict(color='white')),
                xaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
                yaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
                )
    fig.update_traces(hovertemplate=get_hover_template("Genre"))
    fig.update_yaxes(title_text='Pourcentage (%)', title_font=dict(color='white'), tickfont=dict(color='white'))

    return fig


# Figures en cache pour les sous-genres
subgenre_cache = {
    "edm": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "edm"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map,
        title="Évolution des sous-genres de Edm",
        height=500,
    ),
    "latin": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "latin"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map,
        title="Évolution des sous-genres de Latin",
        height=500
    ),
    "pop": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "pop"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map,
        title="Évolution des sous-genres de Pop",
        height=500
    ),
    "r&b": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "r&b"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map,
        title="Évolution des sous-genres de R&b",
        height=500
    ),
    "rap": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "rap"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map,
        title="Évolution des sous-genres de Rap",
        height=500
    ),
    "rock": px.area(
        data_preprocess("./dataset/spotify_songs_clean.csv", "rock"),
        x="decennie", y="percentage", color="playlist_subgenre",
        line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
        color_discrete_map=color_map,
        title="Évolution des sous-genres de Rock",
        height=500
    )
}

def get_hover_template(type_name):
    return (
        f"<b>{type_name}:</b></span>" 
        " %{customdata[0]} <br /></span>"
        "<b>Decennie:</b></span>"
        " %{x}<br /></span>"
        "<b>Pourcentage:</b></span>"
        " %{y:.3f} %</span>"
        "<extra></extra>" # Pour enlever le "trace 0" qui apparait automatiquement sinon
    )


# Hover template pour les graphes avec les custom bins
def get_hover_template_custom(type_name):
    return (
        f"<b>{type_name}:</b></span>" 
        " %{customdata[0]} <br /></span>"
        "<b>Date:</b></span>"
        " %{x|%Y/%m/%d}<br /></span>"
        "<b>Pourcentage:</b></span>"
        " %{y:.3f} %</span>"
        "<extra></extra>" # Pour enlever le "trace 0" qui apparait automatiquement sinon
    )


layout = html.Div([
    html.H1("Adaptation des artistes à l'évolution des goûts musicaux"),
    html.Div([
        dcc.Graph(id="graph-q8", figure=get_figure_genre())
    ], style={'width': '50%', 'display': 'inline-block'}),
    html.Div([
        dcc.Markdown("""
        ### Analyse de l'évolution des genres des artistes
                     
        Il est maintenant possible de s'attarder non plus sur les caractéristiques des musiques elles-mêmes, mais sur l'évolution des artistes et des genres qu'ils créent.
                     
        On peut y apprendre de nombreux éléments sur l'évolution des goûts musicaux. 
        Par exemple, le rock semblait être le plus populaire dans les années 1970 (on peut alors penser à l'apparition de groupes comme les Rolling Stones, U2 ou Radiohead…)
        alors que l'EDM a lui émergé dans les années 2000.
        """),
        html.Br(),
        dcc.Markdown("""
        Vous pouvez **choisir un genre** en particulier pour observer les évolutions de ses sous-genres, ainsi que choisir un des artistes de ce genre pour observer l'évolution de sa discographie !
        
        *Il est ainsi possible de remarquer par exemple que pour le rap, le hip-hop qui représente aujourd'hui la majeure partie du genre, n'existait pas avant les années 1990 !*
        """)
        ],
    style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', "marginTop": "50px", 'color': 'white'}),
    html.Div([
        html.H4("Sélectionnez votre genre et votre artiste préféré et voyez si votre idole suit le flow !", style={"textAlign": "center", "margin": "20px 0"})
    ]),

    # Graphes des sous-genres et artistes
    html.Div([
        html.Div([
            html.Label("Sélectionnez un genre:", style={"color": "white"}),
            dcc.Dropdown(
                id='genre_dropdown',
                options=[{'label': g.capitalize(), 'value': g,} for g in ['edm', 'latin', 'pop', 'r&b', 'rap', 'rock']],
                placeholder="Sélectionnez un genre",
                style={"width": "80%"},
                className='custom-dropdown'
            ),
            
            dcc.Graph(id='subgenre_graph-q15')
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"}),

        html.Div([
            html.Label("Sélectionnez un artiste:", style={"color": "white"}),
            dcc.Dropdown(
                id='artist_dropdown',
                placeholder="Sélectionnez un artiste",
                optionHeight=35,
                style={"width": "80%"},
                className='custom-dropdown'
            ),
            dcc.Graph(id='artist_subgenre_graph')
        ], style={"width": "50%", "display": "inline-block", "verticalAlign": "top", "padding": "10px"})
    ], style={"display": "flex", "flex-direction": "row"})
])




def register_callbacks(app):
# Callback to update the artist dropdown based on the selected genre
    @app.callback(
        [Output('artist_dropdown', 'options'),
        Output('artist_dropdown', 'value')],
        [Input('genre_dropdown', 'value')]
    )
    def update_artist_options(selected_genre):
        if not selected_genre:
            return [], None
        data = get_dataframe("./dataset/spotify_songs_clean.csv")
        data = data[data["playlist_genre"] == selected_genre] # Filtrage par genre des chansons
        artist_counts = data.groupby("track_artist")["track_name"].nunique().reset_index(name="song_count")
        artist_counts = artist_counts.sort_values("song_count", ascending=False)
        options = [{'label': artist, 'value': artist} for artist in artist_counts["track_artist"]] # Création des options pour le dropdown
        return options, None
    
    @app.callback(
        Output('subgenre_graph-q15', 'figure'),
        [Input('genre_dropdown', 'value'),
        Input('artist_dropdown', 'value')]
    )
    def update_subgenre_graph(selected_genre, selected_artist):
        if not selected_genre:
            fig = px.area()
            fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5),
                            text="Sélectionnez un genre pour voir les données.",
                            showarrow=False)
            fig.update_layout(height=500,
                title_font=dict(color='white'),
                legend=dict(traceorder='reversed',font=dict(color='white')),
                legend_title=dict(font=dict(color='white')),
                paper_bgcolor='#121212',
                xaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
                yaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white'))
            )
            return fig

        if selected_artist: # Mise à jour du graphe avec les ranges de l'artiste
            data = get_dataframe("./dataset/spotify_songs_clean.csv")
            data_artist = data[(data["playlist_genre"] == selected_genre) &(data["track_artist"] == selected_artist)]
            
            if data_artist.empty:
                fig = subgenre_cache[selected_genre]
                fig.update_layout(
                    title_font=dict(color='white'),
                    legend_title=dict(font=dict(color='white')),
                    legend=dict(traceorder='reversed', font=dict(color='white')),
                    plot_bgcolor='#121212', 
                    paper_bgcolor='#121212',
                    xaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white')),
                    yaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white'))
                )
            else:
                artist_min = data_artist["track_album_release_date"].min()
                artist_max = data_artist["track_album_release_date"].max()
                genre_data, _ = data_preprocess_custom(
                    "./dataset/spotify_songs_clean.csv", 
                    selected_genre, 
                    bins=10, 
                    start_date=artist_min, 
                    end_date=artist_max
                )
                genre_data["time_bin"] = pd.to_datetime(genre_data["time_bin"])
                fig = px.area(
                    genre_data, 
                    x="time_bin", y="percentage", 
                    color="playlist_subgenre",
                    line_group="playlist_subgenre", 
                    hover_data=["playlist_subgenre"],
                    color_discrete_map=color_map
                )

                fig.update_traces(hovertemplate=get_hover_template_custom(selected_genre))
                fig.update_layout(
                    title_font=dict(color='white'),
                    height=500, 
                    title=dict(text=f"Évolution des sous-genres de {selected_genre}", font=dict(color='white')),
                    legend_title_text="Sous-genre de " + selected_genre,
                    legend_title=dict(font=dict(color='white')),
                    legend=dict(traceorder='reversed',font=dict(color='white')),
                    plot_bgcolor='#121212', 
                    paper_bgcolor='#121212',
                    xaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
                    yaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white'))
                    )


                fig.update_xaxes(title_text="Date", tickformat="%Y")
        else:
            fig = subgenre_cache[selected_genre]
            fig.update_layout(
                    title_font=dict(color='white'),
                    legend_title=dict(font=dict(color='white')),
                    legend=dict(traceorder='reversed', font=dict(color='white')),
                    plot_bgcolor='#121212', 
                    paper_bgcolor='#121212',
                    xaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white')),
                    yaxis=dict(showgrid=True, title_font=dict(color='white'), tickfont=dict(color='white'))
                )
        fig.update_yaxes(title_text='Pourcentage (%)')
        return fig


    @app.callback(
        Output('artist_subgenre_graph', 'figure'),
        [Input('genre_dropdown', 'value'),
        Input('artist_dropdown', 'value')]
    )
    def update_artist_subgenre_graph(selected_genre, selected_artist):
        if not selected_genre or not selected_artist:
            fig = px.area()
            fig.add_annotation(dict(xref="paper", yref="paper", x=0.5, y=0.5),
                            text="Sélectionnez un artiste pour voir les données.",
                            showarrow=False)
            fig.update_layout(height=500,
                title_font=dict(color='white'),
                legend=dict(traceorder='reversed',font=dict(color='white')),
                legend_title=dict(font=dict(color='white')),
                paper_bgcolor='#121212',
                xaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
                yaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white'))
            )
            return fig

        # Proportions cumulées des sous-genres pour l'artiste
        artist_data = data_preprocess_artist_cumulative("./dataset/spotify_songs_clean.csv", selected_artist, selected_genre)
        
        # Création du graphique
        fig = px.area(artist_data, x="formatted_date", y="percentage", color="playlist_subgenre",
                    line_group="playlist_subgenre", hover_data=["playlist_subgenre"],
                    color_discrete_map=color_map)
        
        fig.update_traces(hovertemplate=(
            "<b>Sous-genre:</b> %{customdata[0]}<br>"
            "<b>Date:</b> %{x|%Y-%m-%d}<br>"
            "<b>Pourcentage cumulatif:</b> %{y:.3f}%<extra></extra>"
        ))
        fig.update_yaxes(title_text='Pourcentage cumulatif (%)')
        fig.update_xaxes(title_text='Date')

        fig.update_layout(height=500,
                title=f"Évolution cumulée des sous-genres pour {selected_artist} ({selected_genre})",
                title_font=dict(color='white'),
                legend_title_text="Sous-genre",
                legend=dict(traceorder='reversed',font=dict(color='white')),
                legend_title=dict(font=dict(color='white')),
                plot_bgcolor='#121212', 
                paper_bgcolor='#121212',
                xaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
                yaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white'))
                )
        
        return fig
