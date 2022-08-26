#!/usr/bin/env python3

import sys
import os
import paramiko
import configparser
import argparse
import re


test_suite_path		= ""
lit_path			= ""
builds_dir			= ""
sysroot_path		= "default"
test_suite_subdirs 	= "default"
results_path		= "default"
remote_hostname		= "default"
remote_username		= "default"
remote_password		= "default"
build_threads		= 1
run_threads			= 1
toolchains_dict		= {}


def check_args(args):
	if (args.nruns < 1):
		print("options: error: number of runs can be only natural number")
		exit(1)
	if (not args.build_only and args.no_rsync):
		print("options: error: cannot run tests with no rsync", end="")
		print(" (use --no-rsync only with --build-only flag)")
		exit(1)
	if (args.build_only and args.run_only):
		print("options: error: conflicting options")
		print("(--build_only and --run_only)")
		exit(1)


#this function use global variables
def get_values_from_config(config_file): #TODO: use config.get()
	global test_suite_path, lit_path, remote_hostname, remote_username, \
		build_threads, run_threads, toolchains_dict, test_suite_subdirs, \
		builds_dir, sysroot_path, results_path, remote_password

	config = configparser.ConfigParser()
	config.read(config_file)

	if "MULTITHREADING" in config:
		if "build_threads" in config["MULTITHREADING"]:
			build_threads = config["MULTITHREADING"]["build_threads"]
		if "run_threads" in config['MULTITHREADING']:
			run_threads = config["MULTITHREADING"]["run_threads"]
	if "sysroot_path" in config["PATHS AND FILES"]:
		sysroot_path = config["PATHS AND FILES"]["sysroot_path"]
	if "test_suite_subdirs_file" in config["PATHS AND FILES"]:
		test_suite_subdirs = get_test_suite_subdirs(
			config["PATHS AND FILES"]["test_suite_subdirs_file"])
	if "results_path" in config["PATHS AND FILES"]:
		results_path = config["PATHS AND FILES"]["results_path"]
	if "remote_hostname" in config["REMOTE HOST"]:
		remote_hostname = config["REMOTE HOST"]["remote_hostname"]
	if "remote_username" in config["REMOTE HOST"]:
		remote_username = config["REMOTE HOST"]["remote_username"]
	if "remote_password" in config["REMOTE HOST"]:
		remote_password = config["REMOTE HOST"]["remote_password"]
	test_suite_path = config["PATHS AND FILES"]["test_suite_path"]
	lit_path		= config["PATHS AND FILES"]["lit_path"]
	builds_dir		= config["PATHS AND FILES"]["builds_dir"]

	toolchain_section_name = "TOOLCHAIN 1"
	section_num = 1
	if toolchain_section_name not in config:
		print("config: error: there must be at least one [TOOLCHAIN 1] section")
		exit(1)
	while toolchain_section_name in config:
		toolchains_dict.update({toolchain_section_name: 
			config[toolchain_section_name]})
		toolchain_section = toolchains_dict[toolchain_section_name]
		toolchain_section["cmake_toolchain_file"] = os.path.abspath(
			config[toolchain_section_name]["cmake_toolchain_file"])
		if "toolchain_name" not in config[toolchain_section_name]:
			toolchain_name = \
				get_toolchain_name(toolchain_section["cmake_toolchain_file"])
			toolchain_section.update({'toolchain_name': toolchain_name})
		if "build_path" not in config[toolchain_section_name]:
			build_path = builds_dir + "/" + toolchain_section["toolchain_name"]
			toolchain_section.update({"build_path": build_path})
		toolchain_section.update({"res_file": get_res_file(
			toolchain_section["toolchain_name"], results_path)})
		section_num += 1
		toolchain_section_name = toolchain_section_name[:-1] + str(section_num)


def get_test_suite_subdirs(subdirs_filename):
	subdirs_file = open(subdirs_filename, "r")
	test_suite_subdirs = subdirs_file.read()
	test_suite_subdirs = '"' + re.sub(r"\s+", "", test_suite_subdirs) + '"'	
	subdirs_file.close()
	return test_suite_subdirs


def get_toolchain_name(cmake_toolchain_file):
	dot_last_place = cmake_toolchain_file.rfind(".")
	slash_last_place = cmake_toolchain_file.rfind("/")
	return cmake_toolchain_file[slash_last_place + 1:dot_last_place]


