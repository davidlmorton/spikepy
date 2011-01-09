import wx

from spikepy.common import utils

print "\nSpikepy configuration directories on platform: %s (%s)" % (wx.Platform, 
                                                        utils.platform())

data_dirs = utils.get_data_dirs(app_name='spikepy')

for level in data_dirs.keys():
    print "\n\t--%s--" % (level[0].upper() + level[1:].lower())
    for key, value in data_dirs[level].items():
        print "\t\t%s: %s" % (key, value)
    
