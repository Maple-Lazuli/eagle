FROM ghcr.io/astral-sh/uv:python3.10-alpine

COPY ./hr_simulator  /opt/app/hr_simulator/

COPY pyproject.toml /opt/app/

WORKDIR /opt/app

RUN uv sync

CMD [ "uv", "run", "hr_simulator/app.py"]