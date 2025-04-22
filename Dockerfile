# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# Ensure constants.py, getDB.py, llm.py, Tools.py are copied
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run index.py when the container launches using streamlit
# Bind to 0.0.0.0 to allow external access
CMD ["streamlit", "run", "index.py", "--server.port=8501", "--server.address=0.0.0.0"]

# 환경 변수 설정
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV SUPABASE_URL=${SUPABASE_URL}
ENV SUPABASE_KEY=${SUPABASE_KEY}
ENV DATABASE_URL=${DATABASE_URL} 