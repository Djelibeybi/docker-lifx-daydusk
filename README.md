<!-- markdownlint-disable MD033 -->
# LIFX Day and Dusk in a Docker Container

[![GitHub issues](https://img.shields.io/github/issues/djelibeybi/docker-lifx-daydusk?logo=github&style=for-the-badge)](https://github.com/Djelibeybi/docker-lifx-daydusk/issues)
[![Docker Pulls](https://img.shields.io/docker/pulls/djelibeybi/lifx-daydusk?logo=docker&style=for-the-badge)](https://hub.docker.com/r/djelibeybi/lifx-daydusk)

This container reproduces the LIFX Day and Dusk scheduling functionality locally
but removes the dependency on the LIFX Cloud and adds fine-grained control over
bulb selection, timing, kelvin value and power status.

## Supported Platforms

This image is supported on the following platforms:

* `amd64`: 64-bit Intel or AMD processors including Intel-based Synology NAS
 devices.
* `aarch64`: 64-bit Arm processors including Raspberry Pi 3 Model B/B+ and
 Raspberry Pi 4.

Docker will automatically download the correct image based on the archiecture
upon which it is running.

## Usage

LIFX discovery requires UDP broadcast access to your local network in order to
successfully discover bulbs. This can be achieved using the ```--net=host```
flag. Currently this image will __not work__ if you are using
[Docker for Mac](https://github.com/docker/for-mac/issues/68) or
[Docker for Windows](https://github.com/docker/for-win/issues/543).

The following command will start the container with the required configuration:

```bash
docker run \
  --detach \
  --name=daydusk \
  --net=host \
  -e TZ=<Time Zone> \
  -v /path/to/config/:/config/ \
  djelibeybi/lifx-daydusk
```

### Parameters

The following parameters can be specified on the command-line when executing
 `docker run` to start the container:

* `--net=host`: Shares host networking with container. (**required**).
* `-e TZ`: for [timezone information](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) e.g. `-e TZ=Europe/London` (**required**)
* `-v /path/to/config/:/config/` - **Required:** see below for details.

> **IMPORTANT:** You **must** set a valid `TZ` value otherwise the container
timezone will be set to UTC and your events may fire at the wrong time.

The `--net=host` option can be replaced by advanced users with an appropriate
`macvlan` network configuration however the configuration of the network itself
and modification of the `docker run` command to use that network is left as an
exercise for the reader.

## Creating the `daydusk.yml` configuration file

The sample `docker run` command above maps the local `/path/to/config` directory
to the `/config` directory inside the container. You should change `/path/to/config`
to an actual directory on your host system and you must create at least the
`daydusk.yml` file in this directory.

> **NOTE:** the [`sample-daydusk.yml`](https://github.com/Djelibeybi/docker-lifx-daydusk/blob/develop/sample-daydusk.yml)
matches the default LIFX Day & Dusk configuration **exactly** including powering
on the specified bulbs at the start of each event.

### Syntax

The `daydusk.yml` file consists of one or more named events that define the time
 to start the transition, the end state of the bulbs, the duration of the
 transition and whether the bulbs should turn on automatically before the
 transition starts or turn off automatically after the transition ends.

In the example below, the event named `wakeup` will fire at **6:30am** on
Saturday and Sunday to trigger the bulbs to power on _in whatever state they
were in when they were previously powered off_ and then begin a **30 minute**
transition to **80% brightness** at **4000 kelvin**:

```yaml
daydusk:
  schedules:
    wakeup:
      days:
        - SATURDAY
        - SUNDAY
      hour: 6
      minute: 30
      brightness: 0.8
      kelvin: 4000
      duration: 1800
      power: ON
      transform_options:
        transition_color: True
```

Multiple events can be included within the file, using the following syntax:

```yaml
daydusk:
  schedules:
     wakeup:
     ...

     day:
     ...

     evening:
     ...

     nighttime:
     ...
```

Note the opening `daydusk:` and `schedules:` only appear once at the beginning
of the file. You can validate your YAML syntax online at
[http://www.yamllint.com/](http://www.yamllint.com/).

There is no limit to the number of events, though each event will add additional
time to process when the container starts. To change the events, use `docker stop`
to shut down the running container, modify the `daydusk.yml` file and then run
`docker start` to start the container back up again.

> **Note:** The container will rebuild the schedule from `daydusk.yml` every
time it starts.

The following table documents each parameter and all parameters are required
for each event:

| Parameter    | Required? | Value            | Detail |
| ------------ | :-------- | :--------------- | :----- |
| `days`       | No        | List of either `MONDAY` to `SUNDAY` or `0` to `6` | An list of days on which this event should occur. If not specified, the event will occur daily.<br>If specified numerically, `0` is Sunday and `6` is Saturday. |
| `hour`       | **Yes**   | `0` to `23`     | The hour at which the transition starts |
| `minute`     | **Yes**   |`0` to `59`      | The minute after the hour at which the transition starts |
| `task`       | No        | `theme`         | If you want to apply a theme to the selected bulbs, set this to `theme`. |
| `hue`        | No        |`0` to `360`     | The target hue in degrees at the end of the transition.<br>**Must be set to `0` for temperature adjustment** |
| `saturation` | No        |`0` to `1`       | The target saturation as a float, e.g. for 80% specify `0.8`.<br>**Must be set to `0` for temperature adjustment** |
| `brightness` | **Yes**   |`1` to `1`       | The target brightness as a float, e.g. for 80% specify `0.8` |
| `kelvin`     | **Yes**   |`1500` to `9000` | The target kelvin value at the end of the transition.<br>**Ignored unless both `hue` and `saturation` are set to `0`** |
| `colors`     | No        | -               | An optional [list of colors](#specifying-colors-for-a-theme) to use when applying a theme. Only valid if `task` is set to `theme`. |
| `duration`   | **Yes**   |`1` to `86400`   | How long the transition should run in seconds.<br>Sixty minutes is `3600` seconds. |
| `power`      | No        | <code>[on&#124;off]</code> | Used to turn the bulbs `on` at the start of the event or `off` when the event ends. If not provided the power state remains unchanged. |
| `transform_options` | No | -               | An optional [list of options](#adding-options-for-each-event) to apply to each event. |
| `override`   | No        | -               | An optional [list of overrides](#adding-overrides-for-a-theme) to apply when applying a theme. |
| `reference`  | No        | -               | Used to [specify the bulbs](#specifying-bulbs-for-each-event) to target for each event. |

The [`sample-daydusk.yml`](sample-daydusk.yml) file contains four events that
replicate the default LIFX Day & Dusk times, brightness and kelvin values as
well as the transition duration and power state changes.

The [`theme-daydusk.yml`](theme-daydusk.yml) will set a rainbow theme across
all devices.

### Adding options for each event

There are two options that can be used to fine-tune the transformation that
occurs for each event:

* `transition_color`: modifies the behaviour of the bulb if it's powered on by
the event. By default if `power` is set to `on`, the target bulb(s) will be set
to the target HSBK or color value before being powered on and the transition
duration will only affect the brightness. By setting this to `True`, the target
bulb(s) will power on with the existing HSBK values and the transition will
affect all values, i.e. the bulb will transition both color and brightness over
 the duration. This is particularly useful for `wakeup` transitions so that the
 initial power on doesn't jump to a much higher kelvin value immediately.
* `keep_brightness`: modifies the transition to ignore any brightness value,
i.e. only the HSK/color values are transitions over the duration while the
brightness remains the same.

Example usage:

```yaml
transform_options:
  transition_color: True
  keep_brightness: False
```

### Specifying colors for a theme

The `colors` parameter is optional. If omitted, the default theme uses seven
colors at 30% brightness.

To specify your own colors, use any combination of the following formats:

* Names: `white`, `red`, `orange`, `yellow`, `cyan`, `green`, `blue`
`purple`, `pink`
* Hexadecimal: `hex:#RRGGBB`
* Red, green, blue: `rgb:0-255,0-255,0-255`
* Hue, saturation and brightness: `hsb:0-359, 0-1, 0-1`

Here is an example list of colors that uses each of these formats:

```yaml
colors:
  - red
  - hex:#00ff00
  - rgb:0, 0, 255
  - hsb:120, 1, 0.7
```

Only the `hsb` option specifies brightness for each color. You can override
the brightness globally using the `override` option.

### Adding overrides for a theme

By default, Photons will use the current brightness of the target device(s) when
applying a theme with specified colors that don't include a specific brightness
value. This can be overridden by providing a brightness for all devices when
applying the theme.

To specify a global brightness, add it as an override to your event. The
following example sets the brightness to 70%:

```yaml
override:
  - brightness: 0.7
```

### Specifying bulbs for each event

The `reference` field is used to determine which bulbs will be targeted for each
 event. If an event does not contain a reference field, all discovered bulbs
 will be used. The reference field can be specified in any of the following
 formats on a per-event basis, i.e. you can chose to use one method for an event
  and a different method for another.

> **Currently, no validation is performed to ensure the serial numbers are valid
 or if any specified files exist.** <br>
> Likewise, no validation of the provided filters is performed, so it's possible
for a filter to return no results or unexpected results if misconfigured.

The available formats are:

**A single serial number:**

```yaml
reference: d073d5000001
```

**A list of serial numbers:**

```yaml
reference:
  - d073d5000001
  - d073d5000002
```

**A file that contains a list of serial numbers (one per line):**

```yaml
reference: file:/config/bulbs.conf
```

**A filter that is dynamically evaluated on each run based on bulb-specific data:**

```yaml
reference: match:group_name=bedroom
```

The Photons Core documentation maintains a list [valid filters](https://delfick.github.io/photons-core/modules/photons_device_finder.html#finder-filters) that can be used with this option. Multiple filters can be
combined using an ampersand, e.g. `match:group_name=bedroom&power=on` would match
 all bulbs in the group named `bedroom` that are currently powered on.

### Additional Photons configuration

To provide [additional configuration options](https://photons.delfick.com/configuration/index.html)
to Photons, simply add `lifx.yml` file to the `/config` directory.

## Acknowledgements

* [delfick](https://github.com/delfick) for [Photons](https://photons.delfick.com)
upon which my code depends and for providing additional pointers on using
Photons for configuration validation.
