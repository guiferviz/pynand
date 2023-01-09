################
#  Base image  #
################

FROM python:3.10


#########################
# Define env variables. #
#########################

ENV WORKDIR /workspace


#####################
# Install programs. #
#####################

# Install any other dependencies here.
# ...
# Install Python wheel.
COPY dist/*.whl /root/wheel/
RUN pip install /root/wheel/*.whl


#########
# Setup #
#########

WORKDIR $WORKDIR

ENTRYPOINT ["wire"]
# Default command:
CMD ["--help"]
