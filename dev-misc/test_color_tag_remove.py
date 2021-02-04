#!/usr/bin/python3 -B

import io
import pprint
import re
import sys

# --- compatibility functions ---------------------------------------------------------------------

# --- functions -----------------------------------------------------------------------------------
# --- BEGIN code in dev-misc/test_color_tag_remove.py ---------------------------------------------
def text_remove_color_tags_slist(slist):
    # Iterate list of strings and remove the following tags
    # 1) [COLOR colorname]
    # 2) [/COLOR]
    #
    # Modifying a list is OK when iterating the list. However, do not change the size of the
    # list when iterating.
    for i, s in enumerate(slist):
        s_temp, modified = s, False

        # Remove all [COLOR colorname] tags.
        fa_list = re.findall('(\[COLOR \w+?\])', s_temp)
        fa_set = set(fa_list)
        if len(fa_set) > 0:
            modified = True
            for m in fa_set:
                s_temp = s_temp.replace(m, '')

        # Remove all [/COLOR]
        if s_temp.find('[/COLOR]') >= 0:
            s_temp = s_temp.replace('[/COLOR]', '')
            modified = True

        # Update list
        if modified:
            slist[i] = s_temp
# --- END code in dev-misc/test_color_tag_remove.py -----------------------------------------------

# --- main code -----------------------------------------------------------------------------------
test_string = ('[COLOR orange]cloneof[/COLOR] None / [COLOR orange]romof[/COLOR] neogeo / '
    '[COLOR skyblue]isBIOS[/COLOR] False / [COLOR skyblue]isDevice[/COLOR] False')
print('String "{}"'.format(test_string))
in_list = [test_string]

fa_list = re.findall('(\[COLOR \w+?\])', test_string)
fa_set = set(fa_list)
pprint.pprint(fa_list)
pprint.pprint(fa_set)

text_remove_color_tags_slist(in_list)
print('String "{}"'.format(in_list[0]))
