FROM python:3.12-slim-bookworm

# Set environment variables (can be overridden at runtime)
ENV DEBIAN_FRONTEND=noninteractive
ENV OMP_STACKSIZE=8G
ENV OMP_NUM_THREADS=1
ENV XTB_HOME=/opt/xtb
ENV LD_LIBRARY_PATH=${XTB_HOME}/lib

# Install system dependencies including curl and ca-certificates for uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    tar \
    xz-utils \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Set stack size unlimited
RUN echo "* soft stack unlimited" >> /etc/security/limits.conf && \
    echo "* hard stack unlimited" >> /etc/security/limits.conf

# Create working directories
WORKDIR /app

# Install Python dependencies with uv
COPY requirements.txt .
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python -r requirements.txt


#=================================
# Download and install xTB

RUN mkdir -p /opt/xtb

RUN wget https://github.com/grimme-lab/xtb/releases/download/v6.7.1/xtb-6.7.1-linux-x86_64.tar.xz -O /tmp/xtb.tar.xz && \
    cd /opt && \
    tar -xf /tmp/xtb.tar.xz && \
    mv xtb-dist/* xtb/ && \
    rmdir xtb-dist && \
    rm /tmp/xtb.tar.xz


# Set final PATH with both xtb and python venv
ENV PATH="/opt/xtb/bin:/opt/venv/bin:$PATH"
# Create entrypoint script that respects environment variables
RUN echo '#!/bin/bash\nulimit -s unlimited\nexport OMP_STACKSIZE=${OMP_STACKSIZE:-8G}\nexport OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}\nexec "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh
#=================================

# Copy application code
COPY app.py .

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8888"]
#CMD ["uvicorn", "app:app", "--host", "::", "--port", "8888"]

