FROM locustio/locust
RUN cd /home/
RUN mkdir "dongmanlocustproject"
WORKDIR /home/dongmanlocustproject

COPY requirements.txt ./

RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .

