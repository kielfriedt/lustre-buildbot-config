# -*- python -*-
# ex: set syntax=python:

from buildbot.plugins import util
from buildbot.steps.source.gerrit import Gerrit
from buildbot.steps.shell import ShellCommand, Configure, SetPropertyFromCommand
from buildbot.steps.master import SetProperty
from buildbot.steps.transfer import FileUpload, FileDownload, DirectoryUpload
from buildbot.steps.trigger import Trigger
from buildbot.status.results import SUCCESS, FAILURE, SKIPPED, WARNINGS
from buildbot.steps.source.git import Git
import random


def do_step_if_value(step, name, value):
    props = step.build.getProperties()
    if props.hasProperty(name) and props[name] == value:
        return True
    else:
        return False


def do_step_if_not_ubuntu(step):
    return not do_step_if_value(step, 'distro', 'ubuntu')


def hide_if_skipped(results, step):
    return results == SKIPPED


def hide_except_error(results, step):
    return results in (SUCCESS, SKIPPED)


@util.renderer
def NightlyTestSuiteCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    compiler = props.getProperty('compiler')
    compiler_version = props.getProperty(compiler)
    distro = props.getProperty('distro')
    version = props.getProperty('distrover')
    yaml = "day" + str(random.randint(1, 7)) + "_" + \
        compiler + compiler_version + ".yaml"
    args.extend([bb_url + "bb-runspack.sh", 1, yaml, distro + version + "AWS", "spack"])
    return args


@util.renderer
def WeeklyTestSuiteCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    compiler = props.getProperty('compiler')
    compiler_version = props.getProperty(compiler)
    distro = props.getProperty('distro')
    version = props.getProperty('distrover')
    yaml = "all_" + compiler + compiler_version + ".yaml"
    args.extend([bb_url + "bb-runspack.sh", 0, yaml, distro + version + "AWS", "Weekly"])
    return args


@util.renderer
def XSDKNightlyTestSuiteCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    compiler = props.getProperty('compiler')
    compiler_version = props.getProperty(compiler)
    distro = props.getProperty('distro')
    version = props.getProperty('distrover')
    yaml = "xsdk_" + compiler + compiler_version + ".yaml"
    args.extend([bb_url + "bb-runspack.sh", 1, yaml, distro + version + "AWS", "xsdk"])
    return args


@util.renderer
def dependencyCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    args.extend([bb_url + "bb-dependencies.sh"])
    return args

def nightlyTestSuiteFactory(spack_repo):
    """ Generates a build factory for a tarball generating builder.
    Returns:
        BuildFactory: Build factory with steps for generating tarballs.
    """
    bf = util.BuildFactory()

    # update dependencies
    bf.addStep(ShellCommand(
        command=dependencyCommand,
        decodeRC={0: SUCCESS, 1: FAILURE, 2: WARNINGS, 3: SKIPPED},
        haltOnFailure=True,
        logEnviron=False,
        doStepIf=do_step_if_not_ubuntu,
        hideStepIf=hide_if_skipped,
        description=["installing dependencies"],
        descriptionDone=["installed dependencies"],
        workdir="build/spack"))

    # Pull the patch from Gerrit
    bf.addStep(Git(
        repourl=spack_repo,
        workdir="build/spack",
        mode="full",
        method="fresh",
        retry=[60, 60],
        timeout=3600,
        logEnviron=False,
        getDescription=True,
        haltOnFailure=True,
        description=["cloning"],
        descriptionDone=["cloned"]))

    bf.addStep(ShellCommand(
        command=NightlyTestSuiteCommand,
        decodeRC={0: SUCCESS, 1: FAILURE, 2: WARNINGS, 3: SKIPPED},
        haltOnFailure=True,
        logEnviron=False,
        timeout=3600,
        hideStepIf=hide_if_skipped,
        description=["running nightly test-suite"],
        descriptionDone=["running nightly test-suite"],
        workdir="build/spack"))

    return bf

def weeklyTestSuiteFactory(spack_repo):
    """ Generates a build factory for a tarball generating builder.
    Returns:
        BuildFactory: Build factory with steps for generating tarballs.
    """
    bf = util.BuildFactory()

    # update dependencies
    bf.addStep(ShellCommand(
        command=dependencyCommand,
        decodeRC={0 : SUCCESS, 1 : FAILURE, 2 : WARNINGS, 3 : SKIPPED },
        haltOnFailure=True,
        logEnviron=False,
        doStepIf=do_step_if_not_ubuntu,
        hideStepIf=hide_if_skipped,
        description=["installing dependencies"],
        descriptionDone=["installed dependencies"],
        workdir="build/spack"))

    # Pull the patch from Gerrit
    bf.addStep(Git(
        repourl=spack_repo,
        workdir="build/spack",
        mode="full",
        method="fresh",
        retry=[60,60],
        timeout=3600,
        logEnviron=False,
        getDescription=True,
        haltOnFailure=True,
        description=["cloning"],
        descriptionDone=["cloned"]))

    bf.addStep(ShellCommand(
        command=WeeklyTestSuiteCommand,
        decodeRC={0 : SUCCESS, 1 : FAILURE, 2 : WARNINGS, 3 : SKIPPED },
        haltOnFailure=True,
        logEnviron=False,
        timeout=3600,
        hideStepIf=hide_if_skipped,
        description=["running weekly test-suite"],
        descriptionDone=["running weekly test-suite"],
        workdir="build/spack"))

    return bf

def xsdkTestSuiteFactory(spack_repo):
    """ Generates a build factory for a tarball generating builder.
    Returns:
        BuildFactory: Build factory with steps for generating tarballs.
    """
    bf = util.BuildFactory()

    # update dependencies
    bf.addStep(ShellCommand(
        command=dependencyCommand,
        decodeRC={0: SUCCESS, 1: FAILURE, 2: WARNINGS, 3: SKIPPED},
        haltOnFailure=True,
        logEnviron=False,
        doStepIf=do_step_if_not_ubuntu,
        hideStepIf=hide_if_skipped,
        description=["installing dependencies"],
        descriptionDone=["installed dependencies"],
        workdir="build/spack"))

    # Pull the patch from Gerrit
    bf.addStep(Git(
        repourl=spack_repo,
        workdir="build/spack",
        mode="full",
        method="fresh",
        retry=[60, 60],
        timeout=3600,
        logEnviron=False,
        getDescription=True,
        haltOnFailure=True,
        description=["cloning"],
        descriptionDone=["cloned"]))

    bf.addStep(ShellCommand(
        command=XSDKNightlyTestSuiteCommand,
        decodeRC={0: SUCCESS, 1: FAILURE, 2: WARNINGS, 3: SKIPPED},
        haltOnFailure=True,
        logEnviron=False,
        timeout=3600,
        hideStepIf=hide_if_skipped,
        description=["running xsdk test-suite"],
        descriptionDone=["running xsdk test-suite"],
        workdir="build/spack"))

    return bf
