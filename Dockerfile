FROM python:3

RUN mkdir -p /etc/tor
ADD brands /brands
ADD main.py /
ADD requirements.txt ./

RUN pip install -r ./requirements.txt

RUN mkdir -p /data
ENV SAVE_PATH /data

WORKDIR /
ADD jholiday.py /

CMD [ "python", "-u", "./main.py" ]