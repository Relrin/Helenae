import os
import fnmatch


def getFileList(path_to_folder):
    matches = []
    for root, dirnames, filenames in os.walk(path_to_folder):
        for filename in fnmatch.filter(filenames, '*.*'):
            matches.append(os.path.join(root, filename))
    return matches