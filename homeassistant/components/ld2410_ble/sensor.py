"""LD2410 BLE integration sensor platform."""


from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import LD2410BLE, LD2410BLECoordinator
from .const import DOMAIN
from .models import LD2410BLEData

MOVING_TARGET_DISTANCE_DESCRIPTION = SensorEntityDescription(
    key="moving_target_distance",
    device_class=SensorDeviceClass.DISTANCE,
    entity_registry_enabled_default=False,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Moving Target Distance",
    native_unit_of_measurement=UnitOfLength.CENTIMETERS,
    state_class=SensorStateClass.MEASUREMENT,
)

STATIC_TARGET_DISTANCE_DESCRIPTION = SensorEntityDescription(
    key="static_target_distance",
    device_class=SensorDeviceClass.DISTANCE,
    entity_registry_enabled_default=False,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Static Target Distance",
    native_unit_of_measurement=UnitOfLength.CENTIMETERS,
    state_class=SensorStateClass.MEASUREMENT,
)

DETECTION_DISTANCE_DESCRIPTION = SensorEntityDescription(
    key="detection_distance",
    device_class=SensorDeviceClass.DISTANCE,
    entity_registry_enabled_default=False,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Detection Distance",
    native_unit_of_measurement=UnitOfLength.CENTIMETERS,
    state_class=SensorStateClass.MEASUREMENT,
)

MOVING_TARGET_ENERGY_DESCRIPTION = SensorEntityDescription(
    key="moving_target_energy",
    device_class=None,
    entity_registry_enabled_default=False,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Moving Target Energy",
    native_unit_of_measurement="Target Energy",
    state_class=SensorStateClass.MEASUREMENT,
)

STATIC_TARGET_ENERGY_DESCRIPTION = SensorEntityDescription(
    key="static_target_energy",
    device_class=None,
    entity_registry_enabled_default=False,
    entity_registry_visible_default=True,
    has_entity_name=True,
    name="Static Target Energy",
    native_unit_of_measurement="Target Energy",
    state_class=SensorStateClass.MEASUREMENT,
)

SENSOR_DESCRIPTIONS = (
    MOVING_TARGET_DISTANCE_DESCRIPTION,
    STATIC_TARGET_DISTANCE_DESCRIPTION,
    MOVING_TARGET_ENERGY_DESCRIPTION,
    STATIC_TARGET_ENERGY_DESCRIPTION,
    DETECTION_DISTANCE_DESCRIPTION,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for LD2410BLE."""
    data: LD2410BLEData = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LD2410BLESensor(
            data.coordinator,
            data.device,
            entry.title,
            description,
        )
        for description in SENSOR_DESCRIPTIONS
    )


class LD2410BLESensor(CoordinatorEntity[LD2410BLECoordinator], SensorEntity):
    """Moving/static target distance sensor for LD2410BLE."""

    def __init__(
        self,
        coordinator: LD2410BLECoordinator,
        device: LD2410BLE,
        name: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._device = device
        self._key = description.key
        self.entity_description = description
        self._attr_unique_id = f"{device.address}_{self._key}"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(dr.CONNECTION_BLUETOOTH, device.address)},
        )
        self._attr_native_value = getattr(self._device, self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = getattr(self._device, self._key)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Unavailable if coordinator isn't connected."""
        return self._coordinator.connected and super().available
