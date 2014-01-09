import os
import re
import shutil
import tempfile

import yapgvb

from framework import Framework, TARGET_SHAPES


def to_temp_file(dirname, fname, content):
    tier = fname.split("/")[-3]
    path = os.path.join(dirname, tier + "-" + os.path.basename(fname))
    if os.path.exists(path):
        raise Exception("{} already exists".format(path))
    open(path, "w").write(content)
    return path


def preprocess(fname):
    lst = []
    gfx = yapgvb.Graph().read(fname)
    txt = open(fname).read()
    targets = []

    # Replace the generated node names with their label. CMake generates a graph
    # like this:
    #
    # "node0" [ label="KF5DNSSD" shape="polygon"];
    # "node1" [ label="Qt5::Network" shape="ellipse"];
    # "node0" -> "node1"
    #
    # And we turn it into this:
    #
    # "KF5DNSSD" [ label="KF5DNSSD" shape="polygon"];
    # "Qt5::Network" [ label="Qt5::Network" shape="ellipse"];
    # "KF5DNSSD" -> "Qt5::Network"
    #
    # Using real framework names as labels makes it possible to merge multiple
    # .dot files.
    for node in gfx.nodes:
        label = node.label.replace("KF5::", "")
        if node.shape in TARGET_SHAPES:
            targets.append(label)
        txt = txt.replace('"' + node.name + '"', '"' + label + '"')

    # Sometimes cmake will generate an entry for the target alias, something
    # like this:
    #
    # "node9" [ label="KParts" shape="polygon"];
    # ...
    # "node15" [ label="KF5::KParts" shape="ellipse"];
    # ...
    #
    # After our node renaming, this ends up with a second "KParts" node
    # definition, which we need to get rid of.
    for target in targets:
        rx = r' *"' + target + '".*label="KF5::' + target + '".*shape="ellipse".*;'
        txt = re.sub(rx, '', txt)
    return txt


class FrameworkDb(object):
    def __init__(self):
        self._fw_list = []
        self._fw_for_target = {}

    def read_dot_files(self, dot_files, with_qt=False):
        """
        Init db from dot files
        """

        # Preprocess dot files so that they can be merged together
        # The output needs to be stored in a temp file because yapgvb crashes when
        # trying to make it read from a StringIO
        tmpdir = tempfile.mkdtemp(prefix="kf5dot")
        try:
            input_files = [to_temp_file(tmpdir, x, preprocess(x)) for x in dot_files]
            self._fw_list = [Framework(x, with_qt=with_qt) for x in input_files]
        finally:
            shutil.rmtree(tmpdir)
        self._update_fw_for_target()

    def _update_fw_for_target(self):
        self._fw_for_target = {}
        for fw in self._fw_list:
            for target in fw.get_targets():
                self._fw_for_target[target] = fw

    def find_by_name(self, name):
        for fw in self._fw_list:
            if fw.name == name:
                return fw
        return None

    def remove_unused_frameworks(self, wanted_fw):
        def is_used_in_list(the_fw, lst):
            for fw in lst:
                if fw == the_fw:
                    continue
                for target in fw.get_all_target_dependencies():
                    if the_fw.has_target(target):
                        return True
            return False

        done = False
        old_lst = self._fw_list
        while not done:
            lst = []
            done = True
            for fw in old_lst:
                if fw == wanted_fw:
                    lst.append(fw)
                    continue
                if is_used_in_list(fw, old_lst):
                    lst.append(fw)
                else:
                    done = False
            old_lst = lst
        self._fw_list = lst

    def find_external_targets(self):
        all_targets = set([])
        fw_targets = set([])
        for fw in self._fw_list:
            fw_targets.update(fw.get_targets())
            all_targets.update(fw.get_all_target_dependencies())
        return all_targets.difference(fw_targets)

    def get_fw_for_target(self, target):
        return self._fw_for_target[target]

    def __iter__(self):
        return iter(self._fw_list)
