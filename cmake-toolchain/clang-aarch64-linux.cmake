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