def exclude_keys(dictionary, keys):
    return dict((k, v) for k, v in dictionary.iteritems() if k not in keys)
