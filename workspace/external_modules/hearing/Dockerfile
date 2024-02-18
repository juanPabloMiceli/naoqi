# Use an official Python runtime as a parent image
FROM python:3.8

ENV PYTHONPATH "${PYTHONPATH}:/app/workspace"

# Set the working directory in the container to /app
WORKDIR /app

# Add current directory code to /app in container
ADD . /app/workspace/external_modules/hearing

# install mic input dependencies
RUN apt-get update && apt-get install -y pulseaudio portaudio19-dev

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml pyproject.toml

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Expose port 8000 to the Docker host, so we can access it
# from the outside.
EXPOSE 8000