FROM ghcr.io/astral-sh/uv:python3.10-alpine

COPY ./user_simulator  /opt/app/user_simulator/

COPY pyproject.toml /opt/app/

WORKDIR /opt/app

RUN apk update && apk add --no-cache gcc musl-dev libpq-dev openssl

RUN uv sync

CMD [ "uv", "run", "user_simulator/user.py"]