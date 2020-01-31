# LIFX Day and Dusk in a Docker Container

[![develop branch](https://img.shields.io/travis/djelibeybi/docker-lifx-daydusk/develop?label=develop&logo=travis&style=for-the-badge)](https://travis-ci.org/Djelibeybi/docker-lifx-daydusk) [![master branch](https://img.shields.io/travis/djelibeybi/docker-lifx-daydusk/master?label=master&logo=travis&style=for-the-badge)](https://travis-ci.org/Djelibeybi/docker-lifx-daydusk) [![GitHub issues](https://img.shields.io/github/issues/djelibeybi/docker-lifx-daydusk?logo=github&style=for-the-badge)](https://github.com/Djelibeybi/docker-lifx-daydusk/issues) [![Docker Pulls](https://img.shields.io/docker/pulls/djelibeybi/lifx-daydusk?logo=docker&style=for-the-badge)](https://hub.docker.com/r/djelibeybi/lifx-daydusk)



This container reproduces the LIFX Day and Dusk scheduling functionality locally but removes the dependency on the LIFX Cloud and adds fine-grained control over bulb selection, timing, kelvin value and power status. 

## Supported Platforms

This image is supported on the following platforms:
 * `amd64`: 64-bit Intel or AMD processors including Intel-based Synology NAS devices. 
 * `aarch64`: 64-bit Arm processors including Raspberry Pi 3 Model B/B+ and Raspberry Pi 4.

Docker will automatically download the correct image based on the archiecture upon which it is running.

## Usage

LIFX discovery requires UDP broadcast access to your local network in order to successfully discover bulbs. This can be achieved using the ```--net=host``` flag. Currently this image will not work when using [Docker for Mac](https://github.com/docker/for-mac/issues/68) or [Docker for Windows](https://github.com/docker/for-win/issues/543).


```
docker run \
  --detach \
  --name=daydusk \
  --net=host \
  -e PUID=<UID> \
  -e PGID=<GID> \
  -e TZ=<Time Zone> \
  -v /path/to/config/:/config/ \
  djelibeybi/lifx-daydusk
```

### Parameters

The following parameters can be specified on the command-line when executing `docker run` to start the container:

* `--net=host`: Shares host networking with container (**required**)
* `-e TZ`: for [timezone information](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) e.g. `-e TZ=Europe/London` (**required**)
* `-v /path/to/config/:/config/` - **Required:** see below for details.
* `-e PGID`: for GroupID - see below for explanation
* `-e PUID`: for UserID - see below for explanation

You **must** set a valid `TZ` value otherwise the container will be set to UTC and your events will fire at the wrong time.

## Config Files

### `daydusk.yml`

The sample command above maps the local `/path/to/config` directory to the `/config` directory inside the container. You should change `/path/to/config` to an actual directory on your host system and you must create at least the `daydusk.yml` file in this directory. You **must** provide `/config/daydusk.yml` file. 

A [`sample-daydusk.yml`](https://github.com/Djelibeybi/docker-lifx-daydusk/blob/develop/sample-daydusk.yml) is provided which matches the default LIFX Day & Dusk configuration. 

#### Syntax

The `daydusk.json` file consists of one or more named events that define the time to start the transition, the end state of the bulbs, the duration of the transition and whether the bulbs should turn on automatically before the transition starts or turn off automatically after the transition ends.

In the example below, an event named `wakeup` will fire at **6:30am** on Saturday and Sunday to trigger a **30 minute** transition to power on the bulbs and transition to **80% brightness** at **4000 kelvin**:

```yaml
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
```

The following table documents each parameter and all parameters are required for each event:

| Parameter    | Required? | Value            | Detail |
| ------------ | :-------- | :--------------- | :----- |
| `days`       | No        | List of either `MONDAY` to `SUNDAY` or `0` to `6` | An list of days on which this event should occur. If not specified, the event will occur daily.<br>If specified numerically, `0` is Sunday and `6` is Saturday. |
| `hour`       | **Yes**   | `0` to `23`     | The hour at which the transition starts |
| `minute`     | **Yes**   |`0` to `59`      | The minute after the hour at which the transition starts |
| `hue`        | No        |`0` to `360`     | The target hue in degrees at the end of the transition.<br>**Must be set to `0` for temperature adjustment** |
| `saturation` | No        |`0` to `1`       | The target saturation as a float, e.g. for 80% specify `0.8`.<br>**Must be set to `0` for temperature adjustment** |
| `brightness` | **Yes**   |`1` to `1`       | The target brightness as a float, e.g. for 80% specify `0.8` |
| `kelvin`     | **Yes**   |`1500` to `9000` | The target kelvin value at the end of the transition.<br>**Ignored unless both `hue` and `saturation` are set to `0`** |
| `duration`   | **Yes**   |`1` to `86400`   | How long the transition should run in seconds.<br>Sixty minutes is `3600` seconds. |
| `power`      | No        | <code>[on&#124;off]</code> | Used to turn the bulbs `on` at the start of the event or `off` when the event ends. If not provided the power state remains unchanged. |
| `reference`  | No        | See below       | Used to specify the bulbs to target for the event | 

The [`sample-daydusk.yml`](https://github.com/Djelibeybi/docker-lifx-daydusk/blob/develop/sample-daydusk.yml) file contains four events that replicate the default LIFX Day & Dusk times, brightness and kelvin values as well as the transition duration and power state changes. 

#### Specifying bulbs for each event

The `reference` field is used to determine which bulbs will be targeted for each event. If an event does not contain a reference field, all discovered bulbs will be used. The reference field can be specified in any of the following formats on a per-event basis, i.e. you can chose to use one method for an event and a different method for another.

> **Currently, no validation is performed to ensure the serial numbers are valid or if any specified files exist.** <br>
> Likewise, no validation of the provided filters is performed, so it's possible for a filter to return no results or unexpected results if misconfigured.

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

**A filter than is dynamically evaluated on each run based on bulb-specific data:**
```yaml
reference: match:group_name=bedroom
```

The Photons Core documentation maintains a list [valid filters](https://delfick.github.io/photons-core/modules/photons_device_finder.html#finder-filters) that can be used with this option. Multiple filters can be combined using an ampersand, e.g. `match:group_name=bedroom&power=on` would match all bulbs in the group named `bedroom` that are currently powered on.

## User / Group Identifiers

Sometimes when using data volumes (`-v` flags) permissions issues can arise between the host OS and the container. We avoid this issue by allowing you to specify the user `PUID` and group `PGID`. Ensure the data volume directory on the host is owned by the same user you specify and it will "just work".

In this instance `PUID=1001` and `PGID=1001`. To find yours use `id user` as below:

```
  $ id <dockeruser>
    uid=1001(dockeruser) gid=1001(dockergroup) groups=1001(dockergroup)
```

## Contributing

This project adheres to the [Contributor Covenant code of conduct](.github/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code and to follow the [contribution guidelines](.github/CONTRIBUTING.md).

## Acknowledgements

* [oznu](https://github.com/oznu) for [`docker-homebridge`](https://github.com/oznu/docker-homebridge) upon which the multi-arch support for this repo and image is ~~slightly~~ mostly derived.
* [delfick](https://github.com/delfick) for [`photons-core`](https://github.com/delfick/photons-core) upon which my code depends and for providing additional pointers on using Photons for configuration validation.
