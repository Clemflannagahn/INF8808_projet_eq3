import plotly.graph_objects as go
import pandas as pd
from dash import dcc, html


def convert_date(date):
    try:
        # Format complet "%Y-%m-%d"
        return pd.to_datetime(date, format="%Y-%m-%d")
    except ValueError:
        try:
            # Format année seule "%Y", complété par "-01-01"
            return pd.to_datetime(date, format="%Y") + pd.offsets.DateOffset(months=0, days=0)
        except ValueError:
            return pd.NaT


def get_dataframe(path):
    data = pd.read_csv(path)
    data["track_album_release_date"] = data["track_album_release_date"].apply(convert_date)
    data = data[data["track_album_release_date"].dt.year >= 1970] # On ne garde que les musiques après 1970, car il n'y a pas assez d'échantillons avant
    return data

def get_hover_template():
    return (
        "<b>Nombre d'artistes:</b></span>" 
        " %{customdata} <br /></span>"
        "<b>Nombre de sous-genres:</b></span>"
        " %{x}<br /></span>"
        "<b>Popularité:</b></span>"
        " %{y:.3f} %</span>"
        "<extra></extra>" # Pour enlever le "trace 0" qui apparait automatiquement sinon
    )

def get_figure():
    data = get_dataframe("./dataset/spotify_songs_clean.csv")
    div_pop_df = data.groupby("track_artist").agg(nb_subgenres=("playlist_subgenre", "nunique"), mean_popularity=("track_popularity", "mean")).reset_index()
    div_pop_df = div_pop_df.groupby("nb_subgenres").agg(mean_popularity=("mean_popularity", "mean"), nb_artist=("track_artist", "count")).reset_index()
    div_pop_df = div_pop_df[div_pop_df["nb_artist"] > 4]

    size = div_pop_df["nb_artist"]

    fig = go.Figure(data=[go.Scatter(
        x=div_pop_df["nb_subgenres"],
        y=div_pop_df["mean_popularity"],
        name="Nombre d'artistes",
        mode='markers',
        marker=dict(size=size, sizemode='area', sizeref=2, sizemin=4, color='#62d089', opacity=1),
        customdata=size,
    )])

    fig.update_traces(hovertemplate=get_hover_template())

    fig.update_layout(
        xaxis_title="Nombre de sous-genres",
        yaxis_title="Popularité moyenne",
        xaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(showgrid=True,title_font=dict(color='white'), tickfont=dict(color='white')),
        showlegend=True,
        legend_title_text="Légende",
        legend=dict(font=dict(color='white')),
        legend_title=dict(font=dict(color='white')),
        plot_bgcolor='#121212', 
        paper_bgcolor='#121212',
        height=600,
    )
    return fig

layout = html.Div([
    html.H1("Impact d'une discographie variée sur la popularité"),
    html.Div([
        dcc.Graph(id="graph-q11", figure=get_figure()),
    ], style={'width': '60%', 'display': 'inline-block'}),
    html.Div([
        dcc.Markdown("""
            Une discographie diversifiée (avec de nombreux sous-genres) semble impacter positivement la popularité. 
            On pourrait expliquer ce phénomène en supposant que ces artistes :
            - **s’adaptent à leur environnement** en explorant des sous-genres différents pour parfaire leurs musiques vis à vis de leurs auditoires.
            - **aux modes des époques** pour perdurer dans le temps.
            
            Une majorité des artistes ne possède qu’un seul genre, montrant possiblement la difficulté à changer de style. Ils ont également en moyenne la **popularité** la plus faible.
            """, style={'backgroundColor': '#121212','fontSize': '16px',}),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
        dcc.Markdown("""
            ### Attention cependant à la lecture de ce graphique!
            Un grand nombre de sous-genre peut signifier beaucoup de tests de la part des artistes en questions, mais pas forcément que ceux-ci ont fait un album complet de chaque genre.
        """, style={'backgroundColor': '#121212','fontSize': '16px',}),
    ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top', "marginTop": "100px", 'color': 'white'}),
])

