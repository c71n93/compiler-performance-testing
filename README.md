# llvm-test-suite build and run ssh script

This python script can help to build and run [llvm-test-suite](https://llvm.org/docs/TestSuiteGuide.html) on board easily.

##### Table of contents

1. [Requirements for proper work](#Requirements-for-proper-work)
2. [Comand-line options](#Comand-line-options)
3. [Config file](#Config-file)
4. [Cmake-toolchain file](#Cmake-toolchain-file)
5. [Test-suite subdirs file](#Test-suite-subdirs-file)
6. [Running tests with docker](#Running-tests-with-docker)
7. [Results](#Results)
8. [Running tests with docker](#Running-tests-with-docker)

## Requirements for proper work

- Install [llvm-lit](https://llvm.org/docs/TestSuiteGuide.html) runner
- Check out the [test-suite](https://github.com/llvm/llvm-test-suite.git) module
- Prepare a [cmake-toolchain file](#Cmake-toolchain-file)
- Prepare a [config file](#Config-file)
- Prepare a [file with test-suite subdirs list](#Test-suite-subdirs-file)
- Connect to the board via ssh **using the ssh key** if you want to sync or run tests

**You can avoid all of this by using docker image [Running tests with docker](#unning-tests-with-docker)**

## Comand-line options

There is some useful comand-line options:

- `-h, --help` - show help message and exit
- `--config CONFIG` *(required)* - config file
- `--build-only` - only build tests
	- `--no-rsync` -  disable synchronization with board (can be used only with --build-only flag)
- `--run-only` - only run tests
- `--nruns NRUNS` (*default = 1*) - number of tests runs (natural number)
- `--compare-results` - compare and print results to stdout
- `--remote-hostname` - IP adress of the board (replaces the value in the config, if specified)
- `--remote-username` - board user name (replaces the value in the config, if specified)
- `--remote-password` - board password (replaces the value in the config, if specified)

*Important note: tests can only be run if they have been built and synced with the board before. Otherwise it will cause errors.*

## Config file

Config file - is a file with required variables. It can be passed to the script with option `--config CONFIG`.

### Structure of config file:
```ini
[PATHS AND FILES] #required
test_suite_path = /path/to/test-suite/ #required
lit_path = /path/to/llvm-lit #required
builds_dir = /path/to/directory/with/build/directories/ #required
sysroot_path = /path/to/headers/and/libraries #optional
test_suite_subdirs_file = path/to/file/with/test-suite/subdirs/list.txt #optional
results_path = /path/to/directory/with/test/results/ #optional

[REMOTE HOST] #required
remote_hostname = 255.255.255.255 #required
remote_username = username #required
remote_password = password #required

[MULTITHREADING] #optional
build_threads = 4 #optional
run_threads = 4 #optional

[TOOLCHAIN 1] #required
toolchain_name = gcc-O0 #optional
build_path = /path/to/build/directory #optional
cmake_toolchain_file = cmake-toolchain/gcc-aarch64-linux.cmake #required

[TOOLCHAIN 2] #optional
...

[TOOLCHAIN 3] #optional
...
```
*You can just copy it and change necessary values*

### Meaning of variables:

**[PATHS AND FILES]** *(required section)*
- `test_suite_path` *(required)* - path to directory with [test-suite](https://github.com/llvm/llvm-test-suite.git) sources
- `lit_path` *(required)* - path to [llvm-lit](https://llvm.org/docs/TestSuiteGuide.html) runner tool
- `build_dir` *(required)* - path to directory where will be build directories for each toolchain *Important note: use build directory only into `/home/` directory. Use only absolute paths*
- `sysroot_path` *(default = [default sysroot]* - path to sysroot, to be passed via `--sysroot` compiler option
- `test_suite_subdirs_file` *(default = [runs all tests])* - path to [file with test-suite subdirs list](#Test-suite-subdirs-file)
- `results_path` *(default = ".")* - path to directory where results will be saved

**[REMOTE HOST]** *(required section)*
- `remote_hostname` *(required)* - IP adress of the board
- `remote_username` *(required)* - board user name
- `remote_password` *(required)* - board password

**[MULTITHREADING]** *(optional section)*
- `build_threads` *(default = 1)* - the number of threads that are used to build tests
- `run_threads` *(default = 1)* - the number of threads that are used to run tests

**[TOOLCHAIN *N*]** *(required at least one section)*
- `toolchain_name` *(default = [cmake toolchain filename])* - this name will be used to generate build directories and result files name; if not specified, will be taken from the cmake toolchain filename
- `build_path` *(default = "`builds_dir`"/"`toolchain_name`"/)* - path to build directory for single toolchain(tests will be compiled there) *Important note: use build directory only into `/home/` directory. Use only absolute paths*
- `cmake_toolchain_file` *(required)* - path to [cmake-toolchain file](#Cmake-toolchain-file)

**This file is passed via [comand-line opitons](#Comand-line-options) by `--config` option**

## Cmake-toolchain file
This file is needed for cross-compiling. You can read about cmake-toolchain file [here](https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html).

Here is an example of cmake-toolchain file to cross-compiling with *gcc* under *aarch64*:
```cmake
set(CMAKE_SYSTEM_NAME Linux )
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(triple aarch64-linux-gnu )

# This condition and SYSROOT_FLAG variable needs to support sysroot variable from config.
# So, use it if you want this functionality.
if(DEFINED SYSROOT)
	set(SYSROOT_FLAG "--sysroot ${SYSROOT}")
endif()

set(OPT_FLAG "-O0")

set(CMAKE_C_FLAGS "-static ${OPT_FLAG} ${SYSROOT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS_RELEASE "-static ${OPT_FLAG} ${SYSROOT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_CXX_FLAGS "${OPT_FLAG} ${SYSROOT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS_RELEASE "${OPT_FLAG} ${SYSROOT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_C_COMPILER /usr/bin/clang CACHE STRING "" FORCE)
set(CMAKE_C_COMPILER_TARGET ${triple})
set(CMAKE_CXX_COMPILER /usr/bin/clang++ CACHE STRING "" FORCE)
set(CMAKE_CXX_COMPILER_TARGET ${triple})
```
*This example and others for clang and OpenArkCompiler are in the folder `cmake-toolchain`*

**This file is passed via [config file](#Config-file) by `cmake_toolchain_file` variable**

## Test-suite subdirs file
This file is needed to select the tests to be built.

Here is an example of this file:
```
MultiSource/Benchmarks/BitBench/;
MultiSource/Benchmarks/DOE-ProxyApps-C/;
MultiSource/Benchmarks/Fhourstones-3.1/;
MultiSource/Benchmarks/McCat/;
MultiSource/Benchmarks/mediabench/;
MultiSource/Benchmarks/MiBench/;
MultiSource/Benchmarks/Olden/;
MultiSource/Benchmarks/Prolangs-C/;
MultiSource/Benchmarks/Ptrdist/;
MultiSource/Benchmarks/SciMark2-C/;
MultiSource/Benchmarks/Trimaran/;
MultiSource/Benchmarks/TSVC/;
MultiSource/Benchmarks/VersaBench/;

MultiSource/Applications/aha/;
MultiSource/Applications/d/;
MultiSource/Applications/JM/;
MultiSource/Applications/lemon/;
MultiSource/Applications/lua/;
MultiSource/Applications/oggenc/;
MultiSource/Applications/sgefa/;
MultiSource/Applications/SIBsim4/;
MultiSource/Applications/SPASS/;
MultiSource/Applications/spiff/;
MultiSource/Applications/sqlite3/;
MultiSource/Applications/treecc/;
MultiSource/Applications/viterbi/;

SingleSource/Benchmarks/BenchmarkGame/;
SingleSource/Benchmarks/Dhrystone/;
SingleSource/Benchmarks/Linpack/;
SingleSource/Benchmarks/Polybench/;
SingleSource/Benchmarks/Shootout/
```
*This example contains benchmarks that were selected specifically to test the performance of the [OpenArkCompiler](https://gitee.com/openarkcompiler/OpenArkCompiler).*

**Test-suite subdirs file is a list of paths to individual benchmarks separated by `;`.**

You can find 2 files in this repository: *benchmarks_list_all.txt* and *benchmarks_list_select.txt*. *benchmarks_list_all.txt* contents all benchmarks listed above. *benchmarks_list_select.txt* do not contain benchmarks, that [OpenArkCompiler](https://gitee.com/openarkcompiler/OpenArkCompiler) can't compile yet (08/25/2022) (benchmarks: MultiSource/Benchmarks/DOE-ProxyApps-C/RSBench; MultiSource/Applications/sqlite3/; SingleSource/Benchmarks/BenchmarkGame/)  

**This file is passed via [config file](#Config-file) by `test_suite_subdirs_file` variable**

## Running tests with docker
To run tests more easily, it is possible to use a docker container.

### How to run docker container manually:
#### Run container:

`$ sudo docker run --rm -it korostinskiyr/compiler_performance_testing:manual`

<h4 id="Mount-directory"> Mount directory: </h4>

`$ sudo docker run --rm -it type=bind,source=/path/in/host,destination=/path/in/container *CONTAINER NAME*`

*By mounting directories you can pass [config files](#Config-file), pass [test-suite subdirs files](Test-suite-subdirs-file), pass [cmake-toolchain files](#Cmake-toolchain-file), save results, and and much more*

#### Set up OpenArkCompiler:

` $ cd /home/OpenArkCompiler && source build/envsetup.sh arm release`

<h4 id="Run-script"> Run script: </h4>

` $ cd /home/compiler-performance-testing && ./run_llvm_test_suite.py --remote-hostname 255.255.255.255 --remote-username username --remote-password password --other-options ...`

*Be sure to specify remote-hostname, remote-username, remote-password because because these options are not specified in the default `config.ini`*

*By default script use `config.ini` as [config file](#Config-file) and `benchmarks_list_select.txt` as [test-suite subdirs file](Test-suite-subdirs-file). You can change it by passing the required [comand-line options](#Comand-line-options). If you don't want to mount any directory and save the results, but want to see them, specify the `--compare-results` option*

### How to run docker container automatically:

Here you can run container like a script and pass required options to it.

`$ sudo docker run --rm -it korostinskiyr/compiler_performance_testing:automatic --remote-hostname 255.255.255.255 --remote-username username --remote-password password --other-options ...`

Also check how to [Run script](#Run-script) and [Mount directory](#Mount-directory)

## Results

Results are saved in *json* format and can be displayed with [compare tool](https://llvm.org/docs/TestSuiteGuide.html#displaying-and-analyzing-results). Or may be converted to more convenient format, for example *csv*.