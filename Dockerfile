# use official Python slim image
FROM python:3.11-slim

# set working directory
WORKDIR /app

# copy requirements first (for caching)
COPY requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the code
COPY . .

ENV PORT=8080

# command to run uvicorn
CMD ["sh", "-c", "uvicorn application:app --host 0.0.0.0 --port ${PORT}"]
