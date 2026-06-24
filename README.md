# 📊 VaR Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dashboard interattiva per il calcolo del **Value at Risk (VaR)** di un
portafoglio azionario con tre metodologie: **Historical**, **Parametric** e
**Monte Carlo**.

I dati di mercato vengono scaricati in tempo reale da **Yahoo Finance**.

![Screenshot](screenshot.png)

---

## Metodologie VaR implementate

### 1. Historical Simulation (Non parametrico)

Utilizza direttamente la distribuzione empirica dei rendimenti storici.

**VaR:**
$$VaR_{\alpha} = -\text{percentile}(r,\; (1-\alpha) \times 100)$$

**CVaR (Expected Shortfall):**
$$CVaR_{\alpha} = -\mathbb{E}[r \mid r \leq -VaR_{\alpha}]$$

✅ Nessuna assunzione sulla distribuzione
❌ Sensibile alla finestra temporale scelta

---

### 2. Parametric (Variance-Covariance)

Assume che i rendimenti seguano una distribuzione normale $N(\mu, \sigma^2)$.

**VaR:**
$$VaR_{\alpha} = -(\mu + \sigma \cdot \Phi^{-1}(1-\alpha))$$

**CVaR:**
$$CVaR_{\alpha} = -\left(\mu - \sigma \cdot \frac{\phi(\Phi^{-1}(1-\alpha))}{1-\alpha}\right)$$

✅ Calcolo veloce, formula chiusa
❌ Assume normalità (sottostima le code pesanti)

---

### 3. Monte Carlo Simulation

Simula migliaia di percorsi futuri del portafoglio campionando dalla
distribuzione normale con i parametri stimati.

**Procedura:**
1. Stima $\mu$ e $\sigma$ dai rendimenti storici
2. Genera $N$ simulazioni di $H$ giorni: $r^{(i)} \sim N(0, \sigma^2)$
3. Calcola il P&L cumulato per ciascuna simulazione
4. VaR = percentile $(1-\alpha)$ della distribuzione dei P&L

✅ Flessibile (può usare distribuzioni alternative)
❌ Computazionalmente intensivo

---

## Struttura del progetto

```
var-dashboard/
├── app.py                      # Entry point Streamlit
├── requirements.txt            # Dipendenze
├── README.md                   # Questo file
├── .gitignore
├── data/
│   └── loader.py               # Download Yahoo Finance + log-rendimenti
├── models/
│   ├── historical_var.py       # Historical VaR / CVaR
│   ├── parametric_var.py       # Parametric VaR / CVaR (normale)
│   └── montecarlo_var.py       # Monte Carlo VaR / CVaR
├── ui/
│   ├── sidebar.py              # Controlli input utente
│   ├── charts.py               # Grafici Plotly (5 grafici)
│   └── metrics.py              # Card metriche (st.metric)
└── utils/
    └── portfolio.py            # Pesi, rendimenti, statistiche portafoglio
```

---

## Installazione

### Prerequisiti
- Python 3.10+
- pip

### Step

```bash
# 1. Clona la repo
git clone https://github.com/<username>/var-dashboard.git
cd var-dashboard

# 2. Ambiente virtuale (consigliato)
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. Avvia la dashboard
streamlit run app.py
```

La dashboard sarà disponibile su `http://localhost:8501`.

---

## Come usare la dashboard

1. **Seleziona i ticker** nella sidebar (default: 8 titoli US + IT)
2. **Imposta i pesi** con gli slider (verranno normalizzati automaticamente)
3. **Scegli il periodo storico** (1y, 2y, 3y, 5y)
4. **Imposta il confidence level** (90%, 95%, 99%)
5. **Inserisci il valore del portafoglio** in €
6. **Configura Monte Carlo**: numero simulazioni e orizzonte
7. Clicca **▶ Calcola VaR**
8. Esplora le 4 tab: Overview, VaR Analysis, Monte Carlo, Correlazioni

---

## Tecnologie

| Componente | Libreria |
|---|---|
| Web app | [Streamlit](https://streamlit.io) |
| Dati di mercato | [yfinance](https://pypi.org/project/yfinance/) |
| Calcolo numerico | [NumPy](https://numpy.org), [SciPy](https://scipy.org) |
| Manipolazione dati | [pandas](https://pandas.pydata.org) |
| Grafici | [Plotly](https://plotly.com/python/) |

---

## Disclaimer

> ⚠️ **Questo progetto è a scopo educativo. Non costituisce consulenza finanziaria.**
> Le stime VaR sono basate su modelli semplificati e dati storici.
> Non utilizzare come unico strumento per decisioni di investimento.

---

## Licenza

MIT License — vedi [LICENSE](LICENSE) per i dettagli.
