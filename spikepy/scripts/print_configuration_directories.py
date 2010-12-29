import wx

from spikepy.common import utils

print "\nSpikepy configuration directories on platform: %s (%s)" % (wx.Platform, 
                                                        utils.platform())

data_dirs = utils.get_data_dirs(app_name='spikepy')

print "\n\t--Application-level--"
for key, value in data_dirs['application'].items():
    print "\t\t%s: %s" % (key, value)
    
print "\n\t--User-level--"
for key, value in data_dirs['user'].items():
    print "\t\t%s: %s" % (key, value)

