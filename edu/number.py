# number.py
from homeassistant.const import DEVICE_CLASS_MEASUREMENT
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the EduLink number entities."""
    entities = []

    # Create a number entity for merit count
    entities.append(
        EduLinkNumber(
            hass,
            f"{config_entry.data.get('name')}_merit_count",
            "Merit Count",
            DEVICE_CLASS_MEASUREMENT,
            config_entry,
        )
    )

    # Create number entities for each lesson breakdown
    lesson_breakdown = await get_lesson_breakdown(hass, config_entry.data.get("name"))
    for lesson, count in lesson_breakdown.items():
        entities.append(
            EduLinkNumber(
                hass,
                f"{config_entry.data.get('name')}_{lesson}_merits",
                f"{lesson} Merits",
                DEVICE_CLASS_MEASUREMENT,
                config_entry,
                count,
            )
        )

    async_add_entities(entities)


class EduLinkNumber(Entity):
    """Representation of an EduLink Number entity."""

    def __init__(self, hass, unique_id, name, device_class, config_entry, state=0):
        """Initialize the EduLink Number entity."""
        self._hass = hass
        self._unique_id = unique_id
        self._name = name
        self._device_class = device_class
        self._config_entry = config_entry
        self._state = state

    @property
    def unique_id(self):
        """Return the unique ID of the entity."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def device_class(self):
        """Return the device class of the entity."""
        return self._device_class

    async def async_update(self):
        """Update the state of the entity."""
        # Fetch the latest data from EduLink API and update the state accordingly
        # You might want to implement the logic to update the state here
        lesson_breakdown = await get_lesson_breakdown(
            self._hass, self._config_entry.data.get("name")
        )
        self._state = lesson_breakdown.get(self._name, 0)


async def get_lesson_breakdown(hass, name):
    # Implement your logic to retrieve the lesson breakdown data
    # This is just a placeholder function, replace it with your actual implementation
    return {"Lesson1": 5, "Lesson2": 8, "Lesson3": 3}
