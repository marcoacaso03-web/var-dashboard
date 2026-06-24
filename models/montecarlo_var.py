"""
Modello Monte Carlo VaR / CVaR.

Simula percorsi futuri del portafoglio campionando dalla distribuzione
normale con i parametri (media, deviazione standard) stimati sui dati storici.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Seed riproducibile
# ---------------------------------------------------------------------------
RANDOM_SEED: int = 42


# ---------------------------------------------------------------------------
# Monte Carlo VaR
# ---------------------------------------------------------------------------

def montecarlo_var(
    port_returns: pd.Series,
    confidence: float = 0.95,
    n_simulations: int = 10000,
    horizon: int = 1,
) -> tuple[float, np.ndarray]:
    """Calcola il VaR tramite simulazione Monte Carlo.

    Procedura:
    1. Stima media e deviazione standard dai rendimenti storici.
    2. Genera una matrice di rendimenti simulati.
    3. Somma i rendimenti su tutti gli giorni dell'orizzonte.
    4. Calcola il VaR come percentile della distribuzione dei P&L.

    Parameters
    ----------
    port_returns : pd.Series
        Rendimenti storici del portafoglio.
    confidence : float, default 0.95
        Livello di confidenza.
    n_simulations : int, default 10000
        Numero di simulazioni.
    horizon : int, default 1
        Orizzonte temporale in giorni.

    Returns
    -------
    tuple[float, np.ndarray]
        - ``var_value``: VaR positivo.
        - ``simulated_pnl``: array completo dei P&L simulati (per grafici).
    """
    float(port_returns.mean())
    sigma = float(port_returns.std())

    # Seed riproducibile
    rng = np.random.default_rng(RANDOM_SEED)

    # Matrice di rendimenti simulati: (n_simulations, horizon)
    simulated_returns = rng.normal(0, sigma, size=(n_simulations, horizon))

    # P&L = somma dei rendimenti su tutti gli giorni dell'orizzonte
    simulated_pnl: np.ndarray = simulated_returns.sum(axis=1)

    # VaR come percentile
    var_value: float = float(-np.percentile(simulated_pnl, (1 - confidence) * 100))
    return var_value, simulated_pnl


# ---------------------------------------------------------------------------
# Monte Carlo CVaR
# ---------------------------------------------------------------------------

def montecarlo_cvar(
    simulated_pnl: np.ndarray,
    confidence: float = 0.95,
) -> float:
    """Calcola il CVaR Monte Carlo come media dei P&L sotto la soglia VaR.

    Parameters
    ----------
    simulated_pnl : np.ndarray
        Array dei P&L simulati (output di ``montecarlo_var``).
    confidence : float, default 0.95
        Livello di confidenza.

    Returns
    -------
    float
        CVaR positivo (perdita attesa oltre il VaR).
    """
    var_threshold = -np.percentile(simulated_pnl, (1 - confidence) * 100)
    tail = simulated_pnl[simulated_pnl <= var_threshold]
    if tail.empty:
        return float(-simulated_pnl.min())
    return float(-tail.mean())
