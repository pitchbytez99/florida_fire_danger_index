from homeassistant.helpers.storage import Store
from homeassistant.util import dt
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

class FloridaFDICoordinator(DataUpdateCoordinator):
    def __init__(self, hass, county):
        # Initialize Store to save last data
        self.store = Store(hass, 1, f"{county}_county_fdi_storage.json")
        self.county = county
        # ...

    async def _async_update_data(self):
        try:
            data = await self.hass.async_add_executor_job(self._fetch_data)
            
            await self.store.async_save({
                "fdi": data,
                "last_update": self.hass.helpers.event.dt.utcnow().isoformat()
            })
            
            return data
        
        except Exception as err:
            # On failure, try to load last data from storage
            last = await self.store.async_load()
            
            if last:
                return last.get("fdi")
            
            raise UpdateFailed(f"Error fetching FDI and no cache: {err}")
