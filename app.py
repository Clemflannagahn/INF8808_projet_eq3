import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import os
import sys

# Create the main Dash app instance.
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Spotify Songs Analysis'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importations des différentes sections du storytelling
import caracteristiques_audio
import caracteristiques
import correlation
import pop_vs_duree
import evolutions
import discographie
import adaptation
import longevite

# Register callbacks des sections.
caracteristiques_audio.register_callbacks(app)
caracteristiques.register_callbacks(app)
correlation.register_callbacks(app)
evolutions.register_callbacks(app)
adaptation.register_callbacks(app)
longevite.register_callbacks(app)

# navigation bar avec des liens pour se déplacer rapidement entre les sections
navbar = html.Div(
    [
        html.Img(src="/assets/icons/spotify_icon.svg", style={'height': '40px', 'marginRight': '10px'}),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Définitions"],
            href="#def-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Caractéristiques"],
            href="#caracteristiques-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Corrélation"],
            href="#correlation-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Évolutions"],
            href="#evolutions-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Popularité vs Durée"],
            href="#pop_vs_duree-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Discographie"],
            href="#discographie-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Adaptation"],
            href="#adaptation-section"
        ),
        html.A(
            [html.I(className="fa-brands fa-spotify", style={'marginRight': '8px'}), "Longévité"],
            href="#longevite-section"
        )
    ],
    className="navbar"
)

narrative = html.Div(
    [
        html.H1(
            "Quels ingrédients font le hit parfait… et comment ont-ils évolué avec le temps ?",
            style={
                'color': 'white',
                'textAlign': 'center',
                'marginBottom': '30px',
                'fontWeight': 'bold',
            }
        ),
        dcc.Markdown(""" 
        Écouter de la musique est un plaisir universel. Mais pourquoi certains morceaux deviennent-ils des phénomènes mondiaux, tandis que d'autres passent inaperçus ?
                     
        Pour le découvrir, plongeons dans les données de Spotify avec 30 000 chansons. La plateforme de streaming attribue une note de popularité à chaque morceau, à partir de l'interaction des auditeurs et de caractéristiques audio qui définissent l'identité de chaque chanson. Regardons en détail ces caractéristiques pour mieux comprendre ce qui fait le succès d'une chanson.
        """,
        style={
            'padding': '30px',
            'backgroundColor': '#121212',
            'borderRadius': '8px',
            'color': 'white',
            'lineHeight': '1.6',
            'fontSize': '16px',
            'marginLeft': '5%',
            'marginRight': '5%',
        }
        ),
    ],)

narrative_caracteristiques = html.Div(
    dcc.Markdown("""
    Maintenant que vous êtes devenus des connaisseurs, penchons-nous de plus près sur ces caractéristiques audio.
    Ces dimensions sonores, comme la danceability ou la loudness, ont-elles évolué au fil des années et jouent-elles un rôle clair dans la popularité des morceaux ?
    """),
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px', 'marginLeft': '5%', 'marginRight': '5%'}
)

narrative_correlation = html.Div(
    dcc.Markdown("""
    Il est difficile de tracer un lien direct entre une caractéristique audio et la popularité d’un morceau.
    Prises isolément, elles ne suffisent pas à expliquer le succès musical. Mais peut-être que la clé réside dans leurs interactions.

    Ensemble, les caractéristiques forment la signature sonore d’un morceau, et bien souvent, l’identité d’un genre.
    Voyons comment elles interagissent, s’influencent, et dessinent les contours de nos styles musicaux préférés."""),
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px', 'marginLeft': '5%', 'marginRight': '5%'}
)

narrative_evolutions = html.Div(
    dcc.Markdown("""Après avoir exploré ces dimensions sonores, une question se pose : leur importance est-elle restée la même au fil du temps ?
    Avec l’arrivée du streaming, les formats et les styles ont évolué.
    Certaines caractéristiques se sont-elles renforcées ? D’autres ont-elles disparu ?
    Plongeons maintenant dans leur évolution pour voir comment la musique s’est transformée, année après année, depuis les années 2000."""),
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px', 'marginLeft': '5%', 'marginRight': '5%'}
)

