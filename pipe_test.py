import multiprocessing as mp


parent, child = mp.Pipe()
child.close()

try:
    state = parent.poll()
except BrokenPipeError:
    print('Pipe is closed')
