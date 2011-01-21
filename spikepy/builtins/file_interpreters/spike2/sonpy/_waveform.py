def _adc_to_double(chan, data):
    '''
    Scales a SON Adc channel (int16) to double precision floating point.

    'chan' is a Channel instance.

    Applies the scale and offset supplied in chan.fhead to the data
    contained in 'data'. These values are derived form the channel
    header on disc.

        OUT = (DATA * SCALE/6553.6) + OFFSET

    chan.info will be updated with fields for the min and max values.
    '''
    if data.dtype.name != 'int16':
        raise TypeError('16 bit integer expected')
    s = chan.info.scale / 6553.6
    out = (data.astype('double') * s) + chan.info.offset
    chan.info.ymax = (data.max().astype('double') * s) + chan.info.offset
    chan.info.ymin = (data.min().astype('double') * s) + chan.info.offset
    # chan.info.kind = 9
    return out

def _real_to_adc(data):
    '''
    Converts a floating point array to int16.
    '''
    from scipy import array, polyfit
    # find min and max of input:
    a = array([data.min(), data.max()])
    # find slope and intercept for the line through (-32768, min)
    # and (32767, max):
    scale = polyfit([-32768, 32767], a, 1)
    data = (data-scale[1])/scale[0] # y = ax+b so find x = (y-b)/a
    data = data.round()             # round to nearest integer
    # check that int16 conversion can't lead to overflow:
    if (data.max() > 32767) | (data.min() < -32768):
        raise ValueError('Outside 16bit-integer range')
    data = data.astype('int16')    # convert to int16
    # hout.scale = scale[0]*6553.6 # adjust slope to conform to SON scale
    #                              # format...
    # hout.offset = scale[1]       # ... and set offset
    # hout.kind = 1                # set kind to ADC channel
    return data

