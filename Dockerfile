FROM python:3.10-slim-buster

# Update and install git
RUN apt update && apt upgrade -y && apt install -y git
RUN pip install https://github.com/KurimuzonAkuma/pyrogram/archive/v2.1.29.zip --force-reinstall
# Set work directory and copy everything
WORKDIR /EvaMaria
COPY . .

# Make the start.sh script executable
RUN chmod +x start.sh

# Install Python requirements
RUN pip3 install -U pip && pip3 install -U -r requirements.txt

# Set the startup command
CMD ["./start.sh"]
