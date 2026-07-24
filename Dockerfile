FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
	build-essential \
	libpq-dev \
	&& rm -rf /var/lib/lists/*
	
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
