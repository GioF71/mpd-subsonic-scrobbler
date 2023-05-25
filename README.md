# mpd-subsonic-scrobbler

This is a very simple Subsonic scrobbler for MPD.  
It is not a LAST.FM or libre.fm scrobbler.  
This scrobbler allows mpd to notify a subsonic server when it has played a song which has been server from that subsonic server. The subsonic server might, if configured, scrobble the song to LAST.FM, libre.fm, etc.   
It might be useful when using the Subsonic plugin for Upmpdcli. See the discussion [here](https://github.com/navidrome/navidrome/discussions/2324).

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

The last two provide a simple way to deploy mpd and upmpdcli using docker.  

### Repositories for this project

Repo|URL
:---|:---
Source code|[GitHub](https://github.com/GioF71/mpd-subsonic-scrobbler)
Docker images|[Docker Hub](https://hub.docker.com/r/giof71/mpd-subsonic-scrobbler)

## Available Archs on Docker Hub

- linux/amd64
- linux/arm/v7
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
SUBSONIC_CREDENTIALS|Reference to a file with credentials, alternative to specifying `SUBSONIC_USER` and `SUBSONIC_PASSWORD`|
MIN_COVERAGE|Percent of the song that needs to be played|50
ENOUGH_PLAYBACK_SEC|Minimum playback time needed for a scrobble, regardless of coverage, defaults to `240`
SLEEP_TIME|Interval between a coverage check and the next, in millisec|1000
REDACT_CREDENTIALS|If set to `1`, credentials are not displayed on startup
MAX_SUBSONIC_SERVERS|Max number of SubSonic servers, defaults to `10`
MAX_MPD_INSTANCES|Max number of MPD instances, defaults to `10`
MPD_CLIENT_TIMEOUT_SEC|Mpd client timeout, defaults to `0.05` (one value across all mpd instance)
ITERATION_DURATION_THRESHOLD_PERCENT|If total handle_playback elapsed time is greater than this percentage of `SLEEP_TIME`, a warning is displayed on the standard output. In this case, you should increase `SLEEP_TIME`, reduce `MPD_CLIENT_TIMEOUT_SEC`, or increase this threshold
VERBOSE|Verbose output, valid values are `1` and `0`|0

The subsonic configuration parameters are required: either specificy the individual variables, or specify a SUBSONIC_PARAMETERS to indicate the file which will contain the parameters. The file must be accessible to the container. You can use the /config volume and put a file named, e.g. ".subsonic.env" there.  
All the MPD_* (unless specified) and SUBSONIC_* variables can be suffixed with `_1`, `_2`, `_3` etc in order to configure multiple mpd instances and multiple SubSonic servers.  
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
