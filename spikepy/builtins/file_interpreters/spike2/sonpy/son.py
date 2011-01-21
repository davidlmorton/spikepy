from __init__ import __doc__

def get_sample_interval(chan, unit='microseconds'):
    """
    Returns the sampling interval on a waveform data channel, i.e.,
    the reciprocal of the sampling rate for that channel.

    Based on SONGetSampleInterval.m from the Matlab SON library which
    is part of sigTOOL by Dr. Malcolm Lidierth:
    http://sigtool.sourceforge.net/
    http://www.kcl.ac.uk/schools/biohealth/depts/physiology/mlidierth.html
    """
    if chan.info.kind not in [1,6,7,9]:
        raise ValueError("Invalid channel type")
    if chan.fhead.system_id in [1,2,3,4,5]: # Before version 5
        sample_interval = (chan.info.divide*chan.fhead.us_per_time*
                           chan.fhead.time_per_adc)
    else: # version 6 and above
        sample_interval = (chan.info.l_chan_dvd*chan.fhead.us_per_time*
                           1e6*chan.fhead.dtime_base)
    
    if unit=='microseconds':
        return sample_interval
    elif unit=='milliseconds':
        return sample_interval*1e-3
    elif unit=='seconds':
        return sample_interval*1e-6
    else:
        raise ValueError(
            "Invalid unit: "+str(unit)+
            "\n Must be 'microseconds', 'milliseconds', or 'seconds'")
    

def _get_block_headers(fhead, chan_info):
    '''
    Returns a matrix containing the SON data block headers for a
    channel.
    'fhead' is a FileHeader instance, and 'chan_info' is a
    ChannelInfo instance.

    The returned header in memory contains, for each disk block,
    a column with rows 0-4 representing:
    Offset to start of block in file
    Start time in clock ticks
    End time in clock ticks
    Chan number
    Items
    '''
    from scipy import io, zeros, arange, take
    if chan_info.firstblock == -1:
        raise ValueError('No data on channel ' + str(chan_info.chan))
    succ_block = 1
    # Pre-allocate memory for header data:
    header = zeros([6, chan_info.blocks], int)
    # Get first data block:
    fhead.fid.seek(chan_info.firstblock)
    # Last and next block pointers, start and end times in clock ticks
    header[0:4, 0] = io.fread(fhead.fid, 4, 'l')
    # Channel number and number of items in block:
    header[4:6, 0] = io.fread(fhead.fid, 2, 'h')
    # If only one block:
    if header[succ_block, 0] == -1:
        header[0, 0] = int(chan_info.firstblock)
    # Loop if more blocks:
    else:
        fhead.fid.seek(header[succ_block, 0])
        for i in arange(1, chan_info.blocks):
            header[0:4, i] = io.fread(fhead.fid, 4, 'l')
            header[4:6, i] = io.fread(fhead.fid, 2, 'h')
            if header[succ_block, i] > 0:
                fhead.fid.seek(header[succ_block, i])
            header[0, i-1] = header[0, i]
        # Replace pred_block for previous column:
        header[0, -1] = header[1, -2]
    # Delete succ_block data:
    header = take(header, (0,2,3,4,5), axis=0)
    return header

