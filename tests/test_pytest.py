import tcheck
from crytic_compile import CryticCompile
from crytic_compile.platform.solc_standard_json import SolcStandardJson
from solc_select import solc_select
import subprocess

def run_slither():
    cmd = ['slither', '--detect', 'tcheck', 'detectors/backdoor/0.7.6/My_Strategy.sol']
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def test_slither_output():
    slither_output = run_slither()
    assert "Some expected output" in slither_output



