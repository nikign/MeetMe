import os
import sys
from fabric.api import *
from os import stat
from os.path import exists


# ==========================
# ========= globals ========
# ==========================

env.project_name = 'meet'
env.hosts = ['127.0.0.1']
env.path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
env.run_locally = True
env.target_os = sys.platform


# ==========================
# ========== tasks =========
# ==========================

def makemessages():
    """ Prepares django.po """
    command = '%(path)s/manage.py makemessages -l fa --no-obsolete --no-wrap --no-location'
    local_with_bash(command % env)


def compilemessages():
    """ Compiles django.po into django.mo """
    command = "%(path)s/manage.py compilemessages"
    local_with_bash(command % env)


def test():
    command = '%(path)s/manage.py test meet'
    local_with_bash(command % env)


def local_with_bash(cmd, *args, **kwargs):
    c_m_d = []
    bs_buf = []
    for c in cmd:
        if c == '\\':
            # Don't know if we need to double yet.
            bs_buf.append(c)
        elif c == '"':
            # Double backslashes.
            c_m_d.append('\\' * len(bs_buf)*2)
            bs_buf = []
            c_m_d.append('\\"')
        else:
            # Normal char
            if bs_buf:
                c_m_d.extend(bs_buf)
                bs_buf = []
            c_m_d.append(c)
    if bs_buf:
        result.extend(bs_buf)

    skipped_cmd = ''.join(c_m_d)
    return local('/bin/bash -l -c "%s"' % skipped_cmd, *args, **kwargs)