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
MPD_HOST|MPD hostname|localhost
MPD_PORT|MPD port|6600
SUBSONIC_PARAMETERS_FILE|Separate config file for subsonic parameters|
SUBSONIC_BASE_URL|Subsonic Server URL, including `http` or `https`|
SUBSONIC_PORT|Subsonic Server Port|
SUBSONIC_USER|Subsonic Username|
SUBSONIC_PASSWORD|Subsonic password|
VERBOSE|Verbose output, valid values are `1` and `0`|0
MIN_COVERAGE|Percent of the song that needs to be played|50
SLEEP_TIME|Interval between a coverage check and the next, in millisec|1000

The subsonic configuration parameters are required: either specificy the individual variables, or specify a SUBSONIC_PARAMETERS to indicate the file which will contain the parameters. The file must be accessible to the container. You can use the /config volume and put a file named, e.g. ".subsonic.env" there.  

### Example configurations

The following compose file creates a subsonic scrobbler for `mpd-d10`, which is an instance of `mpd-alsa-docker` running on the same host and specifically on the network `mpd`.  
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
      - PYTHONUNBUFFERED=1
      - MPD_HOST=mpd-d10
      - MPD_PORT=6600
      - SUBSONIC_PARAMETERS_FILE=/config/subsonic.env
      - VERBOSE=0
    volumes:
      - ./navidrome.env:/config/subsonic.env:ro
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
      - PYTHONUNBUFFERED=1
      - MPD_HOST=mpd-d10
      - MPD_PORT=6600
      - SUBSONIC_BASE_URL=${SUBSONIC_BASE_URL}
      - SUBSONIC_PORT=${SUBSONIC_PORT}
      - SUBSONIC_USER=${SUBSONIC_USER}
      - SUBSONIC_PASSWORD=${SUBSONIC_PASSWORD}
      - VERBOSE=0
    restart: unless-stopped
```

In this case, the configuration parameters are read from the `.env` file.  
In order to avoid issues with password, which might contain special characters, it is better to not place such password on the compose file, and leverage the `.env` file instead.  
