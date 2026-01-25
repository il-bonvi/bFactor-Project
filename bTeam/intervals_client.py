# ===============================================================================
# Copyright (c) 2026 Andrea Bonvicin - bFactor Project
# PROPRIETARY LICENSE - TUTTI I DIRITTI RISERVATI
# Sharing, distribution or reproduction is strictly prohibited.
# La condivisione, distribuzione o riproduzione è severamente vietata.
# ===============================================================================

from __future__ import annotations

import logging
from typing import Dict, List

import requests

logger = logging.getLogger(__name__)


class IntervalsClient:
    def __init__(self, base_url: str = "https://intervals.icu/api/v1"):
        self.base_url = base_url.rstrip("/")

    def fetch_intervals(self, api_key: str, athlete_id: int) -> List[Dict]:
        """
        Recupera gli intervalli dall'API Intervals.icu
        
        Args:
            api_key: API key dell'atleta
            athlete_id: ID dell'atleta
            
        Returns:
            Lista di intervalli o lista vuota in caso di errore
        """
        try:
            resp = requests.get(
                f"{self.base_url}/athlete/{athlete_id}/intervals",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data if isinstance(data, list) else []
            else:
                logger.warning(f"Intervals.icu API returned status {resp.status_code}")
                return []
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching intervals for athlete {athlete_id}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching intervals for athlete {athlete_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching intervals: {e}", exc_info=True)
            return []
