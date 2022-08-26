set(CMAKE_SYSTEM_NAME Linux )
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(triple aarch64-linux-gnu )

set(OPT_FLAG "-O2")

set(CMAKE_C_FLAGS "-static --maple-toolchain --ignore-unknown-options ${OPT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_C_FLAGS "-static --maple-toolchain --ignore-unknown-options ${OPT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_CXX_FLAGS "${OPT_FLAG}" CACHE STRING "" FORCE)
set(CMAKE_CXX_FLAGS_RELEASE "${OPT_FLAG}" CACHE STRING "" FORCE)

set(CMAKE_C_COMPILER maple CACHE STRING "" FORCE)
set(CMAKE_CXX_COMPILER g++ CACHE STRING "" FORCE)