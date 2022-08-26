#!/usr/bin/env python3

import sys
import os


def run_llvm_test_suite_cmd():
	run_llvm_test_suite_cmd = "cd /home/compiler-performance-testing && \
		./run_llvm_test_suite.py "
	for i in range (1, len(sys.argv)):
		run_llvm_test_suite_cmd += sys.argv[i] + " "
	return  run_llvm_test_suite_cmd


def run_script():
	setup_openark_cmd = "cd /home/OpenArkCompiler && \
		source build/envsetup.sh arm release"
	run_script_cmd = "echo '\nSetting up OpenArkCompiler\n'" + " && "\
					 + setup_openark_cmd + " && " \
					 + "echo '\nRunning run_llvm_test_suite.py\n'" + " && " \
					 + run_llvm_test_suite_cmd()
	os.system("/bin/bash -c \"" + run_script_cmd + "\"")


def main():
	run_script()

if __name__ == "__main__":
    main()