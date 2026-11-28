import os
import tempfile

import pytest

from sandbox.contract import MAX_OUTPUT_CHARS, bound
from sandbox.policy import Policy, PolicyBackend, PolicyError
from sandbox.unsafe_runner import UnsafeSubprocessBackend


def test_forbidden_path_refused():
    r = PolicyBackend(Policy()).run("open('/etc/passwd')", 1)
    assert r.exit_code == 1 and "denied: path" in r.stderr


def test_traversal_refused():
    r = PolicyBackend(Policy()).run("open('/workspace/../etc/shadow')", 1)
    assert r.exit_code == 1


def test_allowed_path_runs():
    assert PolicyBackend(Policy()).run("open('/workspace/a.csv')", 1).exit_code == 0


def test_egress_refused_by_default():
    r = PolicyBackend(Policy()).run("fetch('https://evil.example')", 1)
    assert r.exit_code == 1 and "egress" in r.stderr


def test_egress_allowed_when_configured():
    p = Policy(allow_egress=True)
    assert PolicyBackend(p).run("fetch('https://x.example')", 1).exit_code == 0


def test_private_data_plus_egress_rejected_at_config():
    with pytest.raises(PolicyError):
        Policy(mounts_private_data=True, allow_egress=True)


def test_private_data_alone_and_egress_alone_are_fine():
    Policy(mounts_private_data=True)
    Policy(allow_egress=True)


def test_output_is_bounded():
    text, cut = bound("x" * (MAX_OUTPUT_CHARS + 1))
    assert len(text) == MAX_OUTPUT_CHARS and cut
    assert bound("ok") == ("ok", False)


def test_unsafe_runner_returns_bounded_result():
    r = UnsafeSubprocessBackend().run("print('x' * 5000)", 20)
    assert r.exit_code == 0 and len(r.stdout) == MAX_OUTPUT_CHARS and r.truncated


def test_unsafe_runner_times_out():
    r = UnsafeSubprocessBackend().run("import time; time.sleep(30)", 1)
    assert r.timed_out and r.exit_code is None


def test_unsafe_runner_has_no_containment():
    # The comparison: the same file read the policy backend refuses succeeds here.
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        f.write("secret")
        path = f.name
    try:
        code = f"print(open({path!r}).read())"
        assert PolicyBackend(Policy()).run(code, 1).exit_code == 1
        r = UnsafeSubprocessBackend().run(code, 20)
        assert r.exit_code == 0 and r.stdout.strip() == "secret"
    finally:
        os.unlink(path)
