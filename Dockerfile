# Use the latest official Python image as the base image
FROM python:latest
EXPOSE 8000

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app/

# Install dependencies
COPY . /app/
RUN pip install -r requirements.txt

# Make the entrypoint script executable and set it as the entrypoint
COPY entrypoint.sh /app/

ENTRYPOINT ["sh","entrypoint.sh"]

# CMD [ "python", "manage.py", "runserver" ]
