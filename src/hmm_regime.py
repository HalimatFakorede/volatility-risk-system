import numpy as np
from hmmlearn.hmm import GaussianHMM

def detect_hmm_regime(df, col="Return", n_states=2):
    X = df[col].dropna().values.reshape(-1, 1)

    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=100
    )
    model.fit(X)

    states = model.predict(X)

    regime_map = {
        np.argmax(model.means_): "Stress",
        np.argmin(model.means_): "Calm"
    }

    df.loc[df[col].dropna().index, "HMM_Regime"] = [
        regime_map[s] for s in states
    ]

    return df
