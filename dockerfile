
FROM python:3.9-bullseye


RUN apt-get update && apt-get install -y curl gnupg2
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev


WORKDIR /app


COPY . /app

RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000


CMD ["python", "app.py"]