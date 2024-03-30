FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install  -r requirements.txt
EXPOSE 5000
ENV FLASK_APP=src/app.py
CMD ["flask", "run", "--host", "0.0.0.0"]