def get_res_file(toolchain_name, results_path):
	result_filename = toolchain_name.replace(" ", "-") + ".json"
	if results_path == "default":
		return result_filename
	else:
		return results_path + "/" + result_filename


#this function use global variables
def build_all_toolchains():
	for toolchain_section_name in toolchains_dict.keys():
		toolchain_section = toolchains_dict[toolchain_section_name]
		print("\nStart building ", '"', toolchain_section["toolchain_name"],
			'"', ":", sep = "", end = "\n\n")
		build_single_toolchain(toolchain_section["build_path"],
			toolchain_section["cmake_toolchain_file"],
			test_suite_subdirs, test_suite_path,
			remote_username + "@" + remote_hostname, build_threads)


def build_single_toolchain(build_path, cmake_toolchain_file, 
								test_suite_subdirs, test_suite_path, 
								remote_host, build_threads):
	cmake_defines = "-DTEST_SUITE_BENCHMARKING_ONLY=ON" \
				  + " -DTEST_SUITE_COLLECT_CODE_SIZE=OFF" \
				  + " -DMULTITHREADED_BUILD=" + str(build_threads) \
				  + " -DTEST_SUITE_REMOTE_HOST=" + remote_host \
				  + " -DCMAKE_TOOLCHAIN_FILE:FILEPATH=" + cmake_toolchain_file
	if (test_suite_subdirs != "default"):
		cmake_defines += " -DTEST_SUITE_SUBDIRS=" + test_suite_subdirs
	if (sysroot_path != "default"):
		cmake_defines += " -DSYSROOT=" + sysroot_path
	cmake_options = "-G Ninja" \
				  + " " + cmake_defines \
				  + " " + test_suite_path

	os.system("mkdir -p " + build_path)
	cd_to_build_path = "cd " + build_path
	os.system(cd_to_build_path + " && " + "cmake " + cmake_options)
	os.system(cd_to_build_path + " && " + "ninja")


#this function use global variables
def sync_all_toolchains_build_dirs_with_board():
	for toolchain_section_name in toolchains_dict.keys():
		toolchain_section = toolchains_dict[toolchain_section_name]
		print("\nStart synchronization ", '"', 
			toolchain_section["toolchain_name"],'"', ":", sep = "", 
			end = "\n\n")
		sync_single_toolchain_build_dir_with_board(remote_hostname,
			remote_username, remote_password, toolchain_section["build_path"])


def sync_single_toolchain_build_dir_with_board(remote_hostname, remote_username,
											   remote_password, build_path):
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(hostname = remote_hostname, username = remote_username)
	client.exec_command("echo '" + remote_password + \
						"' | sudo mkdir -p -m=777 " + \
						get_start_of_build_dir(build_path))
	os.system("cd " + build_path + " && " + "ninja rsync")


def get_start_of_build_dir(build_path): #TODO: decide how to fix this
	splited_path = build_path.split("/", 3)
	if (splited_path[0] == "~"):
		print("error: use only absolute paths for 'build_path'")
		exit(1)
	start_build_dir = ""
	for i in range(0, 3):
		start_build_dir += splited_path[i] + "/"
	return start_build_dir


#this function use global variables
def lit_run_all_toolchains(nruns):
	for toolchain_section_name in toolchains_dict.keys():
		toolchain_section = toolchains_dict[toolchain_section_name]
		print("\nStart running ", '"', toolchain_section["toolchain_name"],
			'"', ":", sep = "", end = "\n\n")
		lit_run_single_tooclchain (toolchain_section["build_path"],
			toolchain_section["res_file"], lit_path, run_threads, 
			nruns)


def lit_run_single_tooclchain(build_path, res_file, lit_path, run_threads,
							  nruns):
	if (nruns == 1):
		single_lit_run(build_path, lit_path, res_file, run_threads)
		return
	for i in range(1, nruns + 1):
		print(f"\n[{i}]", end = "\n\n")
		single_lit_run(build_path, lit_path, make_nres_filename(res_file, i),
					   run_threads)


def single_lit_run(build_path, lit_path, res_file, run_threads):
	lit_options = "-vv -j " + str(run_threads) \
		+ " -o " + res_file + " " + build_path

	os.system(lit_path + " " + lit_options)


