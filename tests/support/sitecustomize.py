"""Install the egress guard in Python subprocesses started by tests.

Tests put this directory on ``PYTHONPATH`` of the child process (see
``tests/support/subprocess_env.py``); Python imports ``sitecustomize`` at start-up, so the
real entry point under test runs with non-loopback sockets blocked (AC-1, AC-8).
"""

import socket_guard

socket_guard.install()
