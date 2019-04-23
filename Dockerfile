FROM python:3.7.3
COPY . /opt

WORKDIR /opt
RUN pip3 install -r requirements.txt && \
    ./run_tests.sh

