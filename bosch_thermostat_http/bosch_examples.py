import click
import logging
import aiohttp
import bosch_thermostat_http as bosch
from bosch_thermostat_http.db import open_json, MAINPATH
from bosch_thermostat_http.const import HC, SENSORS, DHW
import os
import asyncio

from functools import wraps

_LOGGER = logging.getLogger(__name__)

pass_bosch = click.make_pass_decorator(dict, ensure=True)

rc300 = open_json(os.path.join(MAINPATH, "rc300.json"))
default = open_json(os.path.join(MAINPATH, "default.json"))

sensors_dict = next(iter(default.values()))[SENSORS]
sensors_dict.update(
    next(iter(rc300.values()))[SENSORS]
)
sensor_list = ' , '.join(sensors_dict.keys())


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group(invoke_without_command=True)
@click.pass_context
@coro
async def cli(ctx):
    """A tool to create rawscan of Bosch thermostat."""
    pass


@cli.command()
@click.option("--ip", envvar="BOSCH_IP", type=str, required=True, help="IP address of gateway")
@click.option("--token", envvar="BOSCH_ACCESS_TOKEN", type=str, required=True, help="Token from sticker without dashes.")
@click.option("--password", envvar="BOSCH_PASSWORD", type=str, required=False, help="Password you set in mobile app.")
@click.option("-d", "--debug", default=False, count=True)
@click.option('--sensor', '-s', multiple=True, help="You can use multiple sensors. Possible values: %s" % sensor_list)
@click.pass_context
@coro
async def sensors(ctx, ip: str, token: str, password: str, debug: int, sensor):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
        _LOGGER.debug(f"Lib version is {bosch.version.__version__}")
    else:
        logging.basicConfig(level=logging.INFO)
    async with aiohttp.ClientSession() as session:
        gateway = bosch.Gateway(
            session=session, host=ip, access_key=token, password=password
        )
        _LOGGER.debug("Trying to connect to gateway.")
        if await gateway.check_connection():
            _LOGGER.info("Successfully connected to gateway. Found UUID: %s", gateway.uuid)
            sensors = gateway.initialize_sensors(list(sensor))
            for sensor_obj in sensors:
                await sensor_obj.update()
                print(sensor_obj.name, ":", sensor_obj.get_all_properties())
        else:
            _LOGGER.error("Couldn't connect to gateway!")
        await session.close()

@cli.command()
@click.option("--ip", envvar="BOSCH_IP", type=str, required=True, help="IP address of gateway")
@click.option("--token", envvar="BOSCH_ACCESS_TOKEN", type=str, required=True, help="Token from sticker without dashes.")
@click.option("--password", envvar="BOSCH_PASSWORD", type=str, required=False, help="Password you set in mobile app.")
@click.option("-d", "--debug", default=False, count=True)
@click.option("-t", "--target_temp", default=False, count=True, help="Get target temperature")
@click.option("-m", "--op_mode", default=False, count=True, help="Print current mode")
@click.option("--op_modes", default=False, count=True, help="Print available operation modes")
@click.option("--setpoints", default=False, count=True, help="Print setpoints from schedule")
@click.pass_context
@coro
async def hc(ctx, ip: str, token: str, password: str, debug: int, target_temp: int, op_mode: int, op_modes: int, setpoints: int):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
        _LOGGER.debug(f"Lib version is {bosch.version.__version__}")
    else:
        logging.basicConfig(level=logging.INFO)
    async with aiohttp.ClientSession() as session:
        gateway = bosch.Gateway(
            session=session, host=ip, access_key=token, password=password
        )
        _LOGGER.debug("Trying to connect to gateway.")
        if await gateway.check_connection():
            _LOGGER.info("Successfully connected to gateway. Found UUID: %s", gateway.uuid)
            await circuit_fetch(gateway, HC, target_temp, op_mode, op_modes, setpoints)
        else:
            _LOGGER.error("Couldn't connect to gateway!")
        await session.close()

@cli.command()
@click.option("--ip", envvar="BOSCH_IP", type=str, required=True, help="IP address of gateway")
@click.option("--token", envvar="BOSCH_ACCESS_TOKEN", type=str, required=True, help="Token from sticker without dashes.")
@click.option("--password", envvar="BOSCH_PASSWORD", type=str, required=False, help="Password you set in mobile app.")
@click.option("-d", "--debug", default=False, count=True)
@click.option("-t", "--target_temp", default=False, count=True, help="Get target temperature")
@click.option("-m", "--op_mode", default=False, count=True, help="Print current mode")
@click.option("--op_modes", default=False, count=True, help="Print available operation modes")
@click.option("--setpoints", default=False, count=True, help="Print setpoints from schedule")
@click.pass_context
@coro
async def dhw(ctx, ip: str, token: str, password: str, debug: int, target_temp: int, op_mode: int, op_modes: int, setpoints: int):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
        _LOGGER.debug(f"Lib version is {bosch.version.__version__}")
    else:
        logging.basicConfig(level=logging.INFO)
    async with aiohttp.ClientSession() as session:
        gateway = bosch.Gateway(
            session=session, host=ip, access_key=token, password=password
        )
        _LOGGER.debug("Trying to connect to gateway.")
        if await gateway.check_connection():
            _LOGGER.info("Successfully connected to gateway. Found UUID: %s", gateway.uuid)
            await circuit_fetch(gateway, DHW, target_temp, op_mode, op_modes, setpoints)
        else:
            _LOGGER.error("Couldn't connect to gateway!")
        await session.close()


async def circuit_fetch(gateway, circuit_type, target_temp, op_mode, op_modes, setpoints):
    await gateway.initialize_circuits(circuit_type)
    circuits = gateway.get_circuits(circuit_type)
    for circuit in circuits:
        _LOGGER.debug("Fetching data from circuit.")
        await circuit.update()
        if target_temp:
            print(f"Target temp of {circuit.name} is: {circuit.target_temperature}")
        if op_mode:
            print(f"Operation mode of {circuit.name} is: {circuit.current_mode}")
        if op_modes:
            print(f"Available operation modes of {circuit.name} are: {circuit.available_operation_modes}")
        if setpoints:
            print(f"Available setpoints of {circuit.name} are: {circuit.schedule.setpoints}")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(cli())
