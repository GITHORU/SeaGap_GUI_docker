# Use an official Python runtime as a parent image
#FROM julia:1.11.1
FROM python:3.11-slim AS base


# Set the working directory for your app
WORKDIR /app

# Set environment variables to ensure Python outputs are flushed immediately
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1


## Install system dependencies for Python and Julia
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    apt-get install -y xcb-cursor0 &&\
    rm -rf /var/lib/apt/lists/

COPY requirements.txt .
COPY customDialogs.py .
COPY customLayout.py .
COPY gui.py .
COPY GARPOS2SeaGap.py .
COPY init_julia.py .
RUN mkdir img
COPY img/* img
RUN pip install --no-cache-dir -r requirements.txt
RUN python init_julia.py

 # Clone the external GitHub repository containing Julia functions
#RUN git clone https://github.com/GITHORU/SeaGap_GITHORU.git # /opt/julia_functions

## Copy the rest of your application code
#COPY . .

# Expose the port your app runs on
EXPOSE 5000

# Specify the command to run your application
#RUN julia -e "using Pkg; Pkg.add(url=''); Pkg.add('https://github.com/f-tommy/SeaGapR.git')"
#CMD ["julia","-e", "using Pkg; Pkg.add(url=''); Pkg.add('https://github.com/f-tommy/SeaGapR.git')"]
CMD ["python", "./gui.py"]
#CMD ["python"]