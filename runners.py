import threading
from multiprocessing import Queue
from time import sleep
from pie_logger import get_logger

log = get_logger()


def complex_runner(func, pies, pie_count=3, **kwargs):
    """Run pie (object or list) pie_count times.
    func: the function to send to run. like bake_it
    Pies: a Pie or list of Pies to run
    pie_count: multipy the the pies pie_count times
    **kwargs, any arguments to send to func    
    """

    oven_q = Queue()

    if type(pies) != list:
        pies = [pies]

    def start_oven(oven_q, seconds):
        log.debug("wait {} seconds while we heat the oven...".format(seconds))
        sleep(seconds)
        log.debug("oven heated for {} seconds".format(seconds))
        oven_q.put(True)

    thread_oven = threading.Thread(target=start_oven, args=(oven_q, 10))
    thread_oven.start()

    threads = []
    for a_pie in pies:
        for x in range(pie_count):
            kwargs.update(n=x)
            thread = threading.Thread(target=func,
                                      args=(oven_q,
                                            a_pie),
                                      kwargs=kwargs)
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()

    thread_oven.join()
    sleep(0.1)
    log.info("done!")
