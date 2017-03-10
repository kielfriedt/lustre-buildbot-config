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


def hide_if_skipped(results, step):
    return results == SKIPPED

def hide_except_error(results, step):
    return results in (SUCCESS, SKIPPED)

@util.renderer
def dependencyCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    args.extend([bb_url + "bb-dependencies.sh"])
    return args

@util.renderer
def buildzfsCommand(props):
    args = ["runurl"]
    bb_url = props.getProperty('bburl')
    args.extend([bb_url + "bb-build-zfs-pkg.sh"])

    spltag = props.getProperty('spltag')
    if spltag:
        args.extend(["-s", spltag])

    zfstag = props.getProperty('zfstag')
    if zfstag:
        args.extend(["-z", zfstag])

    return args

@util.renderer
def configureCmd(props):
    args = ["./configure"]
    style = props.getProperty('buildstyle')

    if style == "deb" or style == "rpm":
        with_zfs = props.getProperty('withzfs')
        if with_zfs and with_zfs == "yes":
            args.extend(["--with-zfs"])
        else:
            args.extend(["--without-zfs"])

        with_ldiskfs = props.getProperty('withldiskfs')
        if with_ldiskfs and with_ldiskfs == "yes":
            args.extend(["--enable-ldiskfs"])
        else:
            args.extend(["--disable-ldiskfs"])

    return args

@util.renderer
def makeCmd(props):
    args = ["sh", "-c"]
    style = props.getProperty('buildstyle')

    if style == "deb":
        args.extend(["make -j$(nproc) debs"])
    elif style == "rpm":
        args.extend(["make -j$(nproc) rpms"])
    else:
        args.extend(["make -j$(nproc)"])

    return args

@util.renderer
def collectProductsCmd(props):
    # put all binaries into a deliverables folder so DirectoryUpload can be used
    args = ["sh", "-c"]
    style = props.getProperty('buildstyle')
    arch = props.getProperty('arch')

    if style == "deb":
        args.extend(["mkdir ./deliverables && mv *.deb ./deliverables"])
    elif style == "rpm":
        mvcmd = "mkdir -p ./deliverables/{SRPM,%s/kmod} && mv $(ls *.rpm | grep -v *.src.rpm) ./deliverables/%s/kmod && mv *.src.rpm ./deliverables/SRPM" % (arch, arch)
        args.extend([mvcmd])
    else:
        args = []

    return args

def getBaseUrl(props):
    # generate the base url for build products of a change
    bb_url = props.getProperty('bbmaster')
    url = "http://%s/downloads/" % bb_url
    url += getChangeDirectory(props)
    return url

def getBaseMasterDest(props):
    # generate the base directory on the master for build products of a change
    masterdest = "public_html/downloads/"
    masterdest += getChangeDirectory(props)
    return masterdest

@util.renderer
def buildRepoCmd(props):
    # generate a repository to be sent to the build master
    # currently only support RPM based platforms
    args = ["sh", "-c"]
    style = props.getProperty('buildstyle')
    arch = props.getProperty('arch')
    distro = props.getProperty('distro')
    distrover = props.getProperty('distrover')
    url = getBaseUrl(props)
    url += ('%s/%s' % (distro, distrover))

    if style == "deb":
        args = []
    elif style == "rpm":
        # call create repo for the SRPM directory
        # call create repo for this architecture
        # generate a lustre.repo file for public consumption
        repocmd = "createrepo SRPM && createrepo %s/kmod && printf \"[lustre-SRPM]\nname=lustre-SRPM\nbaseurl=%s/SRPM/\nenabled=1\ngpgcheck=0\n\n[lustre-RPM]\nname=lustre-RPM\nbaseurl=%s/%s/kmod/\nenabled=1\ngpgcheck=0\" > lustre.repo" % (arch, url, url, arch)
        args.extend([repocmd])
    else:
        args = []

    return args

@util.renderer
def tarballMasterDest(props):
    # tarball exists in the top level of a change's directory
    tarball = props.getProperty('tarball')
    masterdest = getBaseMasterDest(props)
    masterdest += tarball
    return masterdest

@util.renderer
def tarballUrl(props):
    # tarball exists in the top level of a change's directory
    tarball = props.getProperty('tarball')
    url = getBaseUrl(props)
    url += tarball
    return url

@util.renderer
def repoMasterDest(props):
    # create a repo for each distro and distro version combination
    distro = props.getProperty('distro')
    distrover = props.getProperty('distrover')
    masterdest = getBaseMasterDest(props)
    masterdest += ('%s/%s' % (distro, distrover))
    return masterdest

@util.renderer
def repoUrl(props):
    # create a repo for each distro and distro version combination
    distro = props.getProperty('distro')
    distrover = props.getProperty('distrover')
    url = getBaseUrl(props)
    url += ('%s/%s' % (distro, distrover))
    return url

@util.renderer
def buildCategory(props):
    # category is generated by the scheduler name so we don't have to
    # look at the individual changes
    sched = props.getProperty('scheduler')
    if sched == 'master-patchset':
        return 'patchset'
    elif sched == 'tag-changes':
        return 'tag'

    return ''

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

def xsdkTestSuiteFactory(spack_repo):
    """ Generates a build factory for a tarball generating builder.
    Returns:
        BuildFactory: Build factory with steps for generating tarballs.
    """
    bf = util.BuildFactory()
    random.seed(random.random())
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
        hideStepIf=hide_if_skipped,
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

