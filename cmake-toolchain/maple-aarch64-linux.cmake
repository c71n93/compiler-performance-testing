set(CMAKE_SYSTEM_NAME Linux )
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(triple aarch64-linux-gnu )

set(OPT_FLAG "-O2")

set(CMAKE_C_FLAGS "-static --no-maple-phase ${OPT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS "-static --no-maple-phase ${OPT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_CXX_FLAGS "${OPT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS_RELEASE "${OPT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_C_COMPILER /home/roman/CS/OpenArkCompiler/output/aarch64-clang-release/bin//maple CACHE STRING "" FORCE)
set(CMAKE_CXX_COMPILER g++ CACHE STRING "" FORCE)