class FileHeader:
    '''
    Reads the file header for a SON file.
    >>> fhead = FileHeader(filename)
    '''
    def __init__(self, filename):
        from scipy import io, zeros
        self.name = filename
        self.fid = open(filename, 'rb')
        self.fid.seek(0)
        self.system_id   = io.fread(self.fid, 1, 'h')
        self.copyright  = self.fid.read(10)
        self.creator    = self.fid.read(8)
        self.us_per_time  = io.fread(self.fid, 1, 'h')
        self.time_per_adc = io.fread(self.fid, 1, 'h')
        self.filestate  = io.fread(self.fid, 1, 'h')
        self.first_data  = io.fread(self.fid, 1, 'l')
        self.channels   = io.fread(self.fid, 1, 'h')
        self.chan_size   = io.fread(self.fid, 1, 'h')
        self.extra_data  = io.fread(self.fid, 1, 'h')
        self.buffersize = io.fread(self.fid, 1, 'h')
        self.os_format   = io.fread(self.fid, 1, 'h')
        self.max_ftime   = io.fread(self.fid, 1, 'l')
        self.dtime_base  = io.fread(self.fid, 1, 'd')
        if self.system_id < 6: self.dtime_base = 1e-6
        self.time_date = {
                        'Detail' : io.fread(self.fid, 6, 'B'),
                        'Year' :   io.fread(self.fid, 1, 'h')}
        if self.system_id < 6:
            self.time_date['Detail'] = zeros(6)
            self.time_date['Year'] = 0
        pad = self.fid.read(52)
        self.file_comment = {}
        pointer = self.fid.tell()
        for i in range(1, 6):
            bytes = io.fread(self.fid, 1, 'B')
            self.file_comment[i] = self.fid.read(bytes)
            pointer = pointer + 80
            self.fid.seek(pointer)

    def __del__(self):
        self.fid.close()

    def chan_list(self):
        '''
        Prints a table with details of active channels in a SON file.
        '''
        print '-' * 38
        print '%-5s %-10s %-10s %s' %('Chan', 'Type', 'Title', 'Comment')
        print '-' * 38
        for chan in range(1, self.channels+1):
            info = _ChannelInfo(self, chan)
            if info.kind > 0:
                print '%-5i %-10s %-10s %s' % (
                        chan, info.type(), info.title,
                        info.comment)
        print '-' * 38

    def _ticks_to_seconds(self, timestamp, timeunits):
        '''
        Scales a timestamp vector.

        'timeunits' is one of
            'ticks': returns the time in base clock ticks.
            'microseconds', 'milliseconds' or 'seconds': scales the
            output to the appropriate unit.
        '''
        if timeunits is 'ticks':
            pass
        elif timeunits is 'microseconds':
            timestamp = timestamp * (self.us_per_time * self.dtime_base * 1e6)
        elif timeunits is 'milliseconds':
            timestamp = timestamp * (self.us_per_time * self.dtime_base * 1e3)
        elif timeunits is 'seconds': # default, time in seconds
            timestamp = timestamp * (self.us_per_time * self.dtime_base)
        else: raise ValueError
        return timestamp #, timeunits

    def __repr__(self):
        return 'File header from SON file %s' % self.name

class _ChannelInfo:
    '''
    Reads the SON file channel header for a channel.
    info = ChannelInfo(fhead, channel)
    where
        'fhead' is an instance containing the file header, and
        'channel' is the channel number.

    The resulting instance will contain values which follow the CED
    disk header structure.
    '''
    def __init__(self, fhead, channel):
        from scipy import io
        self.chan = channel
        # Offset due to file header and preceding channel headers:
        base = 512 + (140*(channel-1))
        fhead.fid.seek(base)
        self.del_size       = io.fread(fhead.fid, 1, 'h')
        self.next_del_block = io.fread(fhead.fid, 1, 'l')
        self.firstblock     = io.fread(fhead.fid, 1, 'l')
        self.lastblock      = io.fread(fhead.fid, 1, 'l')
        self.blocks         = io.fread(fhead.fid, 1, 'h')
        self.n_extra        = io.fread(fhead.fid, 1, 'h')
        self.pre_trig       = io.fread(fhead.fid, 1, 'h')
        self.free0          = io.fread(fhead.fid, 1, 'h')
        self.py_sz          = io.fread(fhead.fid, 1, 'h')
        self.max_data       = io.fread(fhead.fid, 1, 'h')
        bytes               = io.fread(fhead.fid, 1, 'B')
        pointer             = fhead.fid.tell()
        self.comment        = fhead.fid.read(bytes)
        fhead.fid.seek(pointer+71)
        self.max_chan_time  = io.fread(fhead.fid, 1, 'l')
        self.l_chan_dvd     = io.fread(fhead.fid, 1, 'l')
        self.phy_chan       = io.fread(fhead.fid, 1, 'h')
        bytes               = io.fread(fhead.fid, 1, 'B')
        pointer             = fhead.fid.tell()
        self.title          = fhead.fid.read(bytes)
        fhead.fid.seek(pointer+9)
        self.ideal_rate     = io.fread(fhead.fid, 1, 'f')
        self.kind           = io.fread(fhead.fid, 1, 'B')
        pad                 = io.fread(fhead.fid, 1, 'b')

        if self.kind in [1, 6]:
            self.scale    = io.fread(fhead.fid, 1, 'f')
            self.offset   = io.fread(fhead.fid, 1, 'f')
            bytes         = io.fread(fhead.fid, 1, 'B')
            pointer       = fhead.fid.tell()
            self.units    = fhead.fid.read(bytes).strip()
            fhead.fid.seek(pointer+5)
            if fhead.system_id < 6: self.divide = io.fread(fhead.fid, 1, 'l')
            else: self.interleave = io.fread(fhead.fid, 1, 'l')
        elif self.kind in [7, 9]:
            self.min       = io.fread(fhead.fid, 1, 'f')
            self.max       = io.fread(fhead.fid, 1, 'f')
            bytes          = io.fread(fhead.fid, 1, 'B')
            pointer        = fhead.fid.tell()
            self.units     = fhead.fid.read(bytes).strip()
            fhead.fid.seek(pointer+5)
            if fhead.system_id < 6: self.divide = io.fread(fhead.fid, 1, 'l')
            else: self.interleave = io.fread(fhead.fid, 1, 'l')
        elif self.kind in [4]:
            self.init_low   = io.fread(fhead.fid, 1, 'B')
            self.next_low   = io.fread(fhead.fid, 1, 'B')

    def type(self):
        '''
        Adc        16-bit integer waveform data
        EventFall  event data, times taken on low edge of pulse
        EventRise  event data, times taken on high edge of pulse
        EventBoth  event data, times taken on both edges of pulse
        Marker     an event time plus four identifying bytes
        AdcMark    16-bit integer waveform transient shapes
        RealMark   array of real numbers attached to a marker
        TextMark   string of text attached to a marker
        RealWave   32-bit floating point waveforms
        '''
        if   self.kind == 1: type = 'Adc'
        elif self.kind == 2: type = 'EventFall'
        elif self.kind == 3: type = 'EventRise'
        elif self.kind == 4: type = 'EventBoth'
        elif self.kind == 5: type = 'Marker'
        elif self.kind == 6: type = 'AdcMark'
        elif self.kind == 7: type = 'RealMark'
        elif self.kind == 8: type = 'TextMark'
        elif self.kind == 9: type = 'RealWave'
        return type

    def __repr__(self):
        return 'Information from channel %i' % self.chan

