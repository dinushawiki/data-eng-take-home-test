FROM python:3.6

# Update the package lists
RUN apt-get update

COPY . /data-eng-take-home-test

WORKDIR /data-eng-take-home-test

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Dash uses
EXPOSE 8050

CMD ["python", "app.py"]