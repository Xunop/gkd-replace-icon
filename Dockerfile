FROM openjdk:24-bookworm

COPY . /app
WORKDIR /app

# Install python3, zipalign
RUN apt-get update && apt-get install -y python3 zipalign

RUN mkdir -p /app/out && chmod -R 777 /app/out

# python3 replace_icon.py <apk>
ENTRYPOINT ["python3", "replace_icon.py"]