class Channel:
    '''
    Creates an instance whose attributes are those of a channel from a
    SON file.

    >>> chan = Channel(chan_number, filename)
    chan.info will contain the channel information, and
    chan.fhead will contain the SON file header

    Useful calls:
    >>> chan.type()
    >>> chan.data()
    '''
    def __init__(self, channel, filename):
        self.fhead = FileHeader(filename)
        self.info = _ChannelInfo(self.fhead, channel)
        self.blockheader = _get_block_headers(self.fhead, self.info)

    def __repr__(self):
        return  'Channel %i from %s' % (self.info.chan, self.fhead.name)

    def data(self, start=None, stop=None, timeunits='seconds', as_float=True):
        '''
        Returns channel data from a SON file.

        If only a fragment of data is required, limits (in blocks) can be
        defined in 'start' and 'stop'.

        If only 'start' is set, data from that block will be returned.

        'timeunits' can be 'ticks', 'microseconds', 'milliseconds', or
        'seconds', and cause times to be scaled to the appropriate unit.

        'as_float' only makes sense for waveform channels (ie channels of
        type AdcMark, RealMark, Adc, or RealWave). If True, returns data as
        floating point values (scaling and applying offset for Adc/AdcMark
        channel data). Else, data will be of type int16.
        '''
        if self.info.kind in [1, 9]:
            from _waveform import data
            return data(self, start, stop, timeunits, as_float)
        elif self.info.kind in [2, 3, 4, 5, 6, 7, 8]:
            from _marker import data
            return data(self, start, stop, timeunits)

    def type(self):
        '''
        Adc        16-bit integer waveform data
        EventFall  event data, times taken on low edge of pulse
        EventRise  event data, times taken on high edge of pulse
        EventBoth  event data, times taken on both edges of pulse
        Marker     an event time plus four identifying bytes
        AdcMark    16-bit integer waveform transient shapes
        RealMark   array of real numbers attached to a marker
        TextMark   string of text attached to a marker
        RealWave   32-bit floating point waveforms
        '''
        return self.info.type()

    def __del__(self):
        self.fhead.fid.close()

class File:
    '''
    Creates an instance whose attributes are those of a SON file.

    Useful calls:
    >>> f = File(filename) # then:
    >>> f.chanlist() # will print a list of available channels, and
    >>> f.getchannel(chan_number)
    # will create a channel instance named after the
    # channel number provided (see class Channel).
    '''
    def __init__(self, filename):
        self.name = filename

    def __repr__(self):
        return  'SON file %s' % self.name

    def get_channel(self, channel):
        '''
        Set an attribute of current SON file to the channel provided.
        '''
        attr = 'ch%02i' % channel
        self.__dict__[attr] = Channel(channel, self.name)

    def chan_list(self):
        '''
        Prints a table with details of active channels in a SON file.
        '''
        FileHeader(self.name).chan_list()
