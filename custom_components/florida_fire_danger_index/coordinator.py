from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.storage import Store
from homeassistant.util.dt import parse_datetime, utcnow
from datetime import timedelta
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
from .const import FLORIDA_FDI_URL

_LOGGER = logging.getLogger(__name__)

class FloridaFDICoordinator(DataUpdateCoordinator):
    def __init__(self, hass, county):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{county} County Fire Danger Index",
            update_interval=timedelta(days=1)
        )
        
        self.county = county
        self.store = Store(hass, 1, f"{county.lower().replace(' ', '_')}_fdi_storage")
        self._last_update = None
        
    async def _async_load_cached_data(self):
        cached = await self.store.async_load()
        
        if cached:
            data = cached.get("data")
            last_update_iso = cached.get("last_update")
            
            if last_update_iso:
                self._last_update = parse_datetime(last_update_iso)
                
            self.async_set_updated_data(data)
                
    async def _async_update_data(self):
        try:
            data = await self.hass.async_add_executor_job(self._fetch_data)
            self._last_update = utcnow()
            
            await self.store.async_save({
                "data": data,
                "last_update": self._last_update.isoformat(),
            })
            
            return data
        
        except Exception as err:
            _LOGGER.error("Failed to fetch Fire Danger Index data: %s", err)
            
            if self.data is not None:
                return self.data
            
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
            
            _LOGGER.info("Fetching Fire Danger Index from URL: %s", FLORIDA_FDI_URL)
            
            response = requests.get(FLORIDA_FDI_URL, headers=headers)
            response.raise_for_status()
            
            _LOGGER.info("Received response status: %s", response.status_code)
            
        except Exception as e:
            _LOGGER.warning("Error fetching data from %s: %s", FLORIDA_FDI_URL, e)
            return None
    
        soup = BeautifulSoup(response.text, "html.parser")
        
        county_cell = soup.find("td", string=self.county)
        
        if county_cell:
            fire_danger_index_cell = county_cell.find_next_sibling("td")
            fdi_value = fire_danger_index_cell.get_text(strip=True)
            
            _LOGGER.info("Match found for county '%s': FDI=%s", self.county, fdi_value)
            
            return fdi_value
                    
        _LOGGER.warning("No matching county found for '%s'", self.county)
        return "Unknown"

    @property
    def last_update(self):
        return self._last_update
