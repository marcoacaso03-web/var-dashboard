"""
Modello Parametric VaR / CVaR.

Assume che i rendimenti del portafoglio seguano una distribuzione normale
:math:`N(\\mu, \\sigma^2)`. Utilizza la funzione quantile (ppf) di scipy.
"""

from scipy.stats import norm
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Parametric VaR
# ---------------------------------------------------------------------------

def parametric_var(port_returns: pd.Series, confidence: float = 0.95) -> float:
    """Calcola il Parametric VaR assumendo distribuzione normale.

    Formula:

    .. math::

        VaR_{\\alpha} = -(\\mu + \\sigma \\cdot \\Phi^{-1}(1-\\alpha))

    dove :math:`\\Phi^{-1}` è la funzione quantile della normale standard.

    Parameters
    ----------
    port_returns : pd.Series
        Rendimenti storici del portafoglio.
    confidence : float, default 0.95
        Livello di confidenza.

    Returns
    -------
    float
        VaR positivo (perdita).
    """
    mu = float(port_returns.mean())
    sigma = float(port_returns.std())
    z = norm.ppf(1 - confidence)
    return float(-(mu + z * sigma))


# ---------------------------------------------------------------------------
# Parametric CVaR (Expected Shortfall per distribuzione normale)
# ---------------------------------------------------------------------------

def parametric_cvar(port_returns: pd.Series, confidence: float = 0.95) -> float:
    """Calcola il Parametric CVaR con formula analitica per normale.

    Formula:

    .. math::

        CVaR_{\\alpha} = -\\left(\\mu - \\sigma \\cdot
        \\frac{\\phi(\\Phi^{-1}(1-\\alpha))}{1-\\alpha}\\right)

    dove :math:`\\phi` è la PDF della normale standard.

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
    mu = float(port_returns.mean())
    sigma = float(port_returns.std())
    z = norm.ppf(1 - confidence)
    pdf_z = norm.pdf(z)
    return float(-(mu - sigma * pdf_z / (1 - confidence)))
