FROM jupyter/minimal-notebook:ubuntu-22.04

USER root

COPY . /opt/cross-matching

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r /opt/cross-matching/requirements.txt

RUN fix-permissions /opt/cross-matching

WORKDIR /opt/cross-matching/jupyter/notebooks

USER $NB_UID
