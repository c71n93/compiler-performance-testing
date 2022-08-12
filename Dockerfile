FROM ubuntu-python-lnt-suite-clang-gcc-0

WORKDIR /home

COPY . /home/compiler-performance-testing

# RUN apt-get update && apt-get install -y python3 && apt-get -y install python3-pip && apt-get -y install git

# RUN pip3 install paramiko && pip3 install virtualenv

# RUN mkdir -p /home/lnt-venv && virtualenv /home/lnt-venv && git clone https://github.com/llvm/llvm-lnt.git /home/lnt && ~/lnt-venv/bin/python ~/lnt/setup.py develop

# RUN git clone https://github.com/llvm/llvm-test-suite.git test-suite

# RUN apt-get update && apt-get -y install clang-12 && apt-get -y install gcc-aarch64-linux-gnu && apt-get -y install g++-aarch64-linux-gnu

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get -y install ninja-build && apt-get -y install cmake

# ENTRYPOINT ["./run_llvm_test_suite.py"]