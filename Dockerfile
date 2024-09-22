# Use conda-forge's Miniconda base image
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment.yml to the working directory
COPY environment.yml /app/environment.yml

# Create and activate the Conda environment
RUN conda env create -f environment.yml

# Use the conda environment as the default shell
SHELL ["conda", "run", "-n", "ShareLMAPI", "/bin/bash", "-c"]

# Copy the project files to the container
COPY . /app

# Install any additional dependencies with pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables to avoid buffering issues
ENV PYTHONUNBUFFERED=1

# Expose the necessary ports for the two servers
EXPOSE 5000 8000
