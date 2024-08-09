FROM python:3.10.0

RUN apt-get update && apt-get -y install cmake protobuf-compiler && apt-get install ffmpeg libsm6 libxext6  -y
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

RUN pip install uwsgi


COPY  . /app/
WORKDIR /app

RUN pip install -r /app/requirements.txt

EXPOSE 9876

CMD [ "uwsgi", "--ini", "/app/uwsgi.ini" ]