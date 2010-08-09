import traceback

def pool_process(pool, function, args=tuple(), kwargs=dict()):
    if pool is not None:
        try:
            pool_result = pool.apply_async(function, args=args, kwds=kwargs)
            result = pool_result.get()
        except:
            traceback.print_exc()
            sys.exit(1)
    else:
        result = function(*args, **kwargs)
    return result

