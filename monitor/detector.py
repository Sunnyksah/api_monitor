import numpy as np
from monitor.logger import get_logger

log = get_logger("detector")

def detect_anomalies(name: str, current_value: float, history: list, rules: dict) -> list[dict]:
    """
    Returns a list of triggered alerts (empty = all clear)
    Each alert: {"type": str, "message": str, "value": float}
    """

    alerts = []
    values = [h["value"] for h in history if h.get("value") is not None]

    #Rule 1: Spike % from last value
    spike_pct = rules.get("Spike_percent")
    if spike_pct and len(values) >= 1:
        last  = values[-1]
        if last != 0:
            change = abs((current_value - last) / last) * 100
            if change >= spike_pct:
                direction = "Up" if current_value > last else "Down"
                msg = (
                    f"{name}: {direction} {change:.2f}% spike detected. "
                    f"Previous: {last:,.4g} -> current: {current_value:,.4g}"
                )
                alerts.append({"type": "spike", "message": msg, "value": current_value})
                log.warning(msg)


    # Rule 2: Absolute min/max bounds
    min_value  = rules.get("min_value")
    max_value = rules.get("max_value")
    if min_value is not None and current_value < min_value:
        msg = f"{name}: Value {current_value:,.4g} is ABOVE maximum threshold {max_value:,.4g}"
        alerts.append({"type": "above_max", "message": msg, "value": current_value})
        log.warning(msg)

    # Rule 3: Z-score anomaly
    zscore_thres = rules.get("zscore_threshold")
    if zscore_thres and len(values) >= 10:
        arr = np.array(values[-50:])
        mean, std = arr.mean(), arr.std()
        if std > 0:
            z = abs((current_value - mean) / std)
            if z >= zscore_thres:
                msg = (
                    f"{name}: Statistical anamoly detected. "
                    f"Z-score= {z:.2f} (threshold = {zscore_thres}). "
                    f"Value={current_value:,.4g}, Mean={mean:,.4g} stdDev={std:,.4g}"
                )
                alerts.append({"type": "zscore", "message": msg, "value": current_value})
                log.warning(msg)

    return alerts