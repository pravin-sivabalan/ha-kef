"""Constants for KEF Speakers integration."""

DOMAIN = "kef"

# Configuration keys
CONF_HOST = "host"

# Default values
DEFAULT_NAME = "KEF Speaker"
DEFAULT_PORT = 50001

# Update intervals
UPDATE_INTERVAL = 30  # seconds

# Supported KEF speaker models
SUPPORTED_MODELS = [
    "LS50 Wireless II",
    "LSX II", 
    "LS60"
]

# KEF speaker sources mapping
KEF_SOURCES = {
    "wifi": "WiFi",
    "bluetooth": "Bluetooth", 
    "aux": "Aux",
    "optical": "Optical",
    "coaxial": "Coaxial",
    "usb": "USB"
}