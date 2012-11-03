
    if (high_frequency_cutoff is not None 
        and high_frequency_cutoff < sampling_frequency):
        resampled_signal = resample_signal(signal, sampling_frequency, 
                                                    high_frequency_cutoff)
    else:
        high_frequency_cutoff = sampling_frequency
        resampled_signal = signal
    NFFT= find_NFFT(frequency_resolution, high_frequency_cutoff, 
                    force_power_of_two=True) 
    if axes is not None:
        return axes.psd(resampled_signal, NFFT=NFFT, 
                             Fs=high_frequency_cutoff, 
                             noverlap=0, **kwargs)
    else:
        return mlab.psd(resampled_signal, NFFT=NFFT, 
                Fs=high_frequency_cutoff, noverlap=0, **kwargs)

