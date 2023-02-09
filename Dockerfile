FROM python:3.6

USER root

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt -i https://pypi.douban.com/simple/

CMD ["python", "main.py"]
