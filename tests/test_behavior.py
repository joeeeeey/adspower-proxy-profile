import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import adspower_profile as cli


class Behavior(unittest.TestCase):
    def test_encoded_proxy_credentials(self):
        p = cli.parse_proxy("socks5://name%40x:pass%3Aword@proxy.example:1080")
        self.assertEqual(p["proxy_user"], "name@x")
        self.assertEqual(p["proxy_password"], "pass:word")

    def test_https_not_silently_downgraded(self):
        self.assertEqual(
            cli.parse_proxy("https://proxy.example:443")["proxy_type"], "https"
        )

    def test_loopback_only(self):
        for origin in [
            "http://evil.test:50325",
            "http://localhost@evil.test",
            "http://127.0.0.1:50325/x",
        ]:
            with self.assertRaises(cli.SafeError):
                cli.local_base(origin)

    def test_no_implicit_launch(self):
        with (
            patch.dict(
                os.environ,
                {"ADSPOWER_PROXY_URL": "http://u:p@proxy.example:8080"},
                clear=True,
            ),
            patch("adspower_profile.call", return_value={"id": "abc"}) as req,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(
                cli.main(["create", "--name", "synthetic", "--execute"]), 0
            )
            req.assert_called_once()
            self.assertEqual(req.call_args.args[1], "/api/v1/user/create")

    def test_dry_run_no_network(self):
        with (
            patch.dict(
                os.environ,
                {"ADSPOWER_PROXY_URL": "http://u:p@proxy.example:8080"},
                clear=True,
            ),
            patch("adspower_profile.call") as req,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(cli.main(["create", "--name", "synthetic"]), 0)
            req.assert_not_called()
