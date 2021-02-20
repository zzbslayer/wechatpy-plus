FROM python:3.8-slim-buster AS develop

# aliyun source
RUN sed -i 's#http://deb.debian.org#https://mirrors.aliyun.com#g' /etc/apt/sources.list

# time zone
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' >/etc/timezone

# python dependencies
RUN mkdir -p /app
WORKDIR /app
ADD ./requirements.txt /app/
RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

# deploy with hypercorn
ADD ./ /app/
CMD hypercorn --bind '0.0.0.0:80' run:app
