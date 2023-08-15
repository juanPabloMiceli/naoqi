# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container to /app
WORKDIR /nao_chat

# Add the current directory contents into the container at /app
# ADD ../nao_chat /nao_chat

ENV PYTHONPATH "${PYTHONPATH}:/nao_chat"

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml file into the working directory
COPY ./pyproject.toml /nao_chat/

EXPOSE 7860

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
