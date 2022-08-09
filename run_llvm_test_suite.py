#!/usr/bin/env python

import sys
import os
import paramiko
import configparser
import argparse
import re


build_path 			 		= ""
test_suite_path 	 		= ""
lit_path 			 		= ""
remote_hostname 	 		= ""
remote_username 	 		= ""
build_threads 		 		= 1
run_threads 		 		= 1
cmake_toolchain_files_list 	= ""
res_file 			 		= "result.json"
test_suite_subdirs_file 	= ""
test_suite_subdirs 	 		= "default"


def check_args(args):
	if (args.nruns < 1):
		print("options: error: number of runs can be only natural number")
		exit()
	if (not args.build_only and args.no_rsync):
		print("options: error: cannot run tests with no rsync", end="")
		print(" (use --no-rsync only with --build-only flag)")
		exit()
	if (args.build_only and args.run_only):
		print("options: error: conflicting options")
		print("(--build_only and --run_only)")
		exit()


def get_values_from_config(config_file):
	global build_path, test_suite_path, lit_path, remote_hostname, \
		   remote_username, build_threads, run_threads, cmake_toolchain_file, \
		   res_file, test_suite_subdirs_file, test_suite_subdirs

	config = configparser.ConfigParser()
	config.read(config_file)

	if 'MULTITHREADING' in config:
		if 'build_threads' in config['MULTITHREADING']:
			build_threads = config['MULTITHREADING']['build_threads']
		if 'run_threads' in config['MULTITHREADING']:
			build_threads = config['MULTITHREADING']['run_threads']
	if 'res_file' in config['FILES']:
		res_file = config['FILES']['res_file']
	if 'test_suite_subdirs_file' in config['FILES']:
		test_suite_subdirs_file = config['FILES']['test_suite_subdirs_file']
		test_suite_subdirs 	 	= get_test_suite_subdirs(test_suite_subdirs_file)

	build_path 			 	= config['PATHS']['build_path']
	test_suite_path 	 	= config['PATHS']['test_suite_path']
	lit_path 			 	= config['PATHS']['lit_path']
	remote_hostname 	 	= config['REMOTE HOST']['remote_hostname']
	remote_username 	 	= config['REMOTE HOST']['remote_username']
	cmake_toolchain_file 	= config['FILES']['cmake_toolchain_file']


def get_test_suite_subdirs(subdirs_filename):
	subdirs_file = open(subdirs_filename, "r")
	test_suite_subdirs = subdirs_file.read()
	test_suite_subdirs = '"' + re.sub(r"\s+", "", test_suite_subdirs) + '"'	
	subdirs_file.close()
	return test_suite_subdirs


def build_tests(build_path, test_suite_path, cmake_toolchain_file,
				remote_host, test_suite_subdirs,
				build_threads):
	cmake_defines = "-DTEST_SUITE_BENCHMARKING_ONLY=ON" \
				  + " -DMULTITHREADED_BUILD=" + str(build_threads) \
				  + " -DTEST_SUITE_REMOTE_HOST=" + remote_host \
				  + " -DCMAKE_TOOLCHAIN_FILE:FILEPATH=" + cmake_toolchain_file
	if (test_suite_subdirs != "default"):
		cmake_defines += " -DTEST_SUITE_SUBDIRS=" + test_suite_subdirs
	cmake_options = "-G Ninja" \
				  + " " + cmake_defines \
				  + " " + test_suite_path

	os.system("mkdir -p " + build_path)
	cd_to_build_path = "cd " + build_path
	os.system(cd_to_build_path + " && " + "cmake " + cmake_options)
	os.system(cd_to_build_path + " && " + "ninja")


def sync_build_dir_with_board(remote_hostname, remote_username, build_path):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(hostname = remote_hostname, username = remote_username)
	client.exec_command("sudo mkdir -p -m=777 " + get_start_of_build_dir(build_path))
	os.system("cd " + build_path + " && " + "ninja rsync")


def get_start_of_build_dir(build_path):
	splited_path = build_path.split("/", 3)
	if (splited_path[0] == "~"):
		print("error: use only absolute paths for 'build_path'")
		exit()
	start_build_dir = ""
	for i in range(0, 3):
		start_build_dir += splited_path[i] + "/"
	return start_build_dir

def lit_run(build_path, lit_path, res_file, run_threads, nruns):
	if (nruns == 1):
		single_lit_run(build_path, lit_path, res_file, run_threads)
		return
	for i in range(1, nruns + 1):
		single_lit_run(build_path, lit_path, make_nres_filename(res_file, i),
					   run_threads)


def single_lit_run(build_path, lit_path, res_file, run_threads):
	lit_options = "-vv -j " + str(run_threads) + " -o " \
				+ res_file + " " + build_path

	os.system(lit_path + " " + lit_options)


def make_nres_filename(res_file, n):
	dot_last_place = res_file.rfind(".")
	return res_file[:dot_last_place] + f"[{n}]" + res_file[dot_last_place:]


def main():
	parser = argparse.ArgumentParser("options")
	parser.add_argument("--conf", dest="config", required=True, 
							 help="config file")
	parser.add_argument("--nruns", dest="nruns", type=int, default=1, 
							 help="number of runs (natural number)")
	parser.add_argument("--build-only", dest="build_only", 
							 action="store_true", help="only build tests")
	parser.add_argument("--no-rsync", dest="no_rsync", action="store_true",
							 help="disable synchronization with board \
(can be used only with --build-only flag)")
	parser.add_argument("--run-only", dest="run_only", action="store_true",
							 help="only run tests")
	args = parser.parse_args()
	check_args(args)

	get_values_from_config(args.config)

	if (not args.run_only):
		build_tests(build_path, test_suite_path, cmake_toolchain_file,
					remote_username + "@" + remote_hostname, test_suite_subdirs,
					build_threads)
	if (not args.no_rsync):
		sync_build_dir_with_board(remote_hostname, remote_username, build_path)
	if (not args.build_only):
		lit_run (build_path, lit_path, res_file, run_threads, args.nruns)

if __name__ == '__main__':
    main()