import pandas as pd
from arch import arch_model

def compute_garch_volatility(returns):
    """
    Estimate conditional volatility using a GARCH(1,1) model.

    Notes:
    - Returns are scaled by 100 prior to modeling.
    - This is standard practice for ARCH/GARCH models to improve numerical stability
      and interpretability of volatility estimates.
    """
    clean_returns = returns.dropna() * 100

    model = arch_model(
        clean_returns,       
        vol="Garch",
        p=1,
        q=1,
        mean="Zero"
    )

    fitted = model.fit(disp="off")

    return pd.Series(
        fitted.conditional_volatility,
        index=clean_returns.index,
        name="GARCH_Volatility"
    )