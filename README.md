# llvm-test-suite build and run ssh script

This python script can help to build and run [llvm-test-suite](https://llvm.org/docs/TestSuiteGuide.html) on board easily.

###### Table of contents

1. [Requirements for proper work](#Requirements-for-proper-work)
2. [Comand-line options](#Comand-line-options)
3. [Config file](#Config-file)
4. [Cmake-toolchain file](#Cmake-toolchain-file)
5. [Test-suite subdirs file](#Test-suite-subdirs-file)
6. [Results](#Results)

## Requirements for proper work

- Install [llvm-lit](https://llvm.org/docs/TestSuiteGuide.html) runner
- Check out the [test-suite](https://github.com/llvm/llvm-test-suite.git) module
- Prepare a [cmake-toolchain file](#Cmake-toolchain-file)
- Prepare a [config file](#Config-file)
- Prepare a [file with test-suite subdirs list](#Test-suite-subdirs-file)
- Connect to the board via ssh **using the ssh key** if you want to sync or run tests

## Comand-line options

There is some useful comand-line options:

- `-h, --help` - show help message and exit
- `--config CONFIG` *(required)* - config file
- `--build-only` - only build tests
	- `--no-rsync` -  disable synchronization with board (can be used only with --build-only flag)
- `--run-only` - only run tests
- `--nruns NRUNS` (*default = 1*) - number of tests runs (natural number)

*Important note: tests can only be run if they have been built and synced with the board before. Otherwise it will cause errors.*

## Config file

Config file - is a file with required variables. It can be passed to the script with option `--config CONFIG`.

Structure of config file:
```
[PATHS]
test_suite_path = /path/to/test-suite
lit_path = /path/to/llvm-lit

[REMOTE HOST]
remote_hostname = 255.255.255.255
remote_username = username

[MULTITHREADING]
build_threads = 4
run_threads = 4

[TOOLCHAINS]
toolchains_number = 3

[TOOLCHAIN 1]
toolchain_name = gcc-O0
build_path = /path/to/build/directory
cmake_toolchain_file = cmake-toolchain/gcc
test_suite_subdirs_file = path/to/file/with/test-suite/subdirs/list
res_file = /path/to/file/with/test/results.json

[TOOLCHAIN 2]
...

[TOOLCHAIN 3]
...
```
*You can just copy it and change necessary values*

Meaning of variables:

**[PATHS]**
- `build_path` *(required)* - path to build directory (tests will be compiled there)
*Important note: use build directory only into `/home/` directory*
- `test_suite_path` *(required)* - path to directory with [test-suite](https://github.com/llvm/llvm-test-suite.git) sources
- `lit_path` *(required)* - path to [llvm-lit](https://llvm.org/docs/TestSuiteGuide.html) runner tool

*Use only absolute paths*

**FILES**
- `cmake_toolchain_file` *(required)* - path to [cmake-toolchain file](#Cmake-toolchain-file)
- `res_file` *(default = "result.json")* - path test results file in *json* format
- `test_suite_subdirs_file` *(default = [runs all tests])* - path to [file with test-suite subdirs list](#Test-suite-subdirs-file)

**REMOTE HOST**
- `remote_hostname` *(required)* - IP adress of the board
- `remote_username` *(required)* - board user name

**MULTITHREADING**
- `build_threads` *(default = 1)* - the number of threads that are used to build tests
- `run_threads` *(default = 1)* - the number of threads that are used to run tests

**This file is passed via [comand-line opitons](#Comand-line-options) by `--config` option**

## Cmake-toolchain file
This file is needed for cross-compiling. You can read about cmake-toolchain file [here](https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html).

Here is an example of cmake-toolchain file to cross-compiling with *gcc* under *aarch64*:
```
set(CMAKE_SYSTEM_NAME Linux )
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(triple aarch64-linux-gnu )

set(OPT_FLAG "-O0")

set(CMAKE_C_FLAGS "-static ${OPT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS_RELEASE "-static ${OPT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_CXX_FLAGS "${OPT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS_RELEASE "${OPT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_C_COMPILER /usr/bin/aarch64-linux-gnu-gcc CACHE STRING "" FORCE)
set(CMAKE_C_COMPILER_TARGET ${triple})
set(CMAKE_CXX_COMPILER /usr/bin/aarch64-linux-gnu-g++ CACHE STRING "" FORCE)
set(CMAKE_C_COMPILER_TARGET ${triple})
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

Test-suite subdirs file is a list of paths to individual benchmarks separated by `;`. 

**This file is passed via [config file](#Config-file) by `test_suite_subdirs_file` variable**

## Results

Results are saved in *json* format and can be displayed with [compare tool](https://llvm.org/docs/TestSuiteGuide.html#displaying-and-analyzing-results). Or may be converted to more convenient format, for example *csv*.