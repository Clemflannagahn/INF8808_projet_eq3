from dash import html, dcc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

def generate_duration_popularity_plot():
    data = pd.read_csv("./dataset/spotify_songs_clean.csv")
    data["duration_min"] = data["duration_ms"] / 60000
    data["duration_bin"] = (data["duration_min"] * 4).round() / 4

    grouped_data = data.groupby("duration_bin", as_index=False).agg({
        "track_popularity": "mean",
        "track_id": "count"
    }).rename(columns={"track_id": "count"})

    grouped_data["duration_bin"] = grouped_data["duration_bin"].round(2)
    grouped_data["track_popularity"] = grouped_data["track_popularity"].round(2)
    grouped_data["Legend"] = "Nombre de morceaux"
    grouped_data["size_scaled"] = np.sqrt(grouped_data["count"]) * 10
    grouped_data["count_original"] = grouped_data["count"]

    fig = px.scatter(
        grouped_data,
        x="duration_bin",
        y="track_popularity",
        size="size_scaled",
        color="Legend",
        title="Influence de la durée d'un morceau sur sa popularité",
        labels={
            "duration_bin": "Durée (min)",
            "track_popularity": "Popularité moyenne",
            "count": "Nombre de morceaux"
        },
        opacity=0.7,
        hover_data={
            "duration_bin": True,
            "track_popularity": True,
            "count_original": True
        },
        color_discrete_map={"Nombre de morceaux": "#2ca02c"}
    )

    lowess_results = lowess(grouped_data["track_popularity"], grouped_data["duration_bin"], frac=0.3)

    fig.add_trace(go.Scatter(
        x=lowess_results[:, 0],
        y=lowess_results[:, 1],
        mode="lines",
        line=dict(dash="dot", color="blue"),
        name="Tendance"
    ))

    fig.update_traces(
        marker=dict(line=dict(width=0)),
        hovertemplate="<b>Durée:</b> %{x} min<br><b>Popularité moyenne:</b> %{y:.2f}<br><b>Nombre de morceaux:</b> %{customdata:.0f}<extra></extra>",
        customdata=grouped_data["count_original"]
    )

    fig.update_layout(
        title_font=dict(size=20, color='white'),
        xaxis=dict(title="Durée (min)", title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(title="Popularité moyenne", title_font=dict(color='white'), tickfont=dict(color='white')),
        legend=dict(font=dict(color='white')),
        legend_title=dict(font=dict(color='white')),
        plot_bgcolor='#121212',
        paper_bgcolor='#121212',
        height=600
    )

    return fig

narrative_q4 = html.Div([
    dcc.Markdown("""
Cette visualisation explore le lien entre la **durée d’un morceau** et sa **popularité moyenne** auprès des auditeurs.

Chaque point représente un ensemble de morceaux ayant une durée similaire. Plus le cercle est grand, plus ce groupe contient de morceaux.  
La courbe en pointillés bleus représente la **tendance générale**.

On remarque que la popularité augmente rapidement avec la durée jusqu’à environ **2 à 3 minutes**, où elle atteint un **pic**.  
Au-delà de cette durée, la popularité tend à **diminuer progressivement**, ce qui laisse entendre qu’un format court à moyen serait **plus apprécié** par les auditeurs.

Mais que raconte vraiment cette tendance ?

On peut imaginer que dans un monde rythmé par les réseaux sociaux, les playlists rapides et l’attention limitée, les auditeurs cherchent des morceaux ** efficaces, qui vont droit au but**.  
Les artistes qui maîtrisent ce format concis semblent avoir plus de popularité.  
C’est aussi le format privilégié pour les chansons virales sur TikTok, ou les hits radios qui doivent capter l’auditeur dès les premières secondes.

En termes de popularité globale sur les plateformes, **le format court gagne la bataille** et  **chaque seconde compte**.

    """)
], style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px', 'marginLeft': '5%', 'marginRight': '5%'})

layout = html.Div([
    html.H1("Durée des morceaux et popularité", style={"textAlign": "left", "color": "white"}),

    html.Div([
        html.Div([
            narrative_q4
        ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginTop': '10px'}),

        html.Div([
            dcc.Graph(id='scatter-duration-popularity', figure=generate_duration_popularity_plot())
        ], style={'width': '60%', 'display': 'inline-block'})
    ])
])
