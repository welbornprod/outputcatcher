#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from io import UnsupportedOperation

__version__ = '0.0.5'


def escape_output(s):
    """ Escape output using python's repr(). """
    return repr(s)[1:-1]


class StdOutCatcher(object):
    """ Catches stdout for code inside the 'with' block.

        Usage:
            with StdOutCatcher(safe=True, maxlength=160) as fakestdout:
                # stdout is stored in fakestdout.output
                print('okay')
            # stdout is back to normal
            # retrieve the captured output..
            print('output was: {}'.format(fakestdout.output))
    """
    def __init__(self, escaped=False, max_length=160):
        # Use safe_output?
        self.escaped = escaped
        # Maximum length before trimming output
        self.max_length = max_length
        # Output
        self._output = ''
        self.length = 0
        self.max_exceeded = False

    def __enter__(self):
        # Replace fileobj with self, fileobj.write() will be self.write()
        sys.stdout = self
        return self

    def __exit__(self, type, value, traceback):
        # Fix stdout.
        sys.stdout = sys.__stdout__

    def flush(self):
        """ Doesn't do anything, but it's here for compatibility. """
        return None

    @property
    def name(self):
        return getattr(
            sys.stdout,
            'name',
            getattr(sys.stdout, '__name__', type(sys.stdout).__name__)
        )

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        """ Sets self._output, escaping first if self.escaped is truthy. """
        if self.escaped:
            self._output = escape_output(value)
            return None
        self._output = value
        return None

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError('write() expects a str, got: {}'.format(
                type(s).__name__
            ))
        if (not s) or self.max_exceeded:
            # Nothing to write, or max-length was already exceeded.
            return 0

        # Save output
        self.output = ''.join((
            self.output,
            s
        ))
        # Trim and block the next call if we are already at max_length.
        if len(self.output) >= self.max_length:
            self.output = self.output[:self.max_length]
            self.max_exceeded = True
        self.length = len(self.output)
        return len(s)


class StdErrCatcher(StdOutCatcher):
    def __enter__(self):
        # Replace stderr with self, stderr.write() will be self.write()
        sys.stderr = self
        return self

    def __exit__(self, type, value, traceback):
        # Fix stderr.
        sys.stderr = sys.__stderr__

    @property
    def name(self):
        return getattr(
            sys.stderr,
            'name',
            getattr(sys.stderr, '__name__', type(sys.stderr).__name__)
        )
