FROM python:3.6

# Install dash dependencies
ADD ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Set work directory
WORKDIR /work

# Run /bin/bash
CMD /bin/bash