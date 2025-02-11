# Build image: `docker build -t janus_bot:1.0 .`
# Run container: `docker run -it -p 8000:8000 --name janus_bot_app janus_bot:1.0`

FROM python:3.13.1-slim

# Update package list
RUN apt-get update

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install python packages
WORKDIR /tmp/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Create a directory `/app/` in the container and change the working directory to `/app/`
WORKDIR /app/

# Copy the contents of the `app/` directory to the WORKDIR in the container
COPY app/ .

RUN chmod +x start-app.sh

# Expose port 8000
EXPOSE 8000/tcp

CMD ["./start-app.sh"]
