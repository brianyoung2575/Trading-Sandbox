import numpy as np

def step_price(S, mu=0.0005, sigma=0.02, dt=1):
    z = np.random.normal(0, 1)
    return S * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)