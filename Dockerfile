FROM python:3.9.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /backend
COPY requirements.txt /backend/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY . /backend

CMD ["bash", "-c", "python3 manage.py makemigrations && python manage.py migrate --fake-initial &&  python3 manage.py loaddata data.json && python3 manage.py runserver 0.0.0.0:8000"]