"""layout.py = layout.ts — hai resolver phải in CÙNG JSON trên cùng thư mục (bun vắng thì bỏ qua nửa ts)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helpers import SCRIPTS, build, clean_env, have, write


def resolve(impl, where, env_extra=None):
    env = clean_env()
    env.update(env_extra or {})
    cmd = [sys.executable, os.path.join(SCRIPTS, "layout.py")] if impl == "py" \
        else ["bun", os.path.join(SCRIPTS, "layout.ts")]
    p = subprocess.run(cmd + [where, "--json"], capture_output=True, text=True, env=env, cwd=where)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def aws_v2(root, spaces=("default",)):
    for s in spaces:
        os.makedirs(os.path.join(root, "aidlc", "spaces", s, "intents"), exist_ok=True)
    write(os.path.join(root, ".claude", "tools", "aidlc-audit.ts"), "// vendor\n")


def contracts(root):
    """Template đội (engine contracts): đúng bộ ba marker mà start_change.py của họ dùng để tìm workspace."""
    write(os.path.join(root, ".agents", "skills", "aidlc", "SKILL.md"), "---\nname: aidlc\n---\n")
    write(os.path.join(root, "docs", "memory", "project.md"), "# project\n")
    write(os.path.join(root, "docs", "intents", "_templates", "intent.md"), "# Intent: [CHANGE_NAME]\n")
    os.makedirs(os.path.join(root, "docs", "intents", "0001-sample"), exist_ok=True)


class Layout(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def both(self, where=None, env_extra=None):
        where = where or self.root
        py = resolve("py", where, env_extra)
        if have("bun"):
            ts = resolve("ts", where, env_extra)
            self.assertEqual(py, ts, "layout.py và layout.ts lệch nhau")
        return py

    def test_nothing(self):
        r = self.both()
        self.assertEqual((r["engine"], r["context_memory"]), ("none", None))

    def test_plain_ai_dlc(self):
        build(self.root)
        r = self.both()
        self.assertEqual(r["engine"], "ai-dlc")
        self.assertTrue(r["context_memory"].endswith(os.path.join(".ai-dlc", "context-memory")))

    def test_found_from_subdirectory(self):
        build(self.root)
        r = self.both(os.path.join(self.root, "src", "api"))
        self.assertEqual((r["engine"], r["root"]), ("ai-dlc", self.root))

    def test_custom_state_via_config_file(self):
        build(self.root)
        os.rename(os.path.join(self.root, ".ai-dlc"), os.path.join(self.root, "docs-state"))
        write(os.path.join(self.root, "ai-dlc.config.json"), json.dumps({"engine": "ai-dlc", "state": "docs-state"}))
        r = self.both()
        self.assertTrue(r["context_memory"].endswith(os.path.join("docs-state", "context-memory")))

    def test_aws_v2_autodetect(self):
        aws_v2(self.root)
        r = self.both()
        self.assertEqual((r["engine"], r["space"]), ("aws-v2", "default"))
        self.assertTrue(r["governance"].endswith(os.path.join(".ai-dlc", "governance")))

    def test_aws_v2_many_spaces_needs_choice(self):
        aws_v2(self.root, spaces=("web", "mobile"))
        r = self.both()
        self.assertEqual(sorted(r["spaces"]), ["mobile", "web"])
        r = self.both(env_extra={"AI_DLC_SPACE": "web"})
        self.assertEqual(r["space"], "web")

    def test_fence_key_value_in_claude_md(self):
        aws_v2(self.root, spaces=("web", "mobile"))
        write(os.path.join(self.root, "CLAUDE.md"), "# Dự án\n\n```ai-dlc\nengine: aws-v2\nspace: mobile\n```\n")
        self.assertEqual(self.both()["space"], "mobile")

    def test_fence_json_in_agents_md(self):
        aws_v2(self.root, spaces=("web", "mobile"))
        write(os.path.join(self.root, "AGENTS.md"), '```ai-dlc\n{"engine": "aws-v2", "space": "web"}\n```\n')
        self.assertEqual(self.both()["space"], "web")

    def test_engine_off(self):
        build(self.root)
        write(os.path.join(self.root, "ai-dlc.config.json"), json.dumps({"engine": "off"}))
        self.assertEqual(self.both()["engine"], "off")

    def test_env_beats_file(self):
        build(self.root)
        write(os.path.join(self.root, "ai-dlc.config.json"), json.dumps({"engine": "ai-dlc"}))
        self.assertEqual(self.both(env_extra={"AI_DLC_ENGINE": "off"})["engine"], "off")

    # ---------- engine contracts (7.0.0-a — template đội) ----------

    def test_contracts_autodetect(self):
        contracts(self.root)
        r = self.both()
        self.assertEqual(r["engine"], "contracts")
        self.assertEqual(r["state"], os.path.join(self.root, "docs", "intents"))
        self.assertEqual(r["skill"], os.path.join(self.root, ".agents", "skills", "aidlc"))
        self.assertEqual(r["memory"], os.path.join(self.root, "docs", "memory"))
        self.assertIsNone(r["context_memory"], "contracts không có context-memory — gói không tạo state riêng")
        self.assertTrue(r["governance"].endswith(os.path.join(".ai-dlc", "governance")))
        self.assertEqual((r["tower"]["port"], r["tower"]["mode"]), (8644, "contracts"))

    def test_contracts_found_from_change_dir(self):
        contracts(self.root)
        r = self.both(os.path.join(self.root, "docs", "intents", "0001-sample"))
        self.assertEqual((r["engine"], r["root"]), ("contracts", self.root))

    def test_contracts_two_markers_are_not_enough(self):
        contracts(self.root)
        os.remove(os.path.join(self.root, "docs", "memory", "project.md"))
        self.assertEqual(self.both()["engine"], "none")

    def test_contracts_explicit_engine_in_config(self):
        contracts(self.root)
        build(self.root)  # .ai-dlc cũ còn nằm đó — config chốt engine của đội
        write(os.path.join(self.root, "ai-dlc.config.json"), json.dumps({"engine": "contracts"}))
        r = self.both()
        self.assertEqual(r["engine"], "contracts")
        self.assertTrue(any("hai nguồn sự thật" in n for n in r["notes"]))

    def test_two_engines_same_dir_ai_dlc_wins_but_warns(self):
        contracts(self.root)
        build(self.root)
        r = self.both()
        self.assertEqual(r["engine"], "ai-dlc")
        self.assertTrue(any("hai nguồn sự thật" in n for n in r["notes"]))

    def test_aws_v2_is_flagged_archived(self):
        aws_v2(self.root)
        self.assertTrue(any("ARCHIVE" in n for n in self.both()["notes"]))


if __name__ == "__main__":
    unittest.main()
