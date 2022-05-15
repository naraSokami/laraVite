import os
import shutil
import glob
from env import VERSION, PATH
import time


# # path
# PATH = input("where do you wanna import files ?")

# while len(glob.glob(PATH.replace("~", os.path.expanduser('~')))) < 1:
#     PATH = input("path invalid please enter a valid path\n")



# bin directory
if not os.path.isdir(os.path.expanduser('~') + "/bin"):
    os.mkdir(os.path.expanduser('~') + "/bin")

# copy laraVite folder in PATH
while os.path.isdir(PATH):
    print("It seems you already have a laraVite folder in ~/bin")
    name = input("How do u wanna name it ?\n")
    PATH = os.path.expanduser('~') + "/bin/" + name
 
shutil.copytree(os.path.dirname(__file__), PATH)


if not os.path.isfile(PATH + "/.bashrc"):
    # touch .bashrc file in home directory
    with open(PATH + "/.bashrc", 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("\n")
        f.write("# .bashrc\n")
        f.write("# Created by laraVite {}\n".format(VERSION))
        f.write("\n")
        f.write("alias laraVv='python {}/main.py'\n".format(PATH.replace("\\", "/")))
        f.close()

# ask to run source
com = "source " + PATH.replace("\\", "/") + "/.bashrc"
print("\n\nplease run\n\t" + com + " in ur terminal")

print("\n\n this window will close in :")
for i in range(21)[::-1]:
    print(' ', i)
    time.sleep(1)
