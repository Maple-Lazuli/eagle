FROM ghcr.io/astral-sh/uv:python3.10-alpine

COPY ./it_account_simulator  /opt/app/it_account_simulator/

COPY pyproject.toml /opt/app/

WORKDIR /opt/app

RUN apk update && apk add --no-cache gcc musl-dev libpq-dev

RUN uv sync

CMD [ "uv", "run", "it_account_simulator/app.py"]