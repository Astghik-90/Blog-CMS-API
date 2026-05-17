FROM python:3.13
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/bin/sh", "-c", "sed -i 's/\r$//' /app/docker-entrypoint.sh && exec /bin/sh /app/docker-entrypoint.sh"]

