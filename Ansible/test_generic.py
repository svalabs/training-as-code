"""
Deployment unit tests
Generic tests
"""
import os
import testinfra.utils.ansible_runner


def test_software(host):
    """
    Check whether required software packages are installed
    """
    packages = [
        "vim-common",
        "bind-utils",
        "epel-release",
        "python3-pytest"
    ]
    for pkg in packages:
        _pkg = host.package(pkg)
        assert _pkg.is_installed

def test_firewall(host):
    """
    Check whether firewall is disabled
    """
    firewalld = host.service("firewalld")
    assert firewalld.is_enabled == False
    assert firewalld.is_running == False

def test_selinux(host):
    """
    Check whether SELinux is in Permissive mode
    """
    sebool = host.run("getenforce")
    assert sebool.stdout.lower().strip() == "permissive"
