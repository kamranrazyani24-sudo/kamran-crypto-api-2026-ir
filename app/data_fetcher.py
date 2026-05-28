from typing import List, Dict


def fetch_klines(symbol: str, timeframe: str, limit: int = 200) -> List[Dict]:
    """
    خروجی استاندارد (نمونه):
    [
      {"open":..., "high":..., "low":..., "close":..., "volume":...},
      ...
    ]
    فعلاً اسکلت است تا برنامه بدون خطای import بالا بیاید.
    """
    return []
