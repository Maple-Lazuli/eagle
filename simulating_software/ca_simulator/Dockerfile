FROM ghcr.io/astral-sh/uv:python3.10-alpine

COPY ./ca_simulator  /opt/app/ca_simulator/

COPY pyproject.toml /opt/app/

WORKDIR /opt/app

RUN apk update && apk add --no-cache gcc musl-dev libpq-dev openssl

RUN uv sync

CMD [ "uv", "run", "ca_simulator/app.py"]