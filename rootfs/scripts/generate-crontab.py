#!/usr/local/bin/python3
"""
A script for generating a crontab that can be used to simulate

It takes in options from photons configuration that looks a bit like:

    ---

    daydusk:

      schedules:
        day:
          hour: 7
          minute: 0
          days:
            - MONDAY
            - WEDNESDAY
          hue: 0
          brightness: 0.9
          kelvin: 3500
          duration: 60
          power: ON

        evening:
          hour: 0
          minute: 0
          brightness: 0.8
          kelvin: 2700
          duration: 600
          power: ON

The options you have available for each schedule is:

hue - integer between 0 and 360 - default 0
saturation - float between 0 and 1 - default 0
brightness - float between 0 and 1 - default 1
kelvin - integer between 1500 and 9000 - default 3500
power - ON/OFF, true/false; or 0/1
duration - A unbounded float of the number of seconds you want this to take

days
    The days you want this run. If not specified it'll run on all days.
    Otherwise this should be a list of the days. Each day can be the name of
    the day (i.e. MONDAY, WEDNESDAY, ...) or a number from 0 to 6 where sunday
    is 0.


hour - required integer between 0 and 23
minute - required integer between 0 and 59

reference
    The lights to target. If this is an empty string or an underscore or not
    specified then it'll default to all devices that can be found.

    Otherwise it should be a special reference string. For example:
    ``match:label=kitchen`` or ``file:/path/to/file/with_mac_per_line``

    Or a list of device mac addresses (i.e. d073d5001337)
"""

from textwrap import dedent
import distutils.sysconfig
import logging
import shlex
import json
import enum
import os

from crontab import CronTab

from photons_app.formatter import MergedOptionStringFormatter
from photons_app.errors import PhotonsAppError
from photons_app.actions import an_action

from photons_protocol.types import enum_spec

from delfick_project.norms import dictobj, sb, BadSpecValue
from delfick_project.addons import addon_hook

log = logging.getLogger("daydusk")


def find_lifx_script():
    bin_dir = distutils.sysconfig.get_config_var("prefix")
    lifx_script = os.path.join(bin_dir, "bin", "lifx")

    if not os.path.exists(lifx_script):
        raise NoLIFXScript()

    return lifx_script

class NoSchedules(PhotonsAppError):
    desc = dedent(
        """
    You need to specify some schedules under the ``daydusk.schedules`` section
    of your configuration

    For example::

        ---

        daydusk:
          schedules:
            day:
              hour: 7
              minute: 0
              days:
                - MONDAY
                - WEDNESDAY

              hue: 0
              saturation: 0
              brightness: 0.9
              kelvin: 3500
              duration: 60
              power: ON
              transform_options:
                - transition_color: True
    """
    ).rstrip()

class NoLIFXScript(PhotonsAppError):
    desc = "I couldn't find the lifx script"

class Days(enum.Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

class range_spec(sb.Spec):
    def setup(self, spec, minimum, maximum):
        self.spec = spec
        self.minimum = minimum
        self.maximum = maximum

    def normalise_filled(self, meta, val):
        val = self.spec.normalise(meta, val)
        if val < self.minimum or val > self.maximum:
            raise BadSpecValue(
                "Value must be between min and max values",
                wanted=val,
                minimum=self.minimum,
                maximum=self.maximum,
                meta=meta,
            )
        return val

class power_spec(sb.Spec):
    def normalise_filled(self, meta, val):
        if val in ("on", "ON", True, 1):
            return "on"
        elif val in ("off", "OFF", False, 0):
            return "off"

        raise BadSpecValue("Power must be on/off, True/False or 0/1", wanted=val, meta=meta)

class reference_spec(sb.Spec):
    def normalise_empty(self, meta):
        return ""

    def normalise_filled(self, meta, val):
        return ",".join(sb.listof(sb.string_spec()).normalise(meta, val))

class Schedule(dictobj.Spec):
    days = dictobj.NullableField(sb.listof(enum_spec(None, Days, unpacking=True)))
    hour = dictobj.Field(range_spec(sb.integer_spec(), 0, 23), wrapper=sb.required)
    minute = dictobj.Field(range_spec(sb.integer_spec(), 0, 59), wrapper=sb.required)

    hue = dictobj.Field(range_spec(sb.float_spec(), 0, 360), default=0)
    saturation = dictobj.Field(range_spec(sb.float_spec(), 0, 1), default=0)
    brightness = dictobj.Field(range_spec(sb.float_spec(), 0, 1), default=1)
    kelvin = dictobj.Field(range_spec(sb.integer_spec(), 1500, 9000), default=3500)

    duration = dictobj.NullableField(sb.float_spec)
    power = dictobj.NullableField(power_spec)
    transform_options = dictobj.NullableField(sb.dictof(sb.string_spec(), sb.boolean()))

    reference = dictobj.Field(reference_spec)

    @property
    def extra(self):
        keys_except = ["days", "hour", "minute", "reference"]
        options = {k: v for k, v in self.as_dict().items() if k not in keys_except}
        return {k: v for k, v in options.items() if v is not None}

    @property
    def dow(self):
        days = self.days
        if not self.days:
            days = list(Days)

        return [day.value for day in days]

class DayDusk(dictobj.Spec):
    schedules = dictobj.Field(
        sb.dictof(sb.string_spec(), Schedule.FieldSpec(formatter=MergedOptionStringFormatter))
    )

@addon_hook(extras=[("lifx.photons", "control")])
def __lifx__(collector, *args, **kwargs):
    collector.register_converters(
        {"daydusk": DayDusk.FieldSpec(formatter=MergedOptionStringFormatter)}
    )

@an_action()
async def make_crontab(collector, **kwargs):
    """
    Make a crontab file executing our day dusk options.

    Usage is::

        ./generate-crontab.py
    """
    extra_script_args = ["--silent"]
    daydusk = collector.configuration["daydusk"]
    cronfile = '/config/daydusk.crontab'
    if not daydusk.schedules:
        raise NoSchedules()

    cron = CronTab()
    lifx_script = find_lifx_script()

    for name, options in daydusk.schedules.items():
        command = [
            lifx_script,
            "lan:transform",
            options.reference,
            *extra_script_args,
            "--",
            json.dumps(options.extra),
        ]

        command = str(" ".join([shlex.quote(part) for part in command])) + " >/dev/null"

        job = cron.new(command=command)
        job.dow.on(*options.dow)
        job.minute.on(options.minute)
        job.hour.on(options.hour)

    if os.path.exists(cronfile):
        os.remove(cronfile)

    cron.write(cronfile)
    print(f"Created crontab at {cronfile}")

if __name__ == "__main__":
    from photons_app.executor import main
    import sys

    main(["make_crontab"])
