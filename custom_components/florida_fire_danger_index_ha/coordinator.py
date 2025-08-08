from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.storage import Store
from homeassistant.util import dt
from datetime import timedelta
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
from .const import (
    FLORIDA_FDI_URL,
    TABLE_DATAFRAME,
    COUNTY_COL_INDEX,
    FDI_COL_INDEX,
)

_LOGGER = logging.getLogger(__name__)

class FloridaFDICoordinator(DataUpdateCoordinator):
    def __init__(self, hass, county):
        self.county = county
        self.store = Store(hass, 1, f"{county.lower().replace(' ', '_')}_fdi_storage")
        self._data = None
        self._last_update = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"{county} County Fire Danger Index",
            update_interval=timedelta(days=1),
        )
        
    async def _async_load_cached_data(self):
        cached = await self.store.async_load()
        
        if cached:
            self._data = cached.get("data")
            last_update_iso = cached.get("last_update")
            
            if last_update_iso:
                self._last_update = self.hass.helpers.event.dt.parse_datetime(last_update_iso)
                
    async def _async_update_data(self):
        try:
            data = await self.hass.async_add_executor_job(self._fetch_data)
            self._data = data
            self._last_update = self.hass.helpers.event.dt.utcnow()
            
            await self.store.async_save({
                "data": data,
                "last_update": self._last_update.isoformat(),
            })
            return data
        
        except Exception as err:
            _LOGGER.error("Failed to fetch Fire Danger Index data: %s", err)
            
            if self._data is not None:
                return self._data
            
            raise UpdateFailed(f"Error fetching Fire Danger Index data: {err}")

        
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
                
                if county_name.lower() == self.county.lower():
                    return fdi_value
                    
        return None
    
    @property
    def data(self):
        return self._data

    @property
    def last_update(self):
        return self._last_update
