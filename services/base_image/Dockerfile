FROM chryswoods/acquire-base:latest

WORKDIR /function
USER root

ADD requirements.txt .

RUN pip3 install -U pip

RUN pip3 install --upgrade --target /python/ --no-cache --no-cache-dir \
                 -r requirements.txt && \
    rm -fr ~/.cache/pip /tmp* requirements.txt func.yaml Dockerfile .venv

ADD HUGS $PYTHON_EXT/HUGS

ADD runner_key /home/$FN_USER/.ssh/

RUN python3 -m compileall $PYTHON_EXT/HUGS/*

ENTRYPOINT ["bash"]

# Become the $FN_USER so that nothing runs as root
USER $FN_USER
