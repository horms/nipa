# SPDX-License-Identifier: GPL-2.0
#
# Copyright (C) 2019 Netronome Systems, Inc.

""" OS command running helpers"""

import datetime
import subprocess

import core


class CmdError(Exception):
    """Exception raised for commands which returned non-zero exit code.

    Attributes
    ----------
    cmd : str
        shell command with all its arguments
    retcode : int
        exit code of the command
    stdout : str
        standard output of the command which failed
    stderr : str
        standard output of the command which failed
    """

    def __init__(self, cmd, retcode, stdout, stderr):
        super().__init__(cmd, retcode, stdout, stderr)

        self.cmd = cmd
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr


def cmd_run(cmd, shell=True, include_stderr=False, env=None, pass_fds=()):
    """Run a command.

    Run a command in subprocess and return the stdout;
    optionally return stderr as well as a second value.

    Parameters
    ----------
    cmd : str
        shell command with all its arguments
    shell : bool, optional
        invoke command in a full shell
    include_stderr : bool, optional
        return stderr as a second return value
    env: dict, optional
        additional env variables
    pass_fds : iterable, optional
        pass extra file descriptors to the command

    Raises
    ------
    CmdError
        If command returned non-zero exit code.

    Returns
    -------
    string
        the stdout, optionally stderr as well as a second string value
    """

    process = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env, pass_fds=pass_fds)

    core.log_open_sec("CMD " + process.args)

    stdout, stderr = process.communicate()
    stdout = stdout.decode("utf-8", "ignore")
    stderr = stderr.decode("utf-8", "ignore")
    process.stdout.close()
    process.stderr.close()

    stderr = "\n" + stderr
    if stderr[-1] == "\n":
        stderr = stderr[:-1]

    core.log("RETCODE", process.returncode)
    core.log("STDOUT", stdout)
    core.log("STDERR", stderr)
    core.log("END", datetime.datetime.now().strftime("%H:%M:%S.%f"))
    core.log_end_sec()

    if process.returncode != 0:
        if stderr and stderr[-1] == "\n":
            stderr = stderr[:-1]
        raise CmdError("Command failed: %s" % (process.args, ),
                       process.returncode, stdout, stderr)

    if not include_stderr:
        return stdout
    return stdout, stderr
