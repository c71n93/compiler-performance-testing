FROM ubuntu-python-lnt-suite-clang-gcc-cmake-maple-ssh-1

WORKDIR /home

#copy script and all required files
COPY . /home/compiler-performance-testing

#install required packages for running llvm-test-suite
# RUN apt-get update && apt-get install -y python3 && apt-get -y install python3-pip && apt-get -y install git

#install required python packages
# RUN pip3 install paramiko && pip3 install virtualenv

#install lnt
# RUN mkdir -p /home/lnt-venv && virtualenv /home/lnt-venv && git clone https://github.com/llvm/llvm-lnt.git /home/lnt && ~/lnt-venv/bin/python ~/lnt/setup.py develop

#clone and set llvm-test-suite
# RUN git clone https://github.com/llvm/llvm-test-suite.git test-suite
# COPY ./docker-settings/lit.cfg /home/test-suite/

#install compilers
# RUN apt-get update && apt-get -y install clang && apt-get -y install gcc-aarch64-linux-gnu && apt-get -y install g++-aarch64-linux-gnu

#install cmake
# ARG DEBIAN_FRONTEND=noninteractive
# RUN apt-get update && apt-get -y install ninja-build && apt-get -y install cmake

#install packages for OpenArkCompiler
# RUN apt-get update && apt-get install -y lsb-release && apt install -y libtinfo5

#install rsync
# RUN apt-get update && apt-get install -y rsync

#generate SSH key pair
# RUN ["/bin/bash", "-c", "ssh-keygen -q -t rsa -N '' -f /root/.ssh/id_rsa <<<y >/dev/null 2>&1"]