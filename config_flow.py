import voluptuous as vol  # noqa: D100

from homeassistant import config_entries

DOMAIN = "edulink"


class EduLinkFlow(config_entries.ConfigFlow, domain=DOMAIN):  # noqa: D101
    VERSION = 1

    async def async_step_user(self, user_input=None):  # noqa: D102
        data_schema = vol.Schema(
            {
                vol.Required(
                    "username", description={"suggested_value": "Username"}
                ): str,
                vol.Required(
                    "password", description={"suggested_value": "Password"}
                ): str,
                vol.Required(
                    "name", description={"suggested_value": "Pupil Name"}
                ): str,
                vol.Required(
                    "school_id", description={"suggested_value": "Enter the school ID"}
                ): str,
            }
        )
        if user_input is not None:
            return self.async_create_entry(title="EduLink One", data=user_input)

        return self.async_show_form(step_id="user", data_schema=data_schema)