narrative_pop_vs_duree = html.Div(
    dcc.Markdown("""
    Au fil des années, les caractéristiques sonores ont suivi leurs propres trajectoires, façonnant des tendances nouvelles selon les genres.
    Mais au-delà de ces dimensions musicales, un autre facteur mérite qu’on s’y attarde : la durée d’un morceau.
    Est-elle simplement un choix artistique ou influence-t-elle réellement la popularité ?
    Dans une époque où tout s’accélère, la longueur d’une chanson pourrait bien jouer un rôle plus stratégique qu’on ne l’imagine.
"""),
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px', 'marginLeft': '5%', 'marginRight': '5%'}
)

narrative_discographie = html.Div(
    dcc.Markdown("""
    À l’ère des formats courts, des scrolls incessants et des tendances qui naissent et disparaissent en quelques jours, la musique semble devoir suivre ce rythme effréné.
    La question se pose alors pour les artistes : doivent-ils vraiment s’adapter en permanence au risque de perdre leurs auditeurs ?
                 
    La diversité musicale deveient alors une stratégie.
    Mais est-elle réellement un levier de popularité, ou au contraire un risque de diluer son identité dans la course au renouvellement ?
    """),
    style={'padding': '20px', 'backgroundColor': '#121212', 'borderRadius': '8px', 'marginLeft': '5%', 'marginRight': '5%'}
)


# Layout global du storytelling
content = html.Div(
    [
        # Caracteristiques section
        narrative,
        html.Div(
            caracteristiques_audio.layout,
            id="def-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        html.Hr(style={"border-color": "#1DB954", "marginLeft": "5%", "marginRight": "5%", "marginTop": "30px"}),
        narrative_caracteristiques,
        html.Div(
            caracteristiques.layout,
            id="caracteristiques-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        html.Hr(style={"border-color": "#1DB954", "marginLeft": "5%", "marginRight": "5%", "marginTop": "30px"}),
        narrative_correlation,
        # Correlation section
        html.Div(
            correlation.layout,
            id="correlation-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        html.Hr(style={"border-color": "#1DB954", "marginLeft": "5%", "marginRight": "5%", "marginTop": "30px"}),
        # Evolutions section
        narrative_evolutions,
        html.Div(
            evolutions.layout,
            id="q5-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        html.Hr(style={"border-color": "#1DB954", "marginLeft": "5%", "marginRight": "5%", "marginTop": "30px"}),
        # Pop_vs_duree section
        narrative_pop_vs_duree,
        html.Div(
            pop_vs_duree.layout,
            id="pop_vs_duree-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        html.Hr(style={"border-color": "#1DB954", "marginLeft": "5%", "marginRight": "5%", "marginTop": "30px"}),
        # Discographie section
        narrative_discographie,
        html.Div(
            discographie.layout,
            id="discographie-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        html.Hr(style={"border-color": "#1DB954", "marginLeft": "5%", "marginRight": "5%", "marginTop": "30px"}),
        # Adaptation section
        html.Div(
            adaptation.layout,
            id="adaptation-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        html.Hr(style={"border-color": "#1DB954", "marginLeft": "5%", "marginRight": "5%", "marginTop": "30px"}),
        # Longevite section
        html.Div(
            longevite.layout,
            id="longevite-section",
            style={"padding-top": "60px", "margin-top": "-60px", 'marginLeft': '5%', 'marginRight': '5%'}
        ),
        # Fin du storytelling
        html.H3(
            """
            C’est ici que s’achève notre exploration de l’univers musical à travers les données de Spotify.
            Vous l’avez vu : derrière chaque morceau se cache un subtil équilibre de caractéristiques, d’émotions et de tendances.
            Alors, avez-vous une meilleure idée de ce qui fait le succès d’une chanson ?
            À vous maintenant d’en parler, de partager, et peut-être… d’écouter autrement.
            """,
            style={
                'color': 'white',
                'textAlign': 'left',
                'marginBottom': '30px',
                'fontWeight': 'bold',
                'marginLeft': '5%',
                'marginRight': '5%',
            }
        ),
    ],
    className="content"
)

# Layout final de l'app
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    content,
])
