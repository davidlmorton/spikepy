
    filename = os.path.split(fullpath)[-1]

    candidates = {}
    for fi in file_interpreters.values():
        for extention in fi.extentions:
            if filename.endswith(extention):
                candidates['%04d-%s' % (fi.priority, fi.name)] = fi

    if candidates:
        return [candidates[key] for key in 
                sorted(candidates.keys(), reverse=True)]
    
    # no good matches found, so try everything.
    return file_interpreters
