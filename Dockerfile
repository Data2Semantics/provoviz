FROM python:2

WORKDIR /code
COPY src/* /code/

#ENV FLASK_APP=run.py
#ENV FLASK_RUN_HOST=0.0.0.0

ADD requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python", "/code/run.py"]

