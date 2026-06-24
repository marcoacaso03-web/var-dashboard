"""
Modello Historical VaR / CVaR.

Metodo non parametrico: utilizza direttamente la distribuzione empirica
dei rendimenti storici senza assumere una forma funzionale specifica.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Historical VaR
# ---------------------------------------------------------------------------

def historical_var(port_returns: pd.Series, confidence: float = 0.95) -> float:
    """Calcola l'Historical VaR come percentile della distribuzione empirica.

    Il VaR al livello di confidenza :math:`\\alpha` è il rendimento peggiore
    al :math:`(1-\\alpha)`-esimo percentile:

    .. math::

        VaR_{\\alpha} = -\\text{percentile}(r, (1-\\alpha) \\times 100)

    Parameters
    ----------
    port_returns : pd.Series
        Rendimenti storici del portafoglio.
    confidence : float, default 0.95
        Livello di confidenza (es. 0.95 = 95%%).

    Returns
    -------
    float
        VaR positivo (rappresenta una perdita).
    """
    return float(-np.percentile(port_returns, (1 - confidence) * 100))


# ---------------------------------------------------------------------------
# Historical CVaR (Expected Shortfall)
# ---------------------------------------------------------------------------

def historical_cvar(port_returns: pd.Series, confidence: float = 0.95) -> float:
    """Calcola l'Historical CVaR (Expected Shortfall).

    Il CVaR è la media dei rendimenti che si trovano sotto la soglia del VaR:

    .. math::

        CVaR_{\\alpha} = -\\mathbb{E}[r \\mid r \\leq -VaR_{\\alpha}]

    Parameters
    ----------
    port_returns : pd.Series
        Rendimenti storici del portafoglio.
    confidence : float, default 0.95
        Livello di confidenza.

    Returns
    -------
    float
        CVaR positivo (perdita attesa oltre il VaR).
    """
    var_threshold = -historical_var(port_returns, confidence)
    tail = port_returns[port_returns <= var_threshold]
    if tail.empty:
        return float(-port_returns.min())
    return float(-tail.mean())
