import difflib
import sys
from web_ui.controllers.apic import SNAPSHOT_PATH

d = difflib.Differ()


def getDiff(file_name_1, file_name_2, apic_url):
    apic_dir = apic_url.replace("http:", "").replace("https:", "").replace("/", "")
    diff_str = ""
    with open(SNAPSHOT_PATH + "/" + apic_dir + "/" + file_name_1, 'r') as file1:
        with open(SNAPSHOT_PATH + "/" + apic_dir + "/" + file_name_2, 'r') as file2:
            diff = difflib.unified_diff(file1.readlines(),
                                        file2.readlines(),
                                        fromfile=file_name_1,
                                        tofile=file_name_2)
            for line in diff:
                include = True
                for prefix in (' '):
                    if line.startswith(prefix):
                        include = False
                if include:
                    diff_str += line
    return diff_str
