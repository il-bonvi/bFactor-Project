# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

from typing import Dict, List

import requests


class IntervalsClient:
    def __init__(self, base_url: str = "https://intervals.icu/api/v1"):
        self.base_url = base_url.rstrip("/")

    def fetch_intervals(self, api_key: str, athlete_id: int) -> List[Dict]:
        # Placeholder for real API integration. Return empty list if call fails.
        try:
            resp = requests.get(
                f"{self.base_url}/athlete/{athlete_id}/intervals",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data if isinstance(data, list) else []
        except Exception:
            return []
        return []
