# LIFX Day and Dusk in a Docker Container

This container reproduces the LIFX Day and Dusk scheduling functionality locally but removes the dependency on the LIFX Cloud and adds fine-grained control over timing, kelvin value and power status. 

## Limitations

The image currently only works on Intel/x86_64 hardware.

## Usage

LIFX discovery requires UDP broadcast access to your local network in order to successfully discover bulbs. This can be achieved using the ```--net=host``` flag. Currently this image will not work when using [Docker for Mac](https://github.com/docker/for-mac/issues/68) or [Docker for Windows](https://github.com/docker/for-win/issues/543).


```
docker run \
  --detach \
  --name=daydusk \
  --net=host \
  -e PUID=<UID> -e PGID=<GID> \
  -e TZ=<Time Zone> |
  -v /path/to/daydusk.json:/config/daydusk.json \
  djelibeybi/lifx-daydusk
```

### Parameters

The parameters are split into two halves, separated by a colon, the left hand side representing the host and the right the container side.

* `--net=host`: Shares host networking with container (**required**)
* `-e TZ`: for [timezone information](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) e.g. `-e TZ=Europe/London`
* `-e PGID`: for GroupID - see below for explanation
* `-e PUID`: for UserID - see below for explanation
* `-v /path/to/daydusk.json:/config/daydusk.json` - **Required:** see below for details.

#### *Optional Settings:*

* `-v /path/to/bulbs.conf:/config/bulbs.conf` - if you provide a `/config/bulbs.conf` file, then only the specified bulbs will be controlled. Otherwise, all discovered bulbs will be controlled. The `/config/bulbs.conf` file should list the MAC addresses of the target bulbs, one per line.


### User / Group Identifiers

Sometimes when using data volumes (`-v` flags) permissions issues can arise between the host OS and the container. We avoid this issue by allowing you to specify the user `PUID` and group `PGID`. Ensure the data volume directory on the host is owned by the same user you specify and it will "just work".

In this instance `PUID=1001` and `PGID=1001`. To find yours use `id user` as below:

```
  $ id <dockeruser>
    uid=1001(dockeruser) gid=1001(dockergroup) groups=1001(dockergroup)
```

## The daydusk.json file

You **must** provide `/config/daydusk.json` file. No default is provided.

### Syntax

The `daydusk.json` file consists of one or more stanzas that define the time to _start_ the transition, the end state of the bulbs, the duration of the transition and whether the bulbs should turn on automatically before the transition starts or turn off automatically after the transition ends.

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
The following table documents each parameter and all parameters are required for each stanza:

| Parameter    | Value | Detail
| ------------ | :---- | :----- |
| `hour`       | `0` to `23`  | The _hour_ at which the transition starts
| `minute`     | `0` to `59` | The _minute_ after the _hour_ at which the transition starts
| `brightness` | `1` to `100` | The target brightness in percent at the end of the transition |
| `kelvin`     | `1500` to `9000` | The target kelvin value at the end of the transition |
| `duration`   | `1` to `1440` | How long the transition should run in minutes |
| `power`      | `[ on | off | ignore ]` | Either the bulbs turn _on_ before the transition starts or turn _off_ when it ends. If you specify ignore, the power state remains unchanged. |

The [`sample-daydusk.json`](https://github.com/Djelibeybi/docker-lifx-daydusk/blob/master/sample-daydusk.json) file matches the default LIFX Day & Dusk times, brightness and kelvin values but does not change the power status of the bulbs either before or after the transition.

