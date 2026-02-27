import argparse
import asyncio
import logging
import os
import signal
import sys

base_path = os.path.abspath("./ha_ef_ble/custom_components/ef_ble")

if base_path not in sys.path:
    sys.path.insert(0, base_path)

import eflib
from bleak import BleakScanner
from eflib import DeviceBase, NewDevice
from eflib.props.raw_data_props import RawDataProps

_LOGGER = logging.getLogger()
stop_event = asyncio.Event()


def handle_exit():
    _LOGGER.info("\nShutdown signal received...")
    stop_event.set()


async def main():
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, handle_exit)

    parser = argparse.ArgumentParser(
        description="EcoFlow Controller",
        epilog="If script called without command args then by default it will stream data from EcoFlow device",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging level"
    )

    parser.add_argument(
        "-u",
        "--user-id",
        required=True,
        help="EcoFlow account user ID retrieved from EcoFlow cabinet",
    )
    parser.add_argument(
        "-m",
        "--ble_mac",
        required=True,
        help="Your EcoFlow device BLE MAC address (can be found with Bluetooth scanner)",
    )

    parser.add_argument(
        "-c",
        "--command",
        required=False,
        help='Command to control your EcoFlow device, e.g. "enable_ac_ports=True" or "enable_dc_12v_port=False"',
    )

    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO

    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _LOGGER = logging.getLogger(__name__)
    _LOGGER.debug(
        "System started with logging level: %s", logging.getLevelName(log_level)
    )

    ecoflowWrapper = Ecoflow(args.user_id, args.ble_mac)
    await ecoflowWrapper.find_ecoflow()
    if ecoflowWrapper.ef_device:
        if command := args.command:
            method_name, value_str = command.split("=")
            value = value_str.strip().lower() == "true"
            if hasattr(ecoflowWrapper.ef_device, method_name):
                method = getattr(ecoflowWrapper.ef_device, method_name)
                await method(value)
                _LOGGER.info("Done")
            else:
                _LOGGER.error("Error: %s is not a valid command.", method_name)
        else:
            await ecoflowWrapper.stream_device_data()
            while not stop_event.is_set():
                await asyncio.sleep(1)
            await ecoflowWrapper.ef_device.disconnect()


class Ecoflow:
    ef_device: DeviceBase | None
    user_id: str
    ef_mac: str

    def __init__(self, user_id: str, ef_mac: str):
        self.ef_mac = ef_mac
        self.user_id = user_id

    async def stream_device_data(self):
        if not self.ef_device:
            _LOGGER.error(
                "First try to find your EcoFlow device with BLE MAC %s", self.ef_mac
            )
            return

        # in case newer Ecoflow device
        if device := eflib.get_protobuf_device(self.ef_device):
            device.on_message_processed(self.hande_data_parsed)
        # in case older EcoFlow device
        if device := eflib.get_fixed_length_coding_device(self.ef_device):
            device.on_message_processed(self.hande_data_parsed)

    async def find_ecoflow(self) -> DeviceBase | None:
        _LOGGER.debug("Searching for EF with BLE MAC %s", self.ef_mac)

        scanner = BleScanner()
        if ef := await scanner.discover_devices(self.ef_mac):
            await ef.connect(self.user_id, 2, 10)
            await ef.wait_until_authenticated_or_error()
            self.ef_device = ef
            return ef

        return None

    def hande_data_parsed(self, message):
        _LOGGER.info("New Data packet received: %s", str(message))
        if isinstance(self.ef_device, RawDataProps) and hasattr(
            self.ef_device, "_fields"
        ):
            fields = self.ef_device._fields
            for field in fields:
                field_name = field.public_name
                try:
                    field_value = getattr(self.ef_device, field_name)
                    # print(f"{field_name}: {field_value}")
                except AttributeError:
                    pass


class BleScanner:
    async def discover_devices(self, mac: str) -> DeviceBase | None:
        """Continuously scan for BLE devices."""
        foundEcoflowDevice: DeviceBase | None = None
        for _i in range(3):
            _LOGGER.info("Starting BLE scan...")

            try:
                devices = await BleakScanner.discover(return_adv=True)

                _LOGGER.info("Found %d BLE devices", len(devices))

                for addr, (dev, adv_data) in devices.items():
                    ef_dev = NewDevice(dev, adv_data)
                    if not ef_dev:
                        continue

                    if mac == addr:
                        foundEcoflowDevice = ef_dev
                        break
            except Exception as ex:
                _LOGGER.error(
                    "Failed attempt to look for Ecoflow with BLE MAC %s: %s", mac, ex
                )

            if foundEcoflowDevice:
                _LOGGER.info(
                    "Found EcoFlow device with BLE MAC %s - %s",
                    mac,
                    foundEcoflowDevice.name,
                )
                return foundEcoflowDevice

        _LOGGER.warning("No EcoFlow device with found with BLE MAC: %s", mac)
        return None


if __name__ == "__main__":
    asyncio.run(main())
