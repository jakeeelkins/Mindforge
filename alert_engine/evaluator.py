def compute_reorder_point(daily_demand: float, lead_time_days: int, safety_days: int = 2) -> int:
    """Simple ROP = demand * (lead time + safety)."""
    return max(1, int(round(daily_demand * (lead_time_days + safety_days))))

def severity_band(on_hand: int, min_threshold: int, rop: int) -> str:
    if on_hand <= 0:
        return "critical"
    if on_hand <= min_threshold:
        return "critical" if on_hand < max(1, min_threshold // 2) else "warning"
    if on_hand <= rop:
        return "warning"
    return "info"
