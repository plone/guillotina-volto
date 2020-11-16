FROM python:3.8

RUN apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    netcat-openbsd \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src

RUN git clone https://github.com/plone/guillotina.git && cd guillotina && pip install -r requirements.txt && python setup.py develop

WORKDIR /usr/src/app

COPY requirements.txt requirements-test.txt contrib-requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -r contrib-requirements.txt
RUN pip install -r requirements-test.txt

COPY . .

RUN pip install -e .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]