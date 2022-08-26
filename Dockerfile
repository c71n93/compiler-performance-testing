FROM korostinskiyr/compiler_performance_testing:manual

WORKDIR /home

# copy script and all required files
RUN rm -r /home/compiler-performance-testing
COPY . /home/compiler-performance-testing

# install required packages for running llvm-test-suite
RUN apt-get update && \
 	apt-get install -y python3 && \
	apt-get -y install python3-pip && \
	apt-get install python-is-python3 && \
	apt-get -y install git

# install required python packages
RUN pip3 install paramiko && \
	pip3 install virtualenv

# install lnt
RUN mkdir -p /home/lnt-venv && \
	virtualenv /home/lnt-venv && \
	git clone https://github.com/llvm/llvm-lnt.git /home/lnt && \
	~/lnt-venv/bin/python ~/lnt/setup.py develop

# clone and set llvm-test-suite
RUN git clone https://github.com/llvm/llvm-test-suite.git test-suite
COPY ./docker-settings/lit.cfg /home/test-suite/

# install cmake, ninja and rsync
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
	apt-get -y install ninja-build && \
	apt-get -y install cmake && \
	apt-get install -y rsync

# install clang and gcc
RUN apt-get update && \
	apt-get -y install clang && \
	apt-get -y install gcc-aarch64-linux-gnu && \
	apt-get -y install g++-aarch64-linux-gnu

# clone OpenArkCompiler
RUN git clone https://gitee.com/openarkcompiler/OpenArkCompiler

# install packages for OpenArkCompiler
RUN apt-get update && \
	apt-get -y install wget && \
	apt-get -y install unzip && \
	apt-get install -y lsb-release && \
	apt install -y libtinfo5

# build OpenArkCompiler
WORKDIR /home/OpenArkCompiler
RUN ["/bin/bash", "-c", "source build/envsetup.sh arm release && make setup"]
RUN ["/bin/bash", "-c", "source build/envsetup.sh arm release && make"]

WORKDIR /home

# generate SSH key pair
RUN apt-get update && \
	apt-get install sshpass
RUN ["/bin/bash", "-c",
	"ssh-keygen -q -t rsa -N '' -f /root/.ssh/id_rsa <<<y >/dev/null 2>&1"]

#execute script
WORKDIR /home/compiler-performance-testing
ENTRYPOINT ["./docker-script.py"]