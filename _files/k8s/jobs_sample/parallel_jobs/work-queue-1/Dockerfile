# Specify BROKER_URL and QUEUE when running
FROM john1wang/job-wq-1:latest

COPY ./worker.py /worker.py
RUN chmod 777 ./worker.py

CMD  /usr/bin/amqp-consume --url=$BROKER_URL -q $QUEUE -c 1 /worker.py
