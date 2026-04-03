# Dockerfile for Spark ETL Application with DataFlint
FROM apache/spark:3.4.1

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies as root to avoid permission issues
USER root
RUN pip3 install --no-cache-dir -r requirements.txt
USER spark

# Copy application code and entrypoint script
USER root
COPY app/ /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create output directory
RUN mkdir -p /data/output

# Download DataFlint JAR to /app (avoid Ivy cache permission issues)
RUN wget -q -O /app/spark_2.12-0.8.8.jar https://repo1.maven.org/maven2/io/dataflint/spark_2.12/0.8.8/spark_2.12-0.8.8.jar

# Run as root for entrypoint (needs to create/chmod directories)
USER root

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SPARK_HOME=/opt/spark
ENV DATAFLINT_ENABLED=true

# Default command
ENTRYPOINT ["/entrypoint.sh"]
