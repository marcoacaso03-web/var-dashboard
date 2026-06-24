"""
Componente metriche VaR Dashboard.

Renderizza le card metriche (st.metric) per le statistiche di portafoglio
e il confronto VaR/CVaR tra le tre metodologie.
"""

from typing import Dict

import streamlit as st


def render_portfolio_stats(stats: dict[str, float], n_assets: int) -> None:
    """Mostra una riga di 4 metriche chiave del portafoglio.

    Parameters
    ----------
    stats : dict
        Dizionario da ``portfolio_stats()`` con chiavi:
        ``annualized_return``, ``annualized_vol``, ``sharpe``.
    n_assets : int
        Numero di titoli nel portafoglio.
    """
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📈 Rend. Annualizzato",
        f"{stats['annualized_return'] * 100:.2f}%",
    )
    col2.metric(
        "📉 Vol. Annualizzata",
        f"{stats['annualized_vol'] * 100:.2f}%",
    )
    col3.metric(
        "⚖️ Sharpe Ratio",
        f"{stats['sharpe']:.3f}",
    )
    col4.metric(
        "📁 Num. Titoli",
        str(n_assets),
    )


def render_var_comparison(
    hist_var: float,
    param_var: float,
    mc_var: float,
    hist_cvar: float,
    param_cvar: float,
    mc_cvar: float,
    confidence: float,
    portfolio_value: float,
) -> None:
    """Mostra il confronto VaR / CVaR tra le tre metodologie.

    Due righe da 3 colonne: prima i VaR, poi i CVaR.
    Ogni metrica mostra la perdita in %% e in €.

    Parameters
    ----------
    hist_var : float
        Historical VaR (valore positivo, in unità decimali, es. 0.025).
    param_var : float
        Parametric VaR.
    mc_var : float
        Monte Carlo VaR.
    hist_cvar : float
        Historical CVaR.
    param_cvar : float
        Parametric CVaR.
    mc_cvar : float
        Monte Carlo CVaR.
    confidence : float
        Livello di confidenza (per la label).
    portfolio_value : float
        Valore del portafoglio in € (per il calcolo del valore monetario).
    """
    st.markdown(f"**VaR / CVaR — Confidence: {confidence * 100:.0f}%**")

    # --- VaR row ---
    v1, v2, v3 = st.columns(3)

    hist_eur = hist_var * portfolio_value
    param_eur = param_var * portfolio_value
    mc_eur = mc_var * portfolio_value

    v1.metric(
        "📊 Historical VaR",
        f"{hist_var * 100:.2f}%",
        delta=f"-€{hist_eur:,.0f}",
        delta_color="inverse",
    )
    v2.metric(
        "📐 Parametric VaR",
        f"{param_var * 100:.2f}%",
        delta=f"-€{param_eur:,.0f}",
        delta_color="inverse",
    )
    v3.metric(
        "🎲 Monte Carlo VaR",
        f"{mc_var * 100:.2f}%",
        delta=f"-€{mc_eur:,.0f}",
        delta_color="inverse",
    )

    # --- CVaR row ---
    c1, c2, c3 = st.columns(3)

    hist_cvar_eur = hist_cvar * portfolio_value
    param_cvar_eur = param_cvar * portfolio_value
    mc_cvar_eur = mc_cvar * portfolio_value

    c1.metric(
        "📊 Historical CVaR",
        f"{hist_cvar * 100:.2f}%",
        delta=f"-€{hist_cvar_eur:,.0f}",
        delta_color="inverse",
    )
    c2.metric(
        "📐 Parametric CVaR",
        f"{param_cvar * 100:.2f}%",
        delta=f"-€{param_cvar_eur:,.0f}",
        delta_color="inverse",
    )
    c3.metric(
        "🎲 Monte Carlo CVaR",
        f"{mc_cvar * 100:.2f}%",
        delta=f"-€{mc_cvar_eur:,.0f}",
        delta_color="inverse",
    )
