# mpd-subsonic-scrobbler

This is a very simple Subsonic scrobbler for MPD.  
It is not a LAST.FM or libre.fm scrobbler.  
This scrobbler allows mpd to notify a subsonic server when it has played a song which has been server from that subsonic server. The subsonic server might, if configured, scrobble the song to LAST.FM, libre.fm, etc.   
It might be useful when using the Subsonic plugin for Upmpdcli. See the discussion [here](https://github.com/navidrome/navidrome/discussions/2324).

## Support

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H7UIN5D)  
Please see the [Goal](https://ko-fi.com/giof71/goal?g=0).  
Please note that support goal is limited to cover running costs for subscriptions to music services.

## Important notice

Initially I used [this](https://hub.docker.com/r/giof71/subsonic-mpd-scrobbler) docker repo. I then noticed that it was named differently from the github repo.  
So I created a new docker hub repo [here](https://hub.docker.com/r/giof71/mpd-subsonic-scrobbler) and updated the documentation.  
The old docker hub repo will not receive updates of course. Please correct your docker compose/run so that they reference the correct image name.  
Sorry for the inconvenience

## Links

### Related projects

PROJECT|Git Repo(s)
:---|:---
[Music Player Daemon](https://www.musicpd.org/)|On [GitHub](https://github.com/MusicPlayerDaemon/MPD)
[Upmpdcli](https://www.lesbonscomptes.com/upmpdcli/pages/upmpdcli-manual.html)|[Framagit](https://framagit.org/medoc92/upmpdcli) [(Mirror)](https://codeberg.org/medoc/upmpdcli). [My Fork](https://framagit.org/giof71/upmpdcli) [(Mirror)](https://codeberg.org/giof71/upmpdcli)
mpd-alsa-docker|[GitHub](https://github.com/GioF71/mpd-alsa-docker)
upmpdcli-docker|[GitHub](https://github.com/GioF71/upmpdcli-docker)
subsonic-connector|[GitHub](https://github.com/GioF71/subsonic-connector)
python-mpd2|[GitHub](https://github.com/Mic92/python-mpd2)

Among those, `mpd-alsa-docker` and `upmpdcli-docker` provide a method for deploying mpd and upmpdcli using docker.  

### Repositories for this project

Repo|URL
:---|:---
Source code|[GitHub](https://github.com/GioF71/mpd-subsonic-scrobbler)
Docker images|[Docker Hub](https://hub.docker.com/r/giof71/mpd-subsonic-scrobbler)

## Available Archs on Docker Hub

- linux/amd64
- linux/arm/v7
- linux/arm/v5
- linux/arm64/v8

## Usage

### Volumes

VOLUME|DESCRIPTION
:---|:---
/config|Suggested location for additional configuration files

### Enviroment Variables

VARIABLE|DESCRIPTION|DEFAULT
:---|:---|:---
MPD_FRIENDLY_NAME|Friendly name of the mpd instance|
MPD_HOST|MPD hostname|localhost
MPD_PORT|MPD port|6600
SUBSONIC_FRIENDLY_NAME|Friendly name of the subsonic server|
SUBSONIC_PARAMETERS_FILE|Separate config file for subsonic parameters|
SUBSONIC_BASE_URL|Subsonic Server URL, including `http` or `https`|
SUBSONIC_PORT|Subsonic Server Port|
SUBSONIC_USER|Subsonic Username|
SUBSONIC_PASSWORD|Subsonic password|
SUBSONIC_LEGACYAUTH|Legacy authentication, required to `true` for lms, defaults to `false`
SUBSONIC_CREDENTIALS|Reference to a file with credentials, alternative to specifying `SUBSONIC_USER` and `SUBSONIC_PASSWORD`|
SUBSONIC_UPMPDCLI_BASE_URL|If set, only this upmpdcli server will be allowed (base url)
SUBSONIC_UPMPDCLI_PORT|If set, only this upmpdcli server will be allowed (port)
MIN_COVERAGE|Percent of the song that needs to be played|50
ENOUGH_PLAYBACK_SEC|Minimum playback time needed for a scrobble, regardless of coverage, defaults to `240`
SLEEP_TIME|Interval between a coverage check and the next, in millisec|1000
REDACT_CREDENTIALS|If set to `1`, credentials are not displayed on startup
MAX_SUBSONIC_SERVERS|Max number of SubSonic servers, defaults to `10`
MAX_MPD_INSTANCES|Max number of MPD instances, defaults to `10`
MPD_CLIENT_TIMEOUT_SEC|Mpd client timeout, defaults to `0.05` (one value across all mpd instance)
ITERATION_DURATION_THRESHOLD_PERCENT|If total handle_playback elapsed time is greater than this percentage of `SLEEP_TIME`, a warning is displayed on the standard output. In this case, you should increase `SLEEP_TIME`, reduce `MPD_CLIENT_TIMEOUT_SEC`, or increase this threshold
MPD_IMPOSED_SLEEP_ITERATION_COUNT|Number of iteration an instance of mpd must `sleep` when it appears to not be accessible, defaults to `30`
VERBOSE|Verbose output, valid values are `1` and `0`|0

The subsonic configuration parameters are required: either specificy the individual variables, or specify a SUBSONIC_PARAMETERS to indicate the file which will contain the parameters. The file must be accessible to the container. You can use the /config volume and put a file named, e.g. ".subsonic.env" there.  
All the `MPD_*` (unless specified) and `SUBSONIC_*` variables can be suffixed with `_1`, `_2`, `_3` etc in order to configure multiple mpd instances and multiple SubSonic servers.  
Inside a single config file, even if it refer to an index > 0, the variable names must be specified without the index.

### Example configurations

The following compose file creates a subsonic scrobbler for `mpd-d10` (as it operates on a Topping D10 DAC) and `mpd-d200` (as it operates on a Yulong D200 DAC), which are instances of `mpd-alsa-docker` running on the same host and specifically on the network `mpd`.  
Subsonic config is read from a separate file.  

```text
---
version: "3"

networks:
  mpd:
    external: true

services:
  scrobbler:
    image: giof71/mpd-subsonic-scrobbler:latest
    container_name: subsonic-scrobbler-d10
    networks:
      - mpd
    environment:
      - MPD_HOST=mpd-d10
      - MPD_PORT=6600
      - MPD_HOST_1=mpd-d200
      - MPD_PORT_1=6600
      - SUBSONIC_PARAMETERS_FILE=/config/my-navidrome.env
      - SUBSONIC_PARAMETERS_FILE_1=/config/navidrome-demo.env
      - VERBOSE=0
    volumes:
      - ./my-navidrome.env:/config/my-navidrome.env:ro
      - ./navidrome-demo.env:/config/navidrome-demo.env:ro
    restart: unless-stopped
```

Same situation, without the separate file:

```text
---
version: "3"

networks:
  mpd:
    external: true

services:
  scrobbler:
    image: giof71/mpd-subsonic-scrobbler:latest
    container_name: subsonic-scrobbler-d10
    networks:
      - mpd
    environment:
      - MPD_HOST=mpd-d10
      - MPD_PORT=6600
      - MPD_HOST_1=mpd-d200
      - MPD_PORT_1=6600
      - SUBSONIC_BASE_URL=${MY_NAVIDROME_BASE_URL}
      - SUBSONIC_PORT=${MY_NAVIDROME_PORT}
      - SUBSONIC_USER=${MY_NAVIDROME_USER}
      - SUBSONIC_PASSWORD=${MY_NAVIDROME_PASSWORD}
      - SUBSONIC_BASE_URL_1=${NAVIDROME_DEMO_BASE_URL}
      - SUBSONIC_PORT_1=${NAVIDROME_DEMO_PORT}
      - SUBSONIC_USER_1=${NAVIDROME_DEMO_USER}
      - SUBSONIC_PASSWORD_1=${NAVIDROME_DEMO_PASSWORD}
      - VERBOSE=0
    restart: unless-stopped
```

In this case, the configuration parameters are read from the `.env` file.  
In order to avoid issues with password, which might contain special characters, it is better to not place such password on the compose file, and leverage the `.env` file instead.  

## Releases

### Release 0.5.4

- Introduced caching against subsonic servers

### Release 0.5.3

- Build using setuptools
- Extracted functions (reduce function length)
- Misc cleanup

### Release 0.5.2

- Correct version in source code
- Improved logging

### Release 0.5.1

- Reduce cpu usage (see [#53](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/53))

### Release 0.5.0 (2024-04-19)

- Bug: fixed repeated scrobbles
- Code style fixed (flake8)
- Bump subsonic-connector to 0.3.4
- Bump py-sonic to 1.0.1

### Release 0.4.0 (2023-11-13)

- Effectively use mpd timeout parameter and handle timeout errors
- Handle non-accessible mpd instances
- Slightly improved code readability
- Dump legacy authentication parameter

### Release 0.3.6 (2023-11-11)

- Handle unavailable servers gracefully (see issue [#48](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/48))

### Release 0.3.5 (2023-11-11)

- Simplified mpd reconnection code (see issue [#46](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/46))

### Release 0.3.4 (2023-11-11)

- Compatibility with latest subsonic-connector, for legacy authentication (see issue [#44](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/44))

### Release 0.3.3 (2023-11-11)

- Recreate mpd connection in case of failure (see issue [#39](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/39))

### Release 0.3.2 (2023-11-06)

- Check song id belongs to current server (see issue [#39](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/39))

### Release 0.3.1 (2023-11-04)

- Display upmpdcli configuration parameters (see issue [#37](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/37))

### Release 0.3.0 (2023-11-04)

- Allow upmpdcli server restrictions (see issue [#35](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/35))

### Release 0.2.2 (2023-10-28)

- Handle mpd disconnections (see issue [#32](https://github.com/GioF71/mpd-subsonic-scrobbler/issues/32))

### Release 0.2.1 (2023-10-28)

- Support for upmpdcli intermediate urls

### Release 0.2.0 (2023-05-25)

- Support for multiple mpd instances

### Release 0.1.2 (2023-05-18)

- Support for multiple subsonic servers
- Code refactor and cleanup
- Remove need to set PYTHONUNBUFFERED=1 in compose file

### Release 0.1.1 (2023-05-13)

- Mostly documentation changes

### Release 0.1.0 (Initial Release, 2023-05-12) 

- First working release
