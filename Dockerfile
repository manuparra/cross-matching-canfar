FROM jupyter/scipy-notebook:ubuntu-22.04

USER root
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install astropy==5.3.4 matplotlib==3.8.0 pyvo==1.4.2 scipy==1.11.3 seaborn==0.13.0

RUN mkdir /scripts
RUN mkdir /jupyter

COPY scripts /scripts
COPY jupyter /jupyter

ADD config/nsswitch.conf /etc/


WORKDIR /scripts/

USER $NB_UID
ENV HOME=/arc/home/$NB_USER \
        NB_USER=$NB_USER \
        NB_UID=$NB_UID \
        NB_GID=$NB_GID \
        LC_ALL=en_US.UTF-8 \
        LANG=en_US.UTF-8

ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
