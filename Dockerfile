FROM python:3.6-alpine3.7

WORKDIR ./src/web-monitor

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./src/web-monitor/web_monitor.py"]