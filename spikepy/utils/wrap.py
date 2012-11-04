#  Copyright (C) 2012  David Morton
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
## {{{ http://code.activestate.com/recipes/148061/ (r6)
def wrap(text, width):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )
'''
# 2 very long lines separated by a blank line
msg = """Arthur:  "The Lady of the Lake, her arm clad in the purest \
shimmering samite, held aloft Excalibur from the bosom of the water, \
signifying by Divine Providence that I, Arthur, was to carry \
Excalibur. That is why I am your king!"

Dennis:  "Listen. Strange women lying in ponds distributing swords is \
no basis for a system of government. Supreme executive power derives \
from a mandate from the masses, not from some farcical aquatic \
ceremony!\""""

# example: make it fit in 40 columns
print(wrap(msg,40))

# result is below
"""
Arthur:  "The Lady of the Lake, her arm
clad in the purest shimmering samite,
held aloft Excalibur from the bosom of
the water, signifying by Divine
Providence that I, Arthur, was to carry
Excalibur. That is why I am your king!"

Dennis:  "Listen. Strange women lying in
ponds distributing swords is no basis
for a system of government. Supreme
executive power derives from a mandate
from the masses, not from some farcical
aquatic ceremony!"
"""
'''
## end of http://code.activestate.com/recipes/148061/ }}}

