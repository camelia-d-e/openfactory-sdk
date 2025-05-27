""" OpenFactory-SDK Command Line Interface. """
import click
import openfactory_sdk as sdk


@click.group()
def cli():
    """ OpenFactory SDK CLI - Develop and test OpenFactory apps locally. """
    pass


@cli.group()
def device():
    """ Manage MTConnect devices. """
    pass


# Register commands
device.add_command(sdk.device.click_up)
device.add_command(sdk.device.click_down)
