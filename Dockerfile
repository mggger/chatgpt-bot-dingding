FROM python:3.7

USER root

WORKDIR /app

ADD . /app

#RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["python", "main.py"]
