ARG VERSION
FROM python:${VERSION}

LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.version = "1.0"


##############################################
### --------INSTALL SOME PACKAGES--------- ###

# All executed commands are printed to the terminal.
RUN set -x

# Packages for other runtime dependenices.
ENV PACKAGES_RUNTIME="curl"
                        
RUN apt-get update && \
apt-get install -y --no-install-recommends $PACKAGES_RUNTIME && \
apt-get autoremove -y && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

### --------------------------------------- ###
###############################################


###############################################
### -------- CORRECT USERID --------------- ###
# Sync www-data with userid and group id of the host machine

ARG USER_ID
ARG GROUP_ID
ARG USER_NAME
ARG GROUP_NAME

RUN if [ ${USER_ID:-0} -ne 0 ] && [ ${GROUP_ID:-0} -ne 0 ]; then \
    groupadd -g ${GROUP_ID} ${GROUP_NAME} &&\
    useradd -m -l -u ${USER_ID} -g ${USER_NAME} ${GROUP_NAME} \
	;fi

### --------------------------------------- ###
###############################################

##############################################
### --------  COPY ENTRYPOINT  ---------- ####

COPY ./copyfs/docker-entrypoint.sh /docker-entrypoint.sh
COPY ./copyfs/docker-entrypoint.d/* /docker-entrypoint.d/

### --------------------------------------- ###
###############################################


##############################################
##### --------  APP SPECIFIC  ---------- #####

USER python

COPY --chown=python:python ./copyfs/opt/app/ /opt/app/
WORKDIR /home/python/app/

EXPOSE ${PYTHON_CONTAINER_PORT}

### --------------------------------------- ###
###############################################

ENTRYPOINT [ "/docker-entrypoint.sh" ]