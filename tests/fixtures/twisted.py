import os
import pytest
import subprocess


@pytest.yield_fixture
def twisted_server(scope="session", autouse=True):
    """
        Using fixture for running server in other process
    """
    twisted_server_cmd = ['python'
                         ,'../../helenae/server.py'
                         ,'9000'
    ]
    twisted_server_proc = subprocess.Popen(twisted_server_cmd
                                          ,stderr=open(os.devnull)
                                          ,stdout=open(os.devnull)
                                          ,shell=False
    )
    yield twisted_server_proc.communicate()[0]