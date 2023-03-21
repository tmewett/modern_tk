import asyncio
import importlib.resources
from inspect import isfunction, signature
from pathlib import Path

from msgpack import Unpacker

class TclError(Exception): pass

def escape_tcl(x):
    match x:
        case int() | float(): return str(x)
        case str():
            return "{"+x+"}"
        case _ if isfunction(x):
            sig = signature(x)
            if any(len(name) != 1 for name in sig.parameters):
                raise NameError(f"unknown argument name(s) in Tk callback {x.__qualname__}")
            args = " ".join(f"%{name}" for name in sig.parameters)
            return f"{{callback {id(x)} {args}}}"
        case _:
            raise TypeError(f"can't convert type {type(x).__name__} into Tcl")

def substitute_tcl(code, values):
    callbacks = set()
    parts = code.split("?")
    if len(values) != len(parts) - 1:
        raise ArgumentError(f"wrong number of values for substitution; got {len(values)}, expected {len(parts) - 1}")
    command = []
    for v in values:
        command.append(parts.pop(0))
        command.append(escape_tcl(v))
    command.append(parts.pop(0))
    return " ".join(command)

# Type converters for Tk 'bind' parameters.
bind_param_map = {
    # %a, %w are hex numbers, but I think semantically IDs/pointers, so leave as strings.
    # Leave (0, 1) booleans as ints to match Tk docs.
    # w,x,y,X,Y floats?
    "b": int,
    "c": int,
    "f": int,
    "h": int,
    "t": float,
    "w": int,
    "x": int,
    "y": int,
    "B": int,
    "D": float, # int?
    "E": int,
    "M": int,
    "N": int,
    "X": int,
    "Y": int,
}

class AsyncioTk:
    def __init__(self, tclsh):
        self.tclsh = Path(tclsh)
        self._results = {}
        self._callbacks = {}
        self._id = 0
    def _new_id(self):
        self._id += 1
        return self._id
    async def __aenter__(self):
        # XXX Doesn't use as_file so probably doesn't work zipped.
        files = importlib.resources.files(f'{__name__}._tcl_lib')
        self._done = asyncio.Event()
        self._process = await asyncio.create_subprocess_exec(self.tclsh, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
        self._process.stdin.write(f"source {files / 'load.tcl'}\n".encode())
        self._read_task = asyncio.create_task(self._read())
        return self
    async def __aexit__(self, exc_type, exc, tb):
        self._done.set()
        self._process.terminate()
    async def _read(self):
        u = Unpacker()
        while not self._process.stdout.at_eof():
            # print("reading stdout")
            data = await self._process.stdout.read(1000)
            u.feed(data)
            for obj in u:
                match obj:
                    case ["result", id, *data]:
                        self._results[id].set_result(data)
                    case ["windowDestroyed", "."]:
                        self._done.set()
                        return
                    case ["callback", cid, args]:
                        # TODO Convert types.
                        asyncio.create_task(self._callbacks[int(cid)](*args))
                    # case _:
                    #     print("unknown")
    async def __call__(self, command, *values):
        if self._read_task.done():
            self._read_task.result()
        full_command = substitute_tcl(command, values)
        # print(full_command)
        for v in values:
            if isfunction(v):
                self._callbacks[id(v)] = v
        rid = self._new_id()
        self._results[rid] = asyncio.Future()
        await self._process.stdin.drain()
        self._process.stdin.write(f"doTcl {rid} {{{full_command}}}\n".encode())
        code, data = await self._results[rid]
        del self._results[rid]
        if code > 0:
            raise TclError(data["info"])
        else:
            return data
    def wait(self):
        return self._done.wait()
