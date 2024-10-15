FROM python:3.10
RUN apt-get update && apt-get install -y adb
RUN pip install pipenv
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --system
COPY . .
RUN mkdir data
EXPOSE 5037
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]
