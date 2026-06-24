"""
Modulo per la gestione del portafoglio.

Gestisce la normalizzazione dei pesi, il calcolo dei rendimenti
di portafoglio e le statistiche riassuntive.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """Normalizza i pesi del portafoglio in modo che sommino a 1.

    Parameters
    ----------
    weights : dict[str, float]
        Dizionario ``{ticker: peso}``. I pesi non devono essere necessariamente
        normalizzati (es. ``{"AAPL": 30, "MSFT": 70}``).

    Returns
    -------
    dict[str, float]
        Dizionario con pesi normalizzati che sommano a 1.0.

    Raises
    ------
    ValueError
        Se la somma dei pesi è zero.
    """
    total = sum(weights.values())
    if total == 0:
        raise ValueError("La somma dei pesi è zero. Imposta almeno un peso > 0.")
    return {ticker: w / total for ticker, w in weights.items()}


def portfolio_returns(
    returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    """Calcola la serie temporale dei rendimenti del portafoglio.

    Il rendimento di portafoglio al tempo t è la media ponderata:

    .. math::

        r^{port}_t = \\sum_{i=1}^{N} w_i \\cdot r_{i,t}

    Parameters
    ----------
    returns : pd.DataFrame
        DataFrame dei rendimenti con una colonna per ogni ticker.
    weights : dict[str, float]
        Dizionario ``{ticker: peso}`` (normalizzato).

    Returns
    -------
    pd.Series
        Serie temporale dei rendimenti di portafoglio.
    """
    # Seleziona solo i ticker presenti in returns
    aligned_weights = {
        t: w for t, w in weights.items() if t in returns.columns
    }
    # Ricalcola normalizzazione nel caso alcuni ticker manchino
    total = sum(aligned_weights.values())
    if total == 0:
        raise ValueError("Nessun ticker del portafoglio è presente nei dati.")
    aligned_weights = {t: w / total for t, w in aligned_weights.items()}

    # Calcolo media ponderata
    port_ret = pd.Series(0.0, index=returns.index, dtype=float)
    for ticker, weight in aligned_weights.items():
        port_ret += weight * returns[ticker]

    port_ret.name = "portfolio_return"
    return port_ret


def portfolio_stats(port_returns: pd.Series) -> dict[str, float]:
    """Calcola le statistiche riassuntive del portafoglio.

    Parameters
    ----------
    port_returns : pd.Series
        Rendimenti giornalieri del portafoglio.

    Returns
    -------
    dict[str, float]
        Dizionario con:
        - ``mean``: rendimento medio giornaliero
        - ``std``: deviazione standard giornaliera
        - ``annualized_return``: rendimento annualizzato (mean × 252)
        - ``annualized_vol``: volatilità annualizzata (std × √252)
        - ``sharpe``: Sharpe ratio annualizzato
    """
    mean = float(port_returns.mean())
    std = float(port_returns.std())
    ann_ret = mean * 252
    ann_vol = std * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else 0.0

    return {
        "mean": mean,
        "std": std,
        "annualized_return": ann_ret,
        "annualized_vol": ann_vol,
        "sharpe": sharpe,
    }