def make_nres_filename(res_file, n):
	dot_last_place = res_file.rfind(".")
	return res_file[:dot_last_place] + f"[{n}]" + res_file[dot_last_place:]


#this function use global variables
def compare_all_results(nruns):
	print("\nStart comparing results:", end = "\n\n")
	compare_cmd = test_suite_path + "/utils/compare.py -a -f "
	for toolchain_section_name in toolchains_dict.keys():
		toolchain_section = toolchains_dict[toolchain_section_name]
		if nruns == 1:
			compare_cmd += toolchain_section["res_file"] + " "
		else:
			for i in range(1, nruns + 1):
				compare_cmd += \
					make_nres_filename(toolchain_section["res_file"], i) + " "

	if results_path == "default":
		os.system(compare_cmd)
	else:
		os.system("cd " + results_path + " && " + compare_cmd)


def get_arg_parser():
	parser = argparse.ArgumentParser("options")
	parser.add_argument("--config", dest="config", default="config.ini",
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
	parser.add_argument("--compare-results", dest="compare_results",
						action="store_true", help="print results comparison")
	parser.add_argument("--debug-config", dest="debug_config",
						action="store_true", help="only shows config variables \
						and exit")
	parser.add_argument("--remote-hostname", dest="remote_hostname",
						# action = "store_const", const="not specified",
						help="IP adress of the board")
	parser.add_argument("--remote-username", dest="remote_username",
						# action = "store_const", const="not specified",
						help="board user name")
	parser.add_argument("--remote-password", dest="remote_password",
						# action = "store_const", const="not specified",
						help="board password")
	return parser


#this function use global variables
def print_config_variables():
	print("test_suite_path =", test_suite_path)
	print("lit_path =", lit_path)
	print("builds_dir =", builds_dir)
	print("sysroot_path =", sysroot_path)
	print("test_suite_subdirs =", test_suite_subdirs)
	print("results_path =", results_path)
	print("remote_hostname =", remote_hostname)
	print("remote_username =", remote_username)
	print("remote_password =", remote_password)
	print("build_threads =", build_threads)
	print("run_threads =", run_threads)
	for toolchain_section_name in toolchains_dict.keys():
		toolchain_section = toolchains_dict[toolchain_section_name]
		print("\n", toolchain_section_name, ":", sep = "")
		for toolchains_attribute_name in toolchain_section.keys():
			toolchains_attribute = toolchain_section[toolchains_attribute_name]
			print("\t", toolchains_attribute_name, " = ", toolchains_attribute,
				sep = "")


#this function use global variables
def setup_ssh_key_connection():
	print("\nSetting up ssh key connection:", end = "\n\n")
	os.system("sshpass -p " + remote_password \
		+ " ssh -o StrictHostKeyChecking=no " \
		+ remote_username + "@" + remote_hostname + " :")
	os.system("sshpass -p " + remote_password + " ssh-copy-id -f "\
		+ remote_username + "@" + remote_hostname)


#this function use global variables
def make_results_path_dir():
	if results_path != "default":
		os.system("mkdir -p " + results_path)


#this function use global variables
def setup_remote_host_information(args):
	global remote_hostname, remote_username, remote_password
	if args.remote_hostname is not None:
		remote_hostname = args.remote_hostname
	if args.remote_username is not None:
		remote_username = args.remote_username
	if args.remote_password is not None:
		remote_password = args.remote_password

	error_code = 0
	if remote_hostname == "default":
		print("options: error: remote hostname must be specified")
		error_code = 1
	if remote_username == "default":
		print("options: error: remote username must be specified")
		error_code = 1
	if remote_password == "default":
		print("options: error: remote password must be specified")
		error_code = 1
	if error_code == 1:
		exit(1)


def main():
	parser = get_arg_parser()
	args = parser.parse_args()
	check_args(args)

	get_values_from_config(args.config)
	setup_remote_host_information(args)

	if (args.debug_config):
		print_config_variables()
		exit(0)
	if (not args.run_only):
		build_all_toolchains()
	if (not args.no_rsync):
		setup_ssh_key_connection()
		sync_all_toolchains_build_dirs_with_board()
	if (not args.build_only):
		setup_ssh_key_connection()
		make_results_path_dir()
		lit_run_all_toolchains(args.nruns)
	if (args.compare_results):
		compare_all_results(args.nruns)

if __name__ == "__main__":
    main()