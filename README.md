It's a simple wrapper around [rabits/ha-ef-ble](https://github.com/rabits/ha-ef-ble.git) project to use apart from HomeAssistant OS\
It allows reading EcoFlow power station data as well as control some toggles.

### Clone current repo recursively:
```bash
git clone --recursive https://github.com/Kotsiubynskyi/ef-ble-wrapper.git
```

> [!IMPORTANT]
> parent project requires Python 3.13+

### Setup:
```bash
cd ef-ble-wrapper
python3 -m venv .venv
source .venv/bin/activate
pip install ./ha_ef_ble
```

## Run

To fetch data — run script with 2 args only
```bash
python3 ef_control.py -u <ecoflow_user_id> -m <ecoflow_ble_mac>
```

To control device add 3rd arg — control command:
```bash
python3 ef_control.py -u <ecoflow_user_id> -m <ecoflow_ble_mac> -c enable_ac_ports=True
```

`<ecoflow_user_id>` can be extracted from your EcoFlow user account using this tool: https://gnox.github.io/user_id. Example — **1594212476301521327**\
*Note: your power station has to be added/registered in EcoFlow app first*

`<ecoflow_ble_mac>` - MAC address of your powerstation can be found by scanning your nearby devices from laptop or phone. Example — **60:55:F9:64:30:BC**

## Example
```bash
python3 ef_control.py -u 1594212476301521327 -m 60:55:F9:64:30:BC -c enable_ac_ports=True
```

