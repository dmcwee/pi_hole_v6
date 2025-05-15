"""Constants for the pi_hole integration."""

from datetime import timedelta

DOMAIN = "pi_hole_v6"

CONF_STATISTICS_ONLY = "statistics_only"

DEFAULT_LOCATION = "admin"
DEFAULT_METHOD = "GET"
DEFAULT_NAME = "Pi-Hole"
DEFAULT_SSL = False
DEFAULT_VERIFY_SSL = True
DEFAULT_STATISTICS_ONLY = True
DEFAULT_API_KEY = ""

SERVICE_DISABLE = "disable"
SERVICE_DISABLE_ATTR_DURATION = "duration"

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=5)
