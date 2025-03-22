FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Clone MRISA and install its dependencies
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/vivithemage/mrisa.git
WORKDIR /app/mrisa
RUN pip install --no-cache-dir -r requirements.txt

# Back to app directory
WORKDIR /app

COPY app/ .

# Create uploads directory if it doesn't exist
RUN mkdir -p static/uploads

# Expose ports for Flask app and MRISA
EXPOSE 8080
EXPOSE 5000

# Create a startup script
RUN echo '#!/bin/bash\n\
python /app/mrisa/src/mrisa/server.py & \n\
gunicorn --bind 0.0.0.0:8080 app:app\n' > /app/start.sh

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]