FROM python:3


RUN apt-get update \
&&apt-get install -y sqlite3

RUN mkdir /var/run/dao

COPY *.py /var/run/dao

COPY config.json /var/run/dao

COPY run.sh /var/run/dao

WORKDIR /var/run/dao

COPY requirements.txt /var/run/dao

RUN pip install -r /var/run/dao/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

CMD ["/bin/bash","/var/run/dao/run.sh"]
