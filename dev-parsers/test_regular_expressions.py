#!/usr/bin/python3 -B

import pprint
import re
import sys

# --- main code -----------------------------------------------------------------------------------
# line_str = '$bio'
# line_str = '$info=dino,'
line_str = '$info=dino,dinou,dinopic,dinopic2,dinoa,'

print('String "{}"'.format(line_str))
m = re.search(r'^\$(.+?)=(.+?),$', line_str)
if m:
    print('Match')
    group_list = m.groups()
    pprint.pprint(group_list)

    list_name = m.group(1)
    mname_list = m.group(2).split(',')
    print(mname_list)
else:
    print('No match')
sys.exit(0)
