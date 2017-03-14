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

def hide_if_skipped(results, step):
    return results == SKIPPED

def hide_except_error(results, step):
    return results in (SUCCESS, SKIPPED)

@util.renderer
def curlCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    args.extend([bb_url + "bb-sendreport.sh"])
    return args

@util.renderer
def runyamlCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    args.extend([bb_url + "bb-runspack.sh"])
    return args
@util.renderer
def dependencyCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    args.extend([bb_url + "bb-dependencies.sh"])
    return args

def xsdkTestSuiteFactory(spack_repo):
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
        command=runyamlCommand,
        decodeRC={0 : SUCCESS, 1 : FAILURE, 2 : WARNINGS, 3 : SKIPPED },
        haltOnFailure=True,
        logEnviron=False,
        hideStepIf=hide_if_skipped,
        description=["running test-suite"],
        descriptionDone=["running test-suite"],
        workdir="build/spack"))


    # send reports
    bf.addStep(ShellCommand(
        command=curlCommand,
        decodeRC={0 : SUCCESS, 1 : FAILURE, 2 : WARNINGS, 3 : SKIPPED },
        haltOnFailure=True,
        logEnviron=False,
        lazylogfiles=True,
        alwaysRun=True,
        description=["Sending output to cdash"],
        descriptionDone=["Sending output to cdash"],
        workdir="build/spack"))

    # Cleanup
    bf.addStep(ShellCommand(
        workdir="build",
        command=["sh", "-c", "rm -rvf *"],
        haltOnFailure=True,
        logEnviron=False,
        lazylogfiles=True,
        alwaysRun=True,
        description=["cleaning up"],
        descriptionDone=["clean up"]))

    return bf
'''
def createPackageBuildFactory():
    """ Generates a build factory for a lustre tarball builder.
    Returns:
        BuildFactory: Build factory with steps for a lustre tarball builder.
    """
    bf = util.BuildFactory()

    # download our tarball and extract it
    bf.addStep(FileDownload(
        workdir="build/spack",
        slavedest=util.Interpolate("%(prop:tarball)s"),
        mastersrc=tarballMasterDest))

    bf.addStep(ShellCommand(
        workdir="build/spack",
        command=["tar", "-xvzf", util.Interpolate("%(prop:tarball)s"), "--strip-components=1"],
        haltOnFailure=True,
        logEnviron=False,
        lazylogfiles=True,
        description=["extracting tarball"],
        descriptionDone=["extract tarball"]))

    # update dependencies
    bf.addStep(ShellCommand(
        command=dependencyCommand,
        decodeRC={0 : SUCCESS, 1 : FAILURE, 2 : WARNINGS, 3 : SKIPPED },
        haltOnFailure=True,
        logEnviron=False,
        doStepIf=do_step_installdeps,
        hideStepIf=hide_if_skipped,
        description=["installing dependencies"],
        descriptionDone=["installed dependencies"]))

    # build spl and zfs if necessary
    bf.addStep(ShellCommand(
        command=buildzfsCommand,
        decodeRC={0 : SUCCESS, 1 : FAILURE, 2 : WARNINGS, 3 : SKIPPED },
        haltOnFailure=True,
        logEnviron=False,
        doStepIf=do_step_zfs,
        hideStepIf=hide_if_skipped,
        description=["building spl and zfs"],
        descriptionDone=["built spl and zfs"]))

    # Build Lustre 
    bf.addStep(ShellCommand(
        workdir="build/spack",
        command=configureCmd,
        haltOnFailure=True,
        logEnviron=False,
        hideStepIf=hide_if_skipped,
        lazylogfiles=True,
        description=["configuring lustre"],
        descriptionDone=["configure lustre"]))

    bf.addStep(ShellCommand(
        workdir="build/spack",
        command=makeCmd,
        haltOnFailure=True,
        logEnviron=False,
        hideStepIf=hide_if_skipped,
        lazylogfiles=True,
        description=["making lustre"],
        descriptionDone=["make lustre"]))

    # Build Products
    bf.addStep(ShellCommand(
        workdir="build/spack",
        command=collectProductsCmd,
        haltOnFailure=True,
        logEnviron=False,
        doStepIf=do_step_collectpacks,
        hideStepIf=hide_if_skipped,
        lazylogfiles=True,
        description=["collect deliverables"],
        descriptionDone=["collected deliverables"]))

    # Build repo
    bf.addStep(ShellCommand(
        workdir="build/spack/deliverables",
        command=buildRepoCmd,
        haltOnFailure=True,
        logEnviron=False,
        doStepIf=do_step_buildrepo,
        hideStepIf=hide_if_skipped,
        lazylogfiles=True,
        description=["building repo"],
        descriptionDone=["build repo"]))



    

    return bf

'''