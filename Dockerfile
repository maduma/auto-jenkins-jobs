from python:3.8.2-slim

ARG AUTOJJ_VERSION
ENV AUTOJJ_VERSION ${AUTOJJ_VERSION}

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd -m autojj
WORKDIR /home/autojj
COPY . .

USER autojj

ENTRYPOINT ["gunicorn", "--access-logfile", "-", "--log-file", "-", "--workers", "1", "--threads", "1", "--bind", "0.0.0.0:5000", "web:app"]
EXPOSE 5000
