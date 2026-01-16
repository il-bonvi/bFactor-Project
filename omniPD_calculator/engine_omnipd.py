import numpy as np
from scipy.optimize import curve_fit

# =========================
# COSTANTI DI MODELLO
# =========================
TCPMAX = 1800  # 30 minuti (limite per il decadimento lineare/logaritmico)

def ompd_power_formula(t, CP, W_prime, Pmax, A):
    """
    Modello OmniPD: combina la potenza critica classica (Monod) 
    con il decadimento per sforzi lunghi (A).
    """
    t = np.array(t, dtype=float)
    # Parte base (curva di Monod-Scherrer modificata per Pmax)
    base = (W_prime / t) * (1 - np.exp(-t * (Pmax - CP) / W_prime)) + CP
    
    # Se t > TCPMAX, applichiamo il decadimento di resistenza (A)
    P = np.where(t <= TCPMAX, base, base - A * np.log(t / TCPMAX))
    return P

def calculate_omnpd_fit(times, powers):
    """
    Esegue il fit dei dati reali sul modello OmniPD.
    Ritorna i parametri CP, W', Pmax, A e le metriche di errore.
    """
    times = np.array(times)
    powers = np.array(powers)
    
    # Initial guess basato sui dati inseriti:
    # CP: 30° percentile, W': 20kJ, Pmax: max potenza, A: costante 5
    p0 = [np.percentile(powers, 30), 20000, powers.max(), 5]
    
    try:
        params, _ = curve_fit(
            ompd_power_formula, 
            times, 
            powers, 
            p0=p0, 
            maxfev=20000
        )
        
        CP, W_prime, Pmax, A = params
        
        # Calcolo errori (RMSE e MAE)
        predictions = ompd_power_formula(times, *params)
        residuals = powers - predictions
        rmse = np.sqrt(np.mean(residuals**2))
        mae = np.mean(np.abs(residuals))
        
        return {
            "success": True,
            "params": {"CP": CP, "W_prime": W_prime, "Pmax": Pmax, "A": A},
            "metrics": {"RMSE": rmse, "MAE": mae},
            "predictions": predictions
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_weff(t, W_prime, CP, Pmax):
    """Calcola il W' efficace (Joule spesi effettivamente in funzione del tempo)"""
    return W_prime * (1 - np.exp(-t * (Pmax - CP) / W_prime))