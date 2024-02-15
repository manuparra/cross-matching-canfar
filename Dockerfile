FROM python:3.10

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install astropy==5.3.4 matplotlib==3.8.0 pyvo==1.4.2 scipy==1.11.3 seaborn==0.13.0

RUN mkdir /script
RUN mkdir /jupyter

COPY scripts /scripts
COPY jupyter /jupyter

ADD config/nsswitch.conf /etc/


WORKDIR /scripts/

ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]

#
