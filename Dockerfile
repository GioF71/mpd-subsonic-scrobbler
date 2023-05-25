FROM python

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

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

RUN mkdir /code
COPY mpd_subsonic_scrobbler/*.py /code/

VOLUME /config

WORKDIR /code

ENTRYPOINT [ "python3", "scrobbler.py" ]
