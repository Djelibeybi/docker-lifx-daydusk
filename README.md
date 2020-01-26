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
  -e PUID=<UID> -e PGID=<GID> \
  -e TZ=<Time Zone> |
  -v /path/to/config/:/config/ \
  djelibeybi/lifx-daydusk
```

### Parameters

The parameters are split into two halves, separated by a colon, the left hand side representing the host and the right the container side.

* `--net=host`: Shares host networking with container (**required**)
* `-e TZ`: for [timezone information](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) e.g. `-e TZ=Europe/London` (**required**)
* `-v /path/to/config/:/config/` - **Required:** see below for details.
* `-e PGID`: for GroupID - see below for explanation
* `-e PUID`: for UserID - see below for explanation

You _must_ set a valid `TZ` value otherwise the container will be set to UTC and your events will fire at the wrong time.

## Config Files

### `daydusk.json`

The sample command above maps the local `/path/to/config` directory to the `/config` directory inside the container. You should change `/path/to/config` to an actual directory on your host system and you must create at least the `daydusk.json` file in this directory. You **must** provide `/config/daydusk.json` file. No default is provided.

A [`sample-daydusk.json`](https://github.com/Djelibeybi/docker-lifx-daydusk/blob/master/sample-daydusk.json) is provided which matches the default LIFX Day & Dusk configuration. 

#### Syntax

The `daydusk.json` file consists of one or more named events that define the time to start the transition, the end state of the bulbs, the duration of the transition and whether the bulbs should turn on automatically before the transition starts or turn off automatically after the transition ends.

In the example below, an event named `wakeup` will fire at **6:30am** to trigger a **30 minute** transition to change the bulbs to **80% brightness** at **4000 kelvin**:

```
...
  "wakeup": {
    "hour": "6",
    "minute": "30",
    "brightness": "80",
    "kelvin": "4000",
    "duration": "30",
    "power": "ignore"
  }
...  
```

The following table documents each parameter and all parameters are required for each event:

| Parameter    | Value | Detail
| ------------ | :---- | :----- |
| `hour`       | `0` to `23`  | The _hour_ at which the transition starts
| `minute`     | `0` to `59` | The _minute_ after the _hour_ at which the transition starts
| `brightness` | `1` to `100` | The target brightness in percent at the end of the transition |
| `kelvin`     | `1500` to `9000` | The target kelvin value at the end of the transition |
| `duration`   | `1` to `1440` | How long the transition should run in minutes |
| `power`      | `[ on | off | ignore ]` | Either the bulbs turn `on` before the transition starts or turn `off` when it ends. Use `ignore` to leave the power state as-is. |

The [`sample-daydusk.json`](https://github.com/Djelibeybi/docker-lifx-daydusk/blob/master/sample-daydusk.json) file matches the default LIFX Day & Dusk times, brightness and kelvin values but does not change the power status of the bulbs either before or after the transition.


### `bulbs.conf` and `<event>-bulbs.conf`

If you provide a `/config/bulbs.conf` file with a list of target MAC addresses (one per line), only those bulbs will be targeted by the configured events.

> **If no bulb files are provided then the events will target all discovered bulbs on the network.**

You can also provide an event-specific list of bulbs using the filename syntax of `<event>-bulbs.conf`. If an event-specific list of bulbs exists, only those bulbs will be targeted. For example, to restrict the bulbs that are targeted by the example `wakeup` event above, create a file named `/config/wakeup-bulbs.conf`.


## User / Group Identifiers

Sometimes when using data volumes (`-v` flags) permissions issues can arise between the host OS and the container. We avoid this issue by allowing you to specify the user `PUID` and group `PGID`. Ensure the data volume directory on the host is owned by the same user you specify and it will "just work".

In this instance `PUID=1001` and `PGID=1001`. To find yours use `id user` as below:

```
  $ id <dockeruser>
    uid=1001(dockeruser) gid=1001(dockergroup) groups=1001(dockergroup)
```


## Acknowledgements

* [oznu](https://github.com/oznu) for [`docker-homebridge`](https://github.com/oznu/docker-homebridge) upon which the multi-arch support for this repo and image is ~~slightly~~ mostly derived.
* [delfick](https://github.com/delfick) for [`photons-core`](https://github.com/delfick/photons-core) upon which my code depends.
