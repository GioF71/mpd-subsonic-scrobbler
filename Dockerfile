FROM python:slim AS BASE

RUN apt-get update
RUN apt-get install -y build-essential

RUN pip install poetry

WORKDIR /code/
COPY . /code/

RUN poetry install

RUN apt-get remove -y build-essential
RUN apt-get -y autoremove
RUN	rm -rf /var/lib/apt/lists/*

FROM scratch
COPY --from=BASE / /

LABEL maintainer="GioF71"
LABEL source="https://github.com/GioF71/mpd-subsonic-scrobbler"

ENV MPD_FRIENDLY_NAME ""
ENV MPD_HOST ""
ENV MPD_PORT ""

ENV SUBSONIC_PARAMETERS_FILE ""

ENV SUBSONIC_FRIENDLY_NAME ""
ENV SUBSONIC_BASE_URL ""
ENV SUBSONIC_PORT ""
ENV SUBSONIC_USER ""
ENV SUBSONIC_PASSWORD ""
ENV SUBSONIC_CREDENTIALS ""
ENV SUBSONIC_UPMPDCLI_BASE_URL ""
ENV SUBSONIC_UPMPDCLI_PORT ""

ENV MIN_COVERAGE ""
ENV ENOUGH_PLAYBACK_SEC ""
ENV SLEEP_TIME ""
ENV VERBOSE ""

ENV REDACT_CREDENTIALS ""

ENV MAX_SUBSONIC_SERVERS ""
ENV MAX_MPD_INSTANCES ""

ENV MPD_CLIENT_TIMEOUT_SEC ""
ENV ITERATION_DURATION_THRESHOLD_PERCENT ""

ENV PYTHONUNBUFFERED=1

WORKDIR /code/mpd_subsonic_scrobbler

ENTRYPOINT [ "poetry", "run", "python", "scrobbler.py" ]
