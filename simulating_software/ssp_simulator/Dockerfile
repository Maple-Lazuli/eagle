FROM ghcr.io/astral-sh/uv:python3.10-alpine

COPY ./ssp_simulator  /opt/app/ssp_simulator/

COPY pyproject.toml /opt/app/

WORKDIR /opt/app

RUN apk update && apk add --no-cache gcc musl-dev libpq-dev

RUN uv sync

CMD [ "uv", "run", "ssp_simulator/app.py"]