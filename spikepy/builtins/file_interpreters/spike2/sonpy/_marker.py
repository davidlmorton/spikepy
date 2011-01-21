def data(chan, start=None, stop=None, timeunits='seconds', as_float=True):
    '''
    Reads data from an event/marker channel (ie, Event, Marker, AdcMark,
    RealMark, or TextMark channel) from a SON file.

    'start', 'stop' set the data limits to be returned, in blocks. If
    only start is set, data from only that block will be returned.

    'timeunits' scales time to appropriate unit. Valid options are 'ticks',
    'microseconds', 'milliseconds' or 'seconds'.

    'as_float' only makes sense for AdcMark or RealMark channels. If
    True, returns data as floating point values (scaling and applying
    offset for Adc data). Else, data will be of type int16.
    '''
    from scipy import io, zeros
    fid = chan.fhead.fid
    blockheader = chan.blockheader
    size_of_header = 20 # Block header is 20 bytes long

    # ====================================
    # = Set start and end blocks to read =
    # ====================================
    if not start and not stop:
	start_block, end_block = 0, chan.info.blocks
    elif start and not stop:
	start_block, end_block = start-1, start
    elif start and stop:
	start_block, end_block = start-1, min([stop, chan.info.blocks])

    # == Sum of samples in required blocks ==
    n_items = sum(blockheader[4, start_block:end_block])

    # =============
    # = Read data =
    # =============
    #       + Event data +
    if chan.info.kind in [2, 3, 4]:
	# pre-allocate memory:
	timings = zeros(n_items, 'int32')
	# read data:
	pointer = 0
	for block in range(start_block, end_block):
	    fid.seek(blockheader[0, block] + size_of_header)
	    timings[pointer : pointer+blockheader[4, block]] = \
		    io.fread(fid, blockheader[4, block], 'l')
	    pointer += blockheader[4, block]

    #       + Marker data +
    elif chan.info.kind == 5:
	# pre-allocate memory:
	timings = zeros(n_items, 'int32')
	markers = zeros([n_items, 4], 'uint8')
	# read data:
	count = 0
	for block in range(start_block, end_block):
	    # start of block:
	    fid.seek(blockheader[0, block] + size_of_header)
	    # loop for each marker:
	    for i in range(blockheader[4, block]):
		timings[count] = io.fread(fid, 1, 'l') # time
		markers[count] = io.fread(fid, 4, 'B') # 4x marker bytes
		count += 1
	markers = [chr(x) for x in markers[:,0]]

    #       + AdcMark data +
    elif chan.info.kind == 6:
	n_values = chan.info.n_extra/2
	# 2 because 2 bytes per int16 value
	# pre-allocate memory:
	timings = zeros(n_items, 'int32')
	markers = zeros([n_items, 4], 'uint8')
	adc     = zeros([n_items, n_values], 'int16')
	# read data:
	count = 0
	for block in range(start_block, end_block):
	    # start of block:
	    fid.seek(blockheader[0, block] + size_of_header)
	    # loop for each marker:
	    for i in range(blockheader[4, block]):
		timings[count] = io.fread(fid, 1, 'l') # time
		markers[count] = io.fread(fid, 4, 'B')
		# 4x marker bytes
		adc[count]     = io.fread(fid, n_values, 'h')
		count += 1
	if as_double:
	    from _waveform import _adc_to_double
	    adc = _adc_to_double(chan, adc)

    #       + RealMark data +
    elif chan.info.kind == 7:
	n_values = chan.info.n_extra/4
	# each value has 4 bytes (single precision)
	# pre-allocate:
	timings = zeros(n_items, 'int32')
	markers = zeros([n_items, 4], 'uint8')
	real =    zeros([n_items, n_values], 'single')
	# read data:
	count = 0
	for block in range(start_block, end_block):
	    # start of block
	    fid.seek(blockheader[0, block] + size_of_header)
	    # loop for each marker
	    for i in range(blockheader[4, block]):
		timings[count] = io.fread(fid, 1, 'l') # time
		markers[count] = io.fread(fid, 4, 'B')
		# 4x marker bytes
		real[count]    = io.fread(fid, n_values, 'f')
		count += 1
	if not as_double:
	    from _waveform import _real_to_adc
	    real = _real_to_adc(real)

    #       + TextMark data +
    elif chan.info.kind == 8:
	# pre-allocate memory:
	timings = zeros(n_items, 'int32')
	markers = zeros([n_items, 4], 'uint8')
	text = zeros([n_items, chan.info.n_extra], 'S1')
	# read data:
	count = 0
	for block in range(start_block, end_block):
	    # start of block
	    fid.seek(blockheader[0, block] + size_of_header)
	    # loop for each marker
	    for i in range(blockheader[4, block]):
		timings[count] = io.fread(fid, 1, 'l') # time
		markers[count] = io.fread(fid, 4, 'B')
		# 4x marker bytes
		text[count]    = io.fread(
			fid, chan.info.n_extra, 'c')
		count += 1

    # ================
    # = Convert time =
    # ================
    timings = chan.fhead._ticks_to_seconds(timings, timeunits)
    chan.info.timeunits  = timeunits
    chan.info.epochs_str = '%i--%i of %i block(s)'\
			   %(start_block+1, end_block, chan.info.blocks)

    # ===============
    # = Return data =
    # ===============
    if chan.info.kind in [2, 3, 4]:
	data = timings
    elif chan.info.kind == 5:
	data = zip(timings, markers)
    elif chan.info.kind == 6:
	data = zip(timings, markers, adc)
    elif chan.info.kind == 7:
	data = zip(timings, markers, real)
    elif chan.info.kind == 8:
	data = zip(timings, markers, text)
    return data
