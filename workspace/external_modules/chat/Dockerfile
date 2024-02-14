# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
# ADD ../nao_chat /nao_chat

ENV PYTHONPATH "${PYTHONPATH}:/app/workspace"

# Add current directory code to /app in container
ADD . /app/workspace/external_modules/chat

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml pyproject.toml

EXPOSE 7860

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
