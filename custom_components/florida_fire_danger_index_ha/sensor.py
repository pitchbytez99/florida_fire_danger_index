from homeassistant.helpers.entity import SensorEntity
from .coordinator import FloridaFDICoordinator
from datetime import datetime
from .const import ONE_DAY

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Florida Fire Danger Index sensor from config flow."""
    selected_county = config_entry.data["county"]
    
    coordinator = FloridaFDICoordinator(hass, selected_county)
    
    await coordinator._async_load_cached_data()
    await coordinator._async_update_data()
    
    async_add_entities([FloridaFireDangerIndexSensor(coordinator)], update_before_add=True)

class FloridaFireDangerIndexSensor(SensorEntity):
    def __init__(self, county, coordinator):
        self.coordinator = coordinator
        self._attr_name = f"{county} County Fire Danger Index"
        self._attr_unique_id = f"{county}_county_fire_danger_index"
        self._attr_icon = "mdi:fire-alert"
        
        @property
        def native_value(self):
            return self.coordinator._data
        
        @property
        def extra_state_attributes(self):
            return {
                "county": self.coordinator.county,
                "last_updated": self.coordinator._last_update.isoformat() if  self.coordinator._last_updat else None,
            }
            
        @property
        def available(self):
            return self.coordinator.last_update is not None and self.coordinator.data is not None
        
        async def async_added_to_hass(self):
            self.async_on_remove(
                self.coordinator.async_add_listener(self.async_write_ha_state)
            )
