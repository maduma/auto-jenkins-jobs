from python:3.8.2

ENV AUTOJJ_VERSION=v0.1.1
#ENV GITLAB_PRIVATE_TOKEN
#ENV JENKINS_SERVER
#ENV JENKINS_USERNAME
#ENV JENKINS_PASSWORD

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN useradd -m autojj
WORKDIR /home/autojj
COPY . .

USER autojj
ENTRYPOINT ["gunicorn", "--workers", "1", "--threads", "1", "--bind", "0.0.0.0:5000", "web:app"]
EXPOSE 5000
