"""
VaR Dashboard — Entry point dell'applicazione Streamlit.

Dashboard interattiva per il calcolo del Value at Risk (VaR) di un
portafoglio azionario con tre metodologie:
  1. Historical Simulation
  2. Parametric (Variance-Covariance)
  3. Monte Carlo Simulation

Uso:
    streamlit run app.py
"""

from datetime import datetime, timedelta

import numpy as np
import streamlit as st

from data.loader import MONTHS_TO_YEARS, get_prices, get_returns
from models.historical_var import historical_cvar, historical_var
from models.montecarlo_var import montecarlo_cvar, montecarlo_var
from models.parametric_var import parametric_cvar, parametric_var
from ui.charts import (
    plot_correlation_heatmap,
    plot_montecarlo_simulations,
    plot_prices,
    plot_returns_distribution,
    plot_weights_pie,
)
from ui.metrics import render_portfolio_stats, render_var_comparison
from ui.sidebar import render_sidebar
from utils.portfolio import normalize_weights, portfolio_returns, portfolio_stats


# ---------------------------------------------------------------------------
# Helper: calcola data di inizio dal periodo selezionato
# ---------------------------------------------------------------------------

def _start_date(period: str) -> str:
    """Converte un periodo tipo '2y' in una data 'YYYY-MM-DD'."""
    years = MONTHS_TO_YEARS.get(period, 2)
    dt = datetime.today() - timedelta(days=years * 365)
    return dt.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="VaR Dashboard",
        page_icon="📊",
        layout="wide",
    )

    st.title("📊 Value at Risk Dashboard")
    st.caption(
        "Calcolo VaR di portafoglio con metodologie Historical, Parametric e Monte Carlo"
    )

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------
    params = render_sidebar()

    if not params["run"]:
        st.info(
            "👈 Configura il portafoglio nella sidebar e premi **▶ Calcola VaR** "
            "per avviare l'analisi."
        )
        return

    # Validazione input
    tickers: list[str] = params["tickers"]
    raw_weights: dict[str, float] = params["weights"]
    period: str = params["period"]
    confidence: float = params["confidence"]
    portfolio_value: float = params["portfolio_value"]
    n_simulations: int = params["n_simulations"]
    horizon: int = params["horizon"]

    if not tickers:
        st.error("Seleziona almeno un ticker.")
        st.stop()

    if not raw_weights or sum(raw_weights.values()) == 0:
        st.error("La somma dei pesi è zero. Imposta almeno un peso > 0.")
        st.stop()

    # ------------------------------------------------------------------
    # Download dati
    # ------------------------------------------------------------------
    try:
        with st.spinner("📡 Scaricamento dati da Yahoo Finance..."):
            start = _start_date(period)
            end = datetime.today().strftime("%Y-%m-%d")
            prices = get_prices(tickers, start, end)
            returns = get_returns(prices)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()
    except Exception as exc:
        st.error(f"Errore imprevisto: {exc}")
        st.stop()

    # ------------------------------------------------------------------
    # Calcolo portafoglio
    # ------------------------------------------------------------------
    weights = normalize_weights(raw_weights)
    port_returns = portfolio_returns(returns, weights)
    stats = portfolio_stats(port_returns)

    # ------------------------------------------------------------------
    # Calcolo VaR e CVaR
    # ------------------------------------------------------------------
    h_var = historical_var(port_returns, confidence)
    h_cvar = historical_cvar(port_returns, confidence)

    p_var = parametric_var(port_returns, confidence)
    p_cvar = parametric_cvar(port_returns, confidence)

    mc_var, simulated_pnl = montecarlo_var(
        port_returns, confidence, n_simulations, horizon
    )
    mc_cvar = montecarlo_cvar(simulated_pnl, confidence)

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview",
        "📊 VaR Analysis",
        "🎲 Monte Carlo",
        "🔗 Correlazioni",
    ])

    # ----- TAB 1: Overview -----
    with tab1:
        st.subheader("Statistiche del Portafoglio")
        render_portfolio_stats(stats, n_assets=len(tickers))

        st.subheader("Andamento Prezzi")
        st.plotly_chart(plot_prices(prices), use_container_width=True)

        st.subheader("Composizione del Portafoglio")
        st.plotly_chart(plot_weights_pie(weights), use_container_width=True)

    # ----- TAB 2: VaR Analysis -----
    with tab2:
        st.subheader("Confronto VaR / CVaR")
        render_var_comparison(
            hist_var=h_var,
            param_var=p_var,
            mc_var=mc_var,
            hist_cvar=h_cvar,
            param_cvar=p_cvar,
            mc_cvar=mc_cvar,
            confidence=confidence,
            portfolio_value=portfolio_value,
        )

        st.subheader("Distribuzione dei Rendimenti")
        st.plotly_chart(
            plot_returns_distribution(
                port_returns, h_var, p_var, mc_var, confidence
            ),
            use_container_width=True,
        )

    # ----- TAB 3: Monte Carlo -----
    with tab3:
        st.subheader("Parametri Simulazione")
        col1, col2 = st.columns(2)
        col1.metric("Simulazioni", f"{n_simulations:,}")
        col2.metric("Orizzonte", f"{horizon} giorni")

        st.subheader("Distribuzione P&L Simulati")
        st.plotly_chart(
            plot_montecarlo_simulations(
                simulated_pnl, mc_var, confidence, n_simulations
            ),
            use_container_width=True,
        )

        st.subheader("VaR a Diversi Livelli di Confidenza")
        conf_levels = [0.90, 0.95, 0.99]
        mc_var_levels = {}
        mc_cvar_levels = {}
        for cl in conf_levels:
            v, pnl = montecarlo_var(port_returns, cl, n_simulations, horizon)
            mc_var_levels[cl] = v
            mc_cvar_levels[cl] = montecarlo_cvar(pnl, cl)

        import pandas as pd
        summary_df = pd.DataFrame({
            "Confidence": [f"{cl * 100:.0f}%" for cl in conf_levels],
            "VaR (%)": [f"{mc_var_levels[cl] * 100:.2f}%" for cl in conf_levels],
            "CVaR (%)": [f"{mc_cvar_levels[cl] * 100:.2f}%" for cl in conf_levels],
            "VaR (€)": [f"€{mc_var_levels[cl] * portfolio_value:,.0f}" for cl in conf_levels],
            "CVaR (€)": [f"€{mc_cvar_levels[cl] * portfolio_value:,.0f}" for cl in conf_levels],
        })
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

    # ----- TAB 4: Correlazioni -----
    with tab4:
        st.subheader("Matrice di Correlazione")
        st.plotly_chart(
            plot_correlation_heatmap(returns),
            use_container_width=True,
        )

        st.subheader("Statistiche Individuali per Ticker")
        import pandas as pd
        rows = []
        for ticker in returns.columns:
            t_ret = returns[ticker]
            t_var = historical_var(t_ret, confidence)
            rows.append({
                "Ticker": ticker,
                "Peso (%)": f"{weights.get(ticker, 0) * 100:.1f}%",
                "Mean giornaliero": f"{t_ret.mean() * 100:.4f}%",
                "Std giornaliera": f"{t_ret.std() * 100:.4f}%",
                "VaR ind. (%)": f"{t_var * 100:.2f}%",
            })
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # ------------------------------------------------------------------
    # Disclaimer
    # ------------------------------------------------------------------
    st.divider()
    st.caption(
        "⚠️ **Disclaimer:** Questo progetto è a scopo educativo. "
        "Non costituisce consulenza finanziaria."
    )


if __name__ == "__main__":
    main()
