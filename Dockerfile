FROM python:3.10.4

WORKDIR /work

COPY ./requirements.txt /work/
RUN pip install -r requirements.txt

COPY ./ris_2 /work/ris_2