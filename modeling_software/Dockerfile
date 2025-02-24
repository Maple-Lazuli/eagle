FROM ghcr.io/astral-sh/uv:python3.10-alpine

COPY ./modeling_software  /opt/app/modeling_software/

COPY pyproject.toml /opt/app/

COPY uv.lock /opt/app/

WORKDIR /opt/app

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libpq \
    openssl-dev \
    cmake \
    make \
    build-base \
    boost-dev \
    zlib-dev \
    curl \
    libpq-dev \
    git \
    && rm -rf /var/cache/apk/*

RUN git clone --no-checkout https://github.com/apache/arrow.git /arrow \
&& cd /arrow \
&& git checkout tags/apache-arrow-19.0.0 \
&& cd cpp \
&& mkdir build \
&& cd build \
&& cmake -DARROW_CSV=ON -DARROW_JSON=ON -DARROW_FILESYSTEM=ON .. \
&& make -j$(nproc) \
&& make install

RUN uv sync

CMD [ "uv", "run","streamlit", "run", "modeling_software/streamlit_app.py"]