import asyncio
from datetime import timedelta
import json
from typing import Any
import uuid
import aiohttp

import requests
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

DOMAIN = "edulink"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigType) -> bool:
    uuid_str = str(uuid.uuid4())

    async with aiohttp.ClientSession() as session:
        # Perform the first HTTP request
        async with session.post(
            url="https://provisioning.edulinkone.com/?method=School.FromCode",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "School.FromCode",
                    "params": {"code": entry.data.get("school_id")},
                    "uuid": uuid_str,
                    "id": "1",
                }
            ),
            headers={"content-type": "application/json"},
        ) as response:
            data = await response.json()

            sch_id = data["result"]["school"]["school_id"]

        # Perform the second HTTP request
        async with session.post(
            url="https://www7.edulinkone.com/api/?method=EduLink.Login",
            json={
                "jsonrpc": "2.0",
                "method": "EduLink.Login",
                "params": {
                    "from_app": False,
                    "device": {},
                    "username": entry.data.get("username"),
                    "password": entry.data.get("password"),
                    "establishment_id": sch_id,
                },
                "uuid": uuid_str,
                "id": "1",
            },
            headers={
                "content-type": "application/json",
                "X-API-Method": "EduLink.Login",
            },
        ) as response:
            data = await response.json()
            learner_id = data["result"]["user"]["id"]
            auth_token = data["result"]["authtoken"]

        # Perform the third HTTP request
        async with session.post(
            url="https://www7.edulinkone.com/api/?method=EduLink.Achievement",
            json={
                "jsonrpc": "2.0",
                "method": "EduLink.Achievement",
                "params": {"learner_id": learner_id},
                "uuid": uuid_str,
                "id": "1",
            },
            headers={
                "content-type": "application/json",
                "X-API-Method": "EduLink.Achievement",
                "authorization": f"Bearer {auth_token}",
            },
        ) as response:
            data = await response.json()
            merits_dump = data["result"]["achievement"]

    merit_count = 0
    lesson_breakdown = {}
    lessons = []

    for i in merits_dump:
        merit_count += 1
        if "lesson_information" in i:
            lessons.append(i["lesson_information"].partition(" -")[0])

    for i in lessons:
        if i not in lesson_breakdown:
            lesson_breakdown.update({i: 0})

    for i in lessons:
        lesson_breakdown[i] += 1

    # Set states in Home Assistant
    hass.states.async_set(f"number.{entry.data.get('name')}_merit_count", merit_count)

    for i in lesson_breakdown.keys():
        hass.states.async_set(
            f"number.{entry.data.get('name')}_{i.replace(' ', '_').replace('&','_').replace('-','').replace('__','')}_merits",
            lesson_breakdown.get(i),
        )
    return True


async def async_setup(hass: HomeAssistant, entry: ConfigType) -> bool:
    # Return boolean to indicate that initialization was successful.
    return True
