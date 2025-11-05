FROM ubuntu:22.04


# Cài đặt Python 3.10 và các phụ thuộc cơ bản
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget curl gnupg lsb-release \
    python3.10 python3.10-venv python3.10-dev python3.10-distutils \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 làm mặc định
RUN ln -sf /usr/bin/python3.10 /usr/bin/python && \
    ln -sf /usr/bin/python3.10 /usr/bin/python3

# Cài pip bằng cách tải script về đĩa rồi chạy
RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

# Tạo thư mục làm việc
WORKDIR /workspace

# Copy requirements và cài đặt
COPY requirements.txt .

RUN python3.10 -m pip install --no-cache-dir --ignore-installed blinker


RUN python3.10 -m pip install --break-system-packages -r requirements.txt


# Copy toàn bộ mã nguồn vào container
COPY . .

# Expose ports
EXPOSE 8000 8051

# Chạy FastAPI server
CMD ["/bin/bash", "-c", "uvicorn server:app --host 0.0.0.0 --port 8000 & python3.10 -m streamlit run font-end/app.py --server.port 8501 --server.address 0.0.0.0"]
