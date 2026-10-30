"""Runpod compute arithmetic only. Prices are inputs, not live quotations."""
import math


def budget_ceiling(balance, gpu_per_hour, storage_per_hour, reserve):
    values = (balance, gpu_per_hour, storage_per_hour, reserve)
    if any(x is None or not isinstance(x, (float, int)) or isinstance(x, bool) or not math.isfinite(x) for x in values):
        raise ValueError("All cost inputs must be current finite numbers")
    if any(x < 0 for x in values) or gpu_per_hour <= 0 or reserve > balance:
        raise ValueError("Invalid price, balance or reserve")
    available = balance - reserve
    return {"available_compute_budget": available,
            "maximum_hours": available / (gpu_per_hour + storage_per_hour),
            "gpu_per_hour": gpu_per_hour,
            "storage_per_hour": storage_per_hour,
            "reserve": reserve,
            "price_status": "USER_SUPPLIED_EXAMPLE_NOT_LIVE_QUOTE"}
