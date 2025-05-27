FROM python:3.9

# Install OS packages for building C extensions and the exact Python 3.11 headers
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
	locales git-core gcc g++ netcat-openbsd libxml2-dev \
    	libxslt-dev libz-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Upgrade pip/setuptools/wheel so we get wheels if they exist
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt requirements-test.txt contrib-requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install -r contrib-requirements.txt \
 && pip install -r requirements-test.txt

COPY . .

# This should now succeed in building typed-ast
RUN pip install -e .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
