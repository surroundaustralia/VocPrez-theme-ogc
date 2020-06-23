import errno
from os.path import join, dirname
import os
import fileinput
import shutil
import glob


def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise

# this dir
THIS_DIR = dirname(__file__)
VOCPREZ_HOME = join(os.sep, "Users", "nick", "Work", "surround", "vocprez", "vocprez")

# add images
THIS_STYLE = join(THIS_DIR, "style")
VP_STYLE = join(VOCPREZ_HOME, "view", "style")
for filename in glob.glob(os.path.join(THIS_STYLE, '*.*')):
    print("copying {} to {}".format(filename, VP_STYLE))
    shutil.copy(filename, VP_STYLE)


# replace templates
THIS_TEMPLATES = join(THIS_DIR, "templates")
VP_TEMPLATES = join(VOCPREZ_HOME, "view", "templates")
for filename in glob.glob(os.path.join(THIS_TEMPLATES, '*.*')):
    print("copying {} to {}".format(filename, VP_TEMPLATES))
    shutil.copy(filename, VP_TEMPLATES)

# configure config
#

