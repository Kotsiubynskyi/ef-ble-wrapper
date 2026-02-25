It's a simple wrapper around [rabits/ha-ef-ble](https://github.com/rabits/ha-ef-ble.git) project to use apart from HomeAssistant OS

### Clone current repo recursively:
```bash
git clone --recursive https://github.com/Kotsiubynskyi/ef-ble-wrapper.git
```

### Setup (requires Python 3.13+):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ./ha_ef_ble
```

## Run

To fetch data - run with 2 args only
```bash
python3 ef_control.py -u <ecoflow_user_id> -m <ecoflow_ble_mac>
```

To control device add 3rd arg - control command:
```bash
python3 ef_control.py -u <ecoflow_user_id> -m <ecoflow_ble_mac> -c enable_ac_ports=True
```

