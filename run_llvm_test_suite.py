#!/usr/bin/env python

#TODO: stop script if error is occured while building
#TODO: stop script if error is occured while compiling
#TODO: stop script if error is occured while syncing

import sys
import os
import paramiko
import configparser
import argparse
import re


test_suite_path   = ""
lit_path 		  = ""
remote_hostname   = ""
remote_username   = ""
build_threads 	  = 1
run_threads 	  = 1
toolchains_number = 1
toolchains_dict   = {}


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


def get_values_from_config(config_file): #TODO: use config.get()
	global test_suite_path, lit_path, remote_hostname, remote_username, \
		   build_threads, run_threads, toolchains_number, toolchains_dict

	config = configparser.ConfigParser()
	config.read(config_file)

	if 'MULTITHREADING' in config:
		if 'build_threads' in config['MULTITHREADING']:
			build_threads = config['MULTITHREADING']['build_threads']
		if 'run_threads' in config['MULTITHREADING']:
			run_threads = config['MULTITHREADING']['run_threads']
	if 'TOOLCHAINS' in config:
		if 'toolchains_number' in config['TOOLCHAINS']:
			toolchains_number = int(config['TOOLCHAINS']['toolchains_number'])
	test_suite_path = config['PATHS']['test_suite_path']
	lit_path 		= config['PATHS']['lit_path']
	remote_hostname = config['REMOTE HOST']['remote_hostname']
	remote_username = config['REMOTE HOST']['remote_username']

	for i in range(1, toolchains_number + 1):
		toolchain_section_name = "TOOLCHAIN " + str(i)
		if toolchain_section_name not in config:
			print("config: error: wrong 'toolchains_number': there is no", toolchain_section_name)
			exit(0)
		toolchains_dict.update({toolchain_section_name: config[toolchain_section_name]})
		if 'toolchain_name' not in config[toolchain_section_name]:
			toolchains_dict[toolchain_section_name].update({'toolchain_name': toolchain_section_name})
		if 'test_suite_subdirs_file' in config[toolchain_section_name]:
			test_suite_subdirs = \
				get_test_suite_subdirs(config[toolchain_section_name]['test_suite_subdirs_file'])
			toolchains_dict[toolchain_section_name].update({'test_suite_subdirs': test_suite_subdirs})
		else:
			toolchains_dict[toolchain_section_name].update({'test_suite_subdirs': 'default'})
		if 'res_file' in config[toolchain_section_name]:
			res_file = config[toolchain_section_name]['res_file']
			toolchains_dict[toolchain_section_name].update({'res_file': res_file})
		else:
			toolchains_dict[toolchain_section_name].update({'res_file': 'default'})


def get_test_suite_subdirs(subdirs_filename):
	subdirs_file = open(subdirs_filename, "r")
	test_suite_subdirs = subdirs_file.read()
	test_suite_subdirs = '"' + re.sub(r"\s+", "", test_suite_subdirs) + '"'	
	subdirs_file.close()
	return test_suite_subdirs


def build_tests(build_path, cmake_toolchain_file, test_suite_subdirs, test_suite_path, 
				remote_host, build_threads):
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
	client.exec_command("sudo mkdir -p -m=777 " + \
						get_start_of_build_dir(build_path))
	os.system("cd " + build_path + " && " + "ninja rsync")


def get_start_of_build_dir(build_path): #TODO: decide how to fix this "костыль"
	splited_path = build_path.split("/", 3)
	if (splited_path[0] == "~"):
		print("error: use only absolute paths for 'build_path'")
		exit()
	start_build_dir = ""
	for i in range(0, 3):
		start_build_dir += splited_path[i] + "/"
	return start_build_dir

def lit_run(build_path, res_file, lit_path, run_threads, nruns):
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


def get_res_file(toolchain_name, res_file):
	if res_file == 'default':
		return toolchain_name.replace(" ", "-") + ".json"
	else:
		return res_file


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
		for toolchain_section_name in toolchains_dict.keys():
			toolchain_section = toolchains_dict[toolchain_section_name]
			print("\nStart building ", '"', toolchain_section["toolchain_name"], '"', ":",
				  sep = "", end = "\n\n")
			build_tests(toolchain_section["build_path"],
				toolchain_section["cmake_toolchain_file"],
				toolchain_section["test_suite_subdirs"],
				test_suite_path, remote_username + "@" + remote_hostname,
				build_threads)
	if (not args.no_rsync):
		for toolchain_section_name in toolchains_dict.keys():
			toolchain_section = toolchains_dict[toolchain_section_name]
			print("\nStart synchronization ", '"', toolchain_section["toolchain_name"], '"', ":",
				  sep = "", end = "\n\n")
			sync_build_dir_with_board(remote_hostname, remote_username,
				toolchain_section["build_path"])
	if (not args.build_only):
		for toolchain_section_name in toolchains_dict.keys():
			toolchain_section = toolchains_dict[toolchain_section_name]
			print("\nStart running ", '"', toolchain_section["toolchain_name"], '"', ":",
				  sep = "", end = "\n\n")
			lit_run (toolchain_section["build_path"],
				get_res_file(toolchain_section["toolchain_name"],
					toolchain_section["res_file"]),
				lit_path, run_threads,
				args.nruns)

if __name__ == '__main__':
    main()