import time


def timeit(f):
    """ Decorator to time Any Function """

    def timed(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        seconds = end_time - start_time
        print("Function Time[-] %s : %2.5f sec, which is %2.5f min, which is %2.5f hour" %
              (f.__name__, seconds, seconds / 60, seconds / 3600))
        return result

    return timed
