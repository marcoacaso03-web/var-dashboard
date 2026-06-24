"""
Modulo per il download dei dati di mercato da Yahoo Finance.

Espone funzioni per scaricare prezzi adjusted close e calcolare
i rendimenti logaritmici giornalieri.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------
DEFAULT_TICKERS: list[str] = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "JPM",
    "ENI.MI", "ENEL.MI", "UCG.MI",
]

MONTHS_TO_YEARS: dict[str, int] = {
    "1y": 1,
    "2y": 2,
    "3y": 3,
    "5y": 5,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def get_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Scarica i prezzi di chiusura aggiustati (Adj Close) da Yahoo Finance.

    Parameters
    ----------
    tickers : list[str]
        Lista di simboli ticker (es. ``["AAPL", "MSFT"]``).
    start : str
        Data di inizio nel formato ``"YYYY-MM-DD"``.
    end : str
        Data di fine nel formato ``"YYYY-MM-DD"``.

    Returns
    -------
    pd.DataFrame
        DataFrame con indice ``DatetimeIndex`` e una colonna per ogni ticker,
        contenente i prezzi di chiusura aggiustati.

    Raises
    ------
    ValueError
        Se nessun dato viene scaricato o il DataFrame è vuoto.
    """
    try:
        raw = yf.download(
            tickers,
            start=start,
            end=end,
            auto_adjust=True,
            progress=False,
        )
    except Exception as exc:
        raise ValueError(
            f"Errore di connessione a Yahoo Finance: {exc}"
        ) from exc

    if raw is None or raw.empty:
        raise ValueError(
            f"Nessun dato scaricato per {tickers}. "
            "Controlla i ticker e il periodo selezionato."
        )

    # auto_adjust=True → i prezzi sono già adjusted
    # Se c'è un solo ticker yfinance restituisce DataFrame con 'Close'
        # Se ci sono multipli, ha MultiIndex columns: ('Close', 'AAPL'), ...
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"].copy()
    else:
        prices = raw[["Close"]].copy()
        if len(tickers) == 1:
            prices.columns = tickers

    prices.dropna(inplace=True)

    if prices.empty:
        raise ValueError("Dati vuoti dopo la rimozione dei NaN.")

    return prices


@st.cache_data(ttl=3600)
def get_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calcola i rendimenti logaritmici giornalieri.

    Parameters
    ----------
    prices : pd.DataFrame
        DataFrame dei prezzi con indice datetime.

    Returns
    -------
    pd.DataFrame
        DataFrame dei log-rendimenti con la stessa struttura (prima riga rimossa).
    """
    log_ret: pd.DataFrame = np.log(prices / prices.shift(1))
    log_ret.dropna(inplace=True)
    return log_ret
