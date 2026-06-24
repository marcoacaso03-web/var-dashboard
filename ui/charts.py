"""
Componente grafici Plotly per la VaR Dashboard.

Ogni funzione restituisce un ``plotly.graph_objects.Figure`` pronto
per essere passato a ``st.plotly_chart()``.
"""

from typing import Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Grafico 1 — Prezzi normalizzati
# ---------------------------------------------------------------------------

def plot_prices(prices: pd.DataFrame) -> go.Figure:
    """Grafico a linee dei prezzi storici normalizzati (base 100).

    Parameters
    ----------
    prices : pd.DataFrame
        Prezzi storici con indice datetime e una colonna per ticker.

    Returns
    -------
    go.Figure
    """
    normalized: pd.DataFrame = prices / prices.iloc[0] * 100

    fig = go.Figure()
    for col in normalized.columns:
        fig.add_trace(
            go.Scatter(
                x=normalized.index,
                y=normalized[col],
                mode="lines",
                name=str(col),
            )
        )

    fig.update_layout(
        title="Andamento Prezzi Normalizzati (base 100)",
        xaxis_title="Data",
        yaxis_title="Prezzo normalizzato",
        legend_title="Ticker",
        template="plotly_dark",
        height=500,
    )
    return fig


# ---------------------------------------------------------------------------
# Grafico 2 — Distribuzione rendimenti + VaR lines
# ---------------------------------------------------------------------------

def plot_returns_distribution(
    port_returns: pd.Series,
    hist_var: float,
    param_var: float,
    mc_var: float,
    confidence: float,
) -> go.Figure:
    """Istogramma dei rendimenti con curva normale e linee VaR.

    Parameters
    ----------
    port_returns : pd.Series
        Rendimenti giornalieri del portafoglio.
    hist_var, param_var, mc_var : float
        VaR delle tre metodologie (positivi, in unità decimali).
    confidence : float
        Livello di confidenza.

    Returns
    -------
    go.Figure
    """
    mu = float(port_returns.mean())
    sigma = float(port_returns.std())

    # Istogramma
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=port_returns.values,
            nbinsx=60,
            name="Rendimenti",
            marker_color="steelblue",
            opacity=0.7,
            histnorm="probability density",
        )
    )

    # Curva normale sovrapposta
    x_range = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 300)
    y_norm = norm.pdf(x_range, mu, sigma)
    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=y_norm,
            mode="lines",
            name="Normale (μ, σ)",
            line=dict(color="white", width=2, dash="dot"),
        )
    )

    # Colori per le linee VaR
    var_lines = [
        (-hist_var, "Historical VaR", "red"),
        (-param_var, "Parametric VaR", "orange"),
        (-mc_var, "Monte Carlo VaR", "purple"),
    ]

    for val, name, color in var_lines:
        fig.add_vline(
            x=val,
            line_width=2,
            line_dash="dash",
            line_color=color,
            annotation_text=name,
            annotation_position="top",
        )

    fig.update_layout(
        title="Distribuzione dei Rendimenti del Portafoglio",
        xaxis_title="Rendimento giornaliero",
        yaxis_title="Densità di probabilità",
        template="plotly_dark",
        height=500,
        legend=dict(x=0.02, y=0.98),
    )
    return fig


# ---------------------------------------------------------------------------
# Grafico 3 — Monte Carlo P&L
# ---------------------------------------------------------------------------

def plot_montecarlo_simulations(
    simulated_pnl: np.ndarray,
    mc_var: float,
    confidence: float,
    n_display: int = 200,
) -> go.Figure:
    """Istogramma dei P&L simulati con evidenziazione delle code.

    Parameters
    ----------
    simulated_pnl : np.ndarray
        Array dei P&L simulati.
    mc_var : float
        VaR Monte Carlo (positivo, in unità decimali).
    confidence : float
        Livello di confidenza.
    n_display : int, default 200
        Numero mostrato nel titolo (per info).

    Returns
    -------
    go.Figure
    """
    # Crea bins e determina quali sono "in code" (oltre il VaR)
    n_bins = 80
    counts, bin_edges = np.histogram(simulated_pnl, bins=n_bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    var_threshold = -mc_var  # soglia negativa

    # Separa barre normali vs code
    colors = ["red" if center <= var_threshold else "steelblue" for center in bin_centers]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=bin_centers,
            y=counts,
            marker_color=colors,
            width=bin_width,
            showlegend=False,
        )
    )

    # Linea VaR
    fig.add_vline(
        x=var_threshold,
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text=f"VaR {confidence * 100:.0f}%",
        annotation_position="top",
    )

    fig.update_layout(
        title=f"Distribuzione P&L Simulati — Monte Carlo ({len(simulated_pnl):,} simulazioni)",
        xaxis_title="P&L (rendimento totale)",
        yaxis_title="Frequenza",
        template="plotly_dark",
        height=500,
    )
    return fig


# ---------------------------------------------------------------------------
# Grafico 4 — Heatmap correlazioni
# ---------------------------------------------------------------------------

def plot_correlation_heatmap(returns: pd.DataFrame) -> go.Figure:
    """Heatmap della matrice di correlazione dei rendimenti.

    Parameters
    ----------
    returns : pd.DataFrame
        Rendimenti giornalieri con una colonna per ticker.

    Returns
    -------
    go.Figure
    """
    corr = returns.corr()

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=[str(c) for c in corr.columns],
            y=[str(c) for c in corr.index],
            colorscale="RdYlGn",
            zmin=-1,
            zmax=1,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            textfont={"size": 12},
            colorbar=dict(title="ρ"),
        )
    )

    fig.update_layout(
        title="Matrice di Correlazione dei Rendimenti",
        template="plotly_dark",
        height=500,
    )
    return fig


# ---------------------------------------------------------------------------
# Grafico 5 — Pie chart pesi
# ---------------------------------------------------------------------------

def plot_weights_pie(weights: Dict[str, float]) -> go.Figure:
    """Grafico a torta della composizione del portafoglio.

    Parameters
    ----------
    weights : dict[str, float]
        Dizionario ``{ticker: peso}`` normalizzato.

    Returns
    -------
    go.Figure
    """
    labels = list(weights.keys())
    values = [w * 100 for w in weights.values()]  # in percentuale

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                textinfo="label+percent",
                hole=0.3,
            )
        ]
    )

    fig.update_layout(
        title="Composizione del Portafoglio",
        template="plotly_dark",
        height=400,
    )
    return fig
