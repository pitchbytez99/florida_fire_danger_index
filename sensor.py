from homeassistant.helpers.entity import SensorEntity
from datetime import datetime
from .const import (
    ONE_DAY, FLORIDA_FDI_URL, TABLE_DATAFRAME,
    COUNTY_COL_INDEX, FDI_COL_INDEX
)

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Florida Fire Danger Index sensor from config flow."""
    selected_county = config_entry.data["county"]
    
    sensor = FloridaFireDangerIndexSensor(selected_county)
    
    async_add_entities([sensor], update_before_add=True)

class FloridaFireDangerIndexSensor(SensorEntity):
    def __init__(self, county):
        self._county = county
        self._attr_name = f"{county} County Fire Danger Index"
        self._attr_unique_id = f"{county}_county_fire_danger_index"
        self._attr_native_value = None
        self._attr_icon = "mdi:fire-alert"
        self._fdi = None
        self._last_update = None
        
        @property
        def extra_state_attributes(self):
            return {
                "county": self._county,
                "fire_danger_index": self._fdi,
                "last_updated": self._last_update.isoformat() if self._last_update else None,
            }
        
    def _fetch_data(self):
        try:
            agent_data = UserAgent()
            headers = {
                "User-Agent": agent_data.chrome,  # Random Chrome user agent
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
            }
            
            response = requests.get(FLORIDA_FDI_URL, headers=headers)
            response.raise_for_status()
            
        except:
            return None
    
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select(TABLE_DATAFRAME)
        
        for row in rows:
            county_entry = row.select(COUNTY_COL_INDEX)
            fdi_entry = row.select(FDI_COL_INDEX)
            
            if county_entry and fdi_entry:
                county_name = county_entry.text.strip()
                fdi_value = fdi_entry.text.strip()
                
                if county_name.lower() == self._county.lower():
                    return fdi_value
                    
        return None

    async def async_update(self):
        """Fetch the latest fire index data."""
        now = datetime.utcnow()
        
        # Skip updating this sensor if its been less than a day
        if self._last_update is not None and (now - self._last_update) < ONE_DAY:
            return
        
        data = await self.hass.async_add_executor_job(self._fetch_data)
        
        if data is not None:
            self._fdi = data
            self._attr_native_value = data
            self._last_update = now
