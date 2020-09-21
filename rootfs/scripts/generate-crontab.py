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

from photons_control.colour import make_hsbk

from delfick_project.norms import dictobj, sb, Meta, BadSpecValue
from delfick_project.addons import addon_hook

log = logging.getLogger("daydusk")

default_colors = [
    (0, 1, 0.3, 3500),
    (40, 1, 0.3, 3500),
    (60, 1, 0.3, 3500),
    (127, 1, 0.3, 3500),
    (239, 1, 0.3, 3500),
    (271, 1, 0.3, 3500),
    (294, 1, 0.3, 3500),
]

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

class task_spec(sb.Spec):
    def normalise_empty(self, meta):
        return "lan:transform"

    def normalise_filled(self, meta, val):
        if val in ("theme"):
            return "lan:apply_theme"
        else:
            return "lan:transform"

class colors_spec(sb.Spec):
    def normalise_empty(self, meta):
        return default_colors

    def normalise_filled(self, meta, val):
        cs = [make_hsbk(val) for val in val]
        return [(c["hue"], c["saturation"], c["brightness"], c["kelvin"]) for c in cs]

class reference_spec(sb.Spec):
    def normalise_empty(self, meta):
        return ""

    def normalise_filled(self, meta, val):
        return ",".join(sb.listof(sb.string_spec()).normalise(meta, val))

class Schedule(dictobj.Spec):
    days = dictobj.NullableField(sb.listof(enum_spec(None, Days, unpacking=True)))
    hour = dictobj.Field(range_spec(sb.integer_spec(), 0, 23), wrapper=sb.required)
    minute = dictobj.Field(range_spec(sb.integer_spec(), 0, 59), wrapper=sb.required)

    task = dictobj.Field(task_spec)

    hue = dictobj.Field(range_spec(sb.float_spec(), 0, 360), default=0)
    saturation = dictobj.Field(range_spec(sb.float_spec(), 0, 1), default=0)
    brightness = dictobj.Field(range_spec(sb.float_spec(), 0, 1), default=1)
    kelvin = dictobj.Field(range_spec(sb.integer_spec(), 1500, 9000), default=3500)
    transform_options = dictobj.NullableField(sb.dictof(sb.string_spec(), sb.boolean()))

    duration = dictobj.NullableField(sb.float_spec)
    power = dictobj.NullableField(power_spec)

    colors = dictobj.NullableField(colors_spec)
    override = dictobj.NullableField(sb.dictof(sb.string_spec(), range_spec(sb.float_spec(), 0, 1)))

    reference = dictobj.Field(reference_spec)

    @property
    def hsbk(self):
        if self.task == 'lan:transform':
            keys = ["hue", "saturation", "brightness", "kelvin"]
            options = {k: v for k, v in self.as_dict().items() if k in keys}
            return {k: v for k, v in options.items() if v is not None}
        else:
            return {}

    @property
    def extra(self):
        keys_except = ["days", "hour", "minute", "reference", "task", "hue", "saturation", "brightness", "kelvin"]
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

@an_action(needs_target=False, special_reference=False)
async def make_crontab(collector, target, reference, artifact, **kwargs):
    """
    Make a crontab file executing our day dusk options.

    Usage is::

        ./generate-crontab.py
    """
    collector.register_converters(
        {"daydusk": DayDusk.FieldSpec(formatter=MergedOptionStringFormatter)}
    )
    daydusk = collector.configuration["daydusk"]

    spec = sb.set_options(
        path=sb.defaulted(sb.string_spec(), '/config/daydusk.crontab'),
        lifx_script=sb.defaulted(sb.string_spec(), '/usr/local/bin/lifx')
    )
    extra = collector.configuration["photons_app"].extra_as_json
    kwargs = {
        k: v for k, v in spec.normalise(Meta.empty(), extra).items() if v is not sb.NotSpecified
    }

    cronfile = kwargs['path']
    lifx_script = kwargs['lifx_script']

    if not daydusk.schedules:
        raise NoSchedules()

    cron = CronTab()

    extra_script_args = ["--silent"]

    for name, options in daydusk.schedules.items():
        script_args = {**options.hsbk, **options.extra}
        command = [
            lifx_script,
            options.task,
            options.reference,
            *extra_script_args,
            "--",
            json.dumps(script_args),
        ]

        command = str(" ".join([shlex.quote(part) for part in command]))

        job = cron.new(command=command)
        job.dow.on(*options.dow)
        job.minute.on(options.minute)
        job.hour.on(options.hour)

    if os.path.exists(cronfile):
        os.remove(cronfile)

    cron.write(cronfile)
    print(f"Generated crontab at {cronfile}")

if __name__ == "__main__":
    __import__("photons_core").run('lan:make_crontab --silent {@:1:}')
