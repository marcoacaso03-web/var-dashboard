"""
Componente sidebar della VaR Dashboard.

Gestisce tutti i controlli input dell'utente nella sidebar Streamlit.
"""

from typing import Dict

import streamlit as st

from data.loader import DEFAULT_TICKERS


# ---------------------------------------------------------------------------
# Mapping periodo → anni
# ---------------------------------------------------------------------------
PERIOD_TO_YEARS: dict[str, int] = {
    "1y": 1,
    "2y": 2,
    "3y": 3,
    "5y": 5,
}


def render_sidebar() -> Dict[str, object]:
    """Renderizza la sidebar e raccoglie tutti i parametri di configurazione.

    Returns
    -------
    dict
        ``{"tickers": list, "weights": dict, "period": str,
          "confidence": float, "portfolio_value": float,
          "n_simulations": int, "horizon": int, "run": bool}``
    """
    st.sidebar.title("⚙️ Configurazione")

    # ------------------------------------------------------------------
    # 1. PORTAFOGLIO
    # ------------------------------------------------------------------
    st.sidebar.markdown("### 📁 Portafoglio")

    selected_tickers: list[str] = st.sidebar.multiselect(
        "Seleziona i ticker",
        options=DEFAULT_TICKERS,
        default=DEFAULT_TICKERS,
    )

    raw_weights: Dict[str, float] = {}
    if selected_tickers:
        st.sidebar.markdown("**Pesi**")
        for ticker in selected_tickers:
            raw_weights[ticker] = st.sidebar.slider(
                f"{ticker}",
                min_value=0.0,
                max_value=1.0,
                value=round(1.0 / len(selected_tickers), 2),
                step=0.05,
                label_visibility="visible",
            )

    st.sidebar.divider()

    # ------------------------------------------------------------------
    # 2. PARAMETRI ANALISI
    # ------------------------------------------------------------------
    st.sidebar.markdown("### 📊 Parametri Analisi")

    period: str = st.sidebar.selectbox(
        "Periodo storico",
        options=list(PERIOD_TO_YEARS.keys()),
        index=1,  # default "2y"
    )

    confidence: float = st.sidebar.selectbox(
        "Confidence level",
        options=[0.90, 0.95, 0.99],
        index=1,  # default 0.95
        format_func=lambda x: f"{x * 100:.0f}%",
    )

    portfolio_value: float = st.sidebar.number_input(
        "Valore del portafoglio (€)",
        min_value=1000.0,
        max_value=100_000_000.0,
        value=100_000.0,
        step=10_000.0,
        format="%.0f",
    )

    st.sidebar.divider()

    # ------------------------------------------------------------------
    # 3. MONTE CARLO
    # ------------------------------------------------------------------
    st.sidebar.markdown("### 🎲 Monte Carlo")

    n_simulations: int = st.sidebar.slider(
        "Numero simulazioni",
        min_value=1000,
        max_value=50000,
        value=10000,
        step=1000,
    )

    horizon: int = st.sidebar.slider(
        "Orizzonte (giorni)",
        min_value=1,
        max_value=30,
        value=1,
    )

    st.sidebar.divider()

    # ------------------------------------------------------------------
    # 4. Pulsante
    # ------------------------------------------------------------------
    run: bool = st.sidebar.button(
        "▶ Calcola VaR",
        type="primary",
        use_container_width=True,
    )

    return {
        "tickers": selected_tickers,
        "weights": raw_weights,
        "period": period,
        "confidence": confidence,
        "portfolio_value": portfolio_value,
        "n_simulations": n_simulations,
        "horizon": horizon,
        "run": run,
    }
