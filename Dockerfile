FROM python:3.10-slim-buster

# Install system packages and Python dependencies
RUN apt update && apt upgrade -y && \
    apt install git -y && \
    pip3 install --upgrade pip

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

# Copy bot code and entrypoint
RUN mkdir /EvaMaria
WORKDIR /EvaMaria
COPY . /EvaMaria
RUN chmod +x /start.sh

# Expose port 8080 for Koyeb's TCP health check
EXPOSE 8080

CMD ["/bin/bash", "/start.sh"]