def data(chan, start=None, stop=None, timeunits='seconds', as_float=True):
    '''
    Reads data from a RealWave or Adc channel from a SON file.

    'chan' is a Channel intance.

    'start', 'stop' set the data limits to be returned, in blocks for
    continuous data or in epochs for triggered data. If only start
    is set, data from only the block/epoch selected will be returned.

    'timeunits' scales time to appropriate unit. Valid options are 'ticks',
    'microseconds', 'milliseconds' or 'seconds'.

    'as_float=True' returns data as floating point values (scaling and
    applying offset for Adc channel data). Else, data will be of type int16.

    RETURNS data, which can be a simple vector (for continuously sampled
    data) or a two-dimensional matrix with each epoch (frame) of data
    in a separate row (if sampling was triggered).
    '''
    from scipy import array, io, histogram, zeros
    fid = chan.fhead.fid
    blockheader = chan.blockheader
    size_of_header = 20 # block header is 20 bytes long
    # sample interval in clock ticks:
    sample_interval = ((blockheader[2,0]-blockheader[1,0])/
                       (blockheader[4,0]-1))

    # =======================================================
    # = Set data types according to channel type to be read =
    # =======================================================
    if chan.info.kind == 1:   datatype = 'h' # Adc channel, 'int16'
    elif chan.info.kind == 9: datatype = 'f' # RealWave channel, 'single'

    # ============================================
    # = Check for discontinuities in data record =
    # ============================================
    num_frames = 1 # number of frames. Initialize to one
    frame = [1]
    for i in range(chan.info.blocks-1): 
        interval_between_blocks = blockheader[1, i+1] - blockheader[2, i]
        if interval_between_blocks > sample_interval:
            # if true, data is discontinuous
            num_frames += 1 # count discontinuities (num_frames)
            #record the frame number that each block belongs to:
            frame.append(num_frames)
        else:
            frame.append(frame[i]) # pad between discontinuities
    frame = array(frame)

    # =================================
    # = Set start and stop boundaries =
    # =================================
    if not start and not stop:
        frames_to_return = num_frames
        chan.info.npoints = zeros(frames_to_return)
        start_epoch = 0 # read all data
        end_epoch = chan.info.blocks
    elif start and not stop:
        if num_frames == 1: # read one epoch
            start_epoch = start-1
            end_epoch = start
        else:
            frames_to_return = 1
            chan.info.npoints = 0
            indx = arange(frame.size)
            start_epoch = indx[frame == start][0]
            end_epoch = indx[frame == start][-1] + 1
    elif start and stop:
        if num_frames == 1: # read a range of epochs
            start_epoch = start-1
            end_epoch = stop
        else:
            frames_to_return = stop-start + 1
            chan.info.npoints = zeros(frames_to_return)
            indx = arange(frame.size)
            start_epoch = indx[frame == start][0]
            end_epoch = indx[frame == stop][-1] + 1

    # Make sure we are in range if using 'start' and 'stop'
    if (start_epoch > chan.info.blocks) | (start_epoch > end_epoch):
        raise ValueError('Invalid start and/or stop')
    if end_epoch > chan.info.blocks: end_epoch = chan.info.blocks

    # =============
    # = Read data =
    # =============
    if num_frames == 1:
        # ++ Continuous sampling - one frame only. Epochs correspond to
        # blocks in the SON file.
        # sum of samples in all blocks:
        number_of_samples = sum(blockheader[4, start_epoch:end_epoch])
        # pre-allocate memory for data:
        data = zeros(number_of_samples, datatype)
        # read data:
        pointer = 0
        for i in range(start_epoch, end_epoch):
            fid.seek(blockheader[0, i] + size_of_header)
            data[pointer : pointer+blockheader[4, i]] =\
                         io.fread(fid, blockheader[4, i], datatype)
            pointer += blockheader[4, i]
        # set extra channel information:
        chan.info.mode       = 'continuous'
        chan.info.epochs     = [start_epoch+1, end_epoch]
        chan.info.npoints    = number_of_samples
        # first data point (clock ticks):
        chan.info.start      = blockheader[1, start_epoch]
        # end of data (clock ticks):
        chan.info.stop       = blockheader[2, end_epoch-1]
        chan.info.epochs_str = '%i--%i of %i blocks' % (start_epoch+1,
                                                        end_epoch,
                                                        chan.info.blocks)

    else:
        # ++ Frame-based data -  multiple frames. Epochs correspond to
        # frames of data.
        # sum of samples in required epochs:
        number_of_samples = sum(blockheader[4, start_epoch:end_epoch])
        # maximum data points to a frame:
        frame_length = (
                histogram(frame, range(start_epoch,end_epoch))[0].max()*
                blockheader[4, start_epoch:end_epoch].max())
        # pre-allocate memory:
        data = zeros([frames_to_return, frame_length], datatype)
        chan.info.start = zeros(frames_to_return)
        chan.info.stop = zeros(frames_to_return)
        # read data:
        pointer = 0 # pointer into data array for each disk data block
        index = 0   # epoch counter
        for i in range(start_epoch, end_epoch):
            fid.seek(blockheader[0, i] + size_of_header)
            data[index, pointer : pointer+blockheader[4, i]] =\
                            io.fread(
                    fid, blockheader[4, i], datatype)
            chan.info.npoints[index] = (chan.info.npoints[index]+
                                        blockheader[4,i])
            try: frame[i+1]
            except IndexError:
                chan.info.stop[index] = blockheader[2, i]
                # time at eof
            else:
                if frame[i+1] == frame[i]:
                    pointer += blockheader[4, i]
                    # increment pointer or...
                else:
                    chan.info.stop[index] = blockheader[2, i]
                    # end time for this frame
                    if i < end_epoch-1:
                        pointer = 0 # begin new frame
                        index += 1
                        # time of first data
                        # point in next frame
                        # (clock ticks):
                        chan.info.start[index] = \
                                blockheader[1, i+1]
        # set extra channel information:
        chan.info.mode = 'triggered'
        chan.info.start[0] = blockheader[1, start_epoch] 
        chan.info.epochs_str = '%i--%i of %i epochs' % (
                start_epoch+1, end_epoch,num_frames)

    # ================
    # = Convert time =
    # ================
    chan.info.start = chan.fhead._ticks_to_seconds(
            chan.info.start, timeunits)
    chan.info.stop =  chan.fhead._ticks_to_seconds(
            chan.info.stop, timeunits)
    chan.info.timeunits = timeunits

    # =========================
    # = Scale and return data =
    # =========================
    if as_float and chan.info.kind == 1:     # Adc
        data = _adc_to_double(chan, data)
    if not as_float and chan.info.kind == 9: # RealWave
        data = _real_to_adc(data)
    return data
