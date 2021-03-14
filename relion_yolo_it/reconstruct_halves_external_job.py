#!/usr/bin/env python
"""
External job for running relion_reconstruct on each random half from select_and_split 
External job 
"""

import argparse
import json
import os
import os.path
import shutil
import time

import gemmi


RELION_JOB_FAILURE_FILENAME = "RELION_JOB_EXIT_FAILURE"
RELION_JOB_SUCCESS_FILENAME = "RELION_JOB_EXIT_SUCCESS"


def run_job(project_dir, job_dir, in_dir, starin, args_list):
    parser = argparse.ArgumentParser()
    parser.add_argument("--class_number", dest="class_number")
    parser.add_argument("--mask_diameter", dest="mask_diam")
    parser.add_argument(
        "--j", dest="threads", help="Number of threads to run (ignored)"
    )
    args = parser.parse_args(args_list)
    if not starin.endswith(".star"):
        raise ValueError(
            "Input file for external ReconstructHalves job must end with .star"
        )

    command = "relion_reconstruct"
    split_starin = starin.split(".")
    splitname1 = ""
    splitname2 = ""
    if len(split_starin) == 2:
        splitname1 += split_starin[0] + "_split1." + split_starin[1]
        splitname2 += split_starin[0] + "_split2." + split_starin[1]
    else:
        for substr in split_starin[:-2]:
            splitname1 += substr + "."
            splitname2 += substr + "."
        splitname1 += split_starin[-2] + "_split1." + split_starin[-1]
        splitname2 += split_starin[-2] + "_split2." + split_starin[-1]

    model_half1 = f"3d_half1_model{args.class_number}.mrc"
    model_half2 = f"3d_half2_model{args.class_number}.mrc"
    options = f"--i {os.path.join(in_dir, splitname1)} --o {os.path.join(job_dir, model_half1)} --ctf true --mask_diameter {args.mask_diam}"
    cmdcheck = os.system(command + " " + options)
    if cmdcheck != 0:
        raise Exception(
            f"relion_reconstruct {options} failed in reconstruct_halves External job"
        )

    options = f"--i {os.path.join(in_dir, splitname2)} --o {os.path.join(job_dir, model_half2)} --ctf true --mask_diameter {args.mask_diam}"
    cmdcheck = os.system(command + " " + options)
    if cmdcheck != 0:
        raise Exception(
            f"relion_reconstruct {options} failed in reconstruct_halves External job"
        )


def main():
    """Change to the job working directory, then call run_job()"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_dir", dest="out_dir", help="Output directory name")
    parser.add_argument(
        "--in_dir",
        dest="in_dir",
        help="Directory name where input star files are stored",
    )
    parser.add_argument("--i", dest="starin", help="Input star file name")
    parser.add_argument(
        "--pipeline_control", help="Directory for pipeline control files"
    )
    known_args, other_args = parser.parse_known_args()
    project_dir = os.getcwd()
    os.makedirs(known_args.out_dir, exist_ok=True)
    os.chdir(known_args.out_dir)
    if os.path.isfile(RELION_JOB_FAILURE_FILENAME):
        print(
            " reconstruct_halves_external_job: Removing previous failure indicator file"
        )
        os.remove(RELION_JOB_FAILURE_FILENAME)
    if os.path.isfile(RELION_JOB_SUCCESS_FILENAME):
        print(
            " reconstruct_halves_external_job: Removing previous success indicator file"
        )
        os.remove(RELION_JOB_SUCCESS_FILENAME)
    try:
        os.chdir("../..")
        run_job(
            project_dir,
            known_args.out_dir,
            known_args.in_dir,
            known_args.starin,
            other_args,
        )
    except:
        if os.getcwd() == project_dir:
            os.chdir(known_args.out_dir)
        open(RELION_JOB_FAILURE_FILENAME, "w").close()
        raise
    else:
        if os.getcwd() == project_dir:
            os.chdir(known_args.out_dir)
        open(RELION_JOB_SUCCESS_FILENAME, "w").close()


if __name__ == "__main__":
    main()
