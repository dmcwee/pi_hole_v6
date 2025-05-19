# PI-HOLE v6 Home Assistant Custom Component

This is a copy of the `pi-hole` component for Home Assistant converted to a custom component and updated to resolve issues with the Pi-Hole v6 api changes. Minor tweaks have been made to address slight differences between the v5 and v6 objects.

## CREDIT

The code in the respository is a copy of the code found in the Home Assistant [`pi_hole`](https://github.com/home-assistant/core/tree/dev/homeassistant/components/pi_hole) component and the `v6.py` file from [`python-hole`](https://github.com/home-assistant-ecosystem/python-hole).

## Installation

1. In the Home Assistant `config` folder create the `custom_components` folder
1. Clone this repository in the `custom_components` folder
1. Restart Home Assistant
1. In Home Assistant => Add Integration search for `pi` and select the **Pi-hole v6** integration.
  1. Provide the **Host**, **Port**, **Name**, **Location**, **Api Key** and **Submit**
  1. *(Optional)* Provide the location information for the device and **Submit**
1. A **Pi-hole v6** integration should appear and begin to populate with data from the Pi-hole

## Issues
- [X] Fix the Status value reporting a Unknown
- [X] Fix the Switch action - Fixed by status update