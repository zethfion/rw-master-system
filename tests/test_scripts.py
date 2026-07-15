from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "master-system-builder"
SCRIPTS = SKILL / "scripts"
DIST_VALIDATOR = REPO / "scripts" / "validate_distribution.py"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class ScriptTests(unittest.TestCase):
    def initialize(self, directory: str) -> Path:
        result = run_script(
            "init_master.py",
            "--root",
            directory,
            "--id",
            "sample-expert",
            "--display-name",
            "Sample Expert",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return Path(directory) / "sample-expert"

    def make_mvp(self, package: Path, *, public_source: bool = False) -> None:
        source_path = "public-sources/source.md" if public_source else "corpus/articles/source.md"
        source = package / source_path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("# Source\n\nEvidence anchor.\n", encoding="utf-8")
        (package / "evidence" / "sources.csv").write_text(
            "source_id,title,source_type,url,author,speakers,published_date,access_basis,evidence_level,disposition,local_path,notes\n"
            f"src-1,Synthetic source,article,https://example.invalid/source,Example Author,Example Author,2026-01-01,authorized,primary,accepted,{source_path},synthetic\n",
            encoding="utf-8",
        )
        (package / "evidence" / "claims.csv").write_text(
            "claim_id,claim,status,source_id,anchor,framework_id,notes\n"
            "claim-1,A synthetic claim,explicit,src-1,source.md#evidence,framework-1,fixture\n",
            encoding="utf-8",
        )
        (package / "soul.md").write_text("# Soul\n\nEvidence-backed boundary.\n", encoding="utf-8")
        (package / "index.md").write_text("# Index\n\n- Frameworks are indexed.\n", encoding="utf-8")
        (package / "evidence" / "open-questions.md").write_text(
            "# Open questions\n\n- Which boundary needs more evidence?\n", encoding="utf-8"
        )
        for number in range(1, 4):
            (package / "frameworks" / f"framework-{number}.md").write_text(
                "---\n"
                f"framework: framework-{number}\n"
                "sources:\n"
                f"  - {source_path}#evidence\n"
                "---\n"
                f"# Framework {number}\n\nUse this evidenced method.\n",
                encoding="utf-8",
            )
        (package / "examples" / "consultation.md").write_text(
            "# Synthetic consultation fixture\n\nThe answer cites src-1 and marks uncertainty.\n",
            encoding="utf-8",
        )

    def test_initialize_and_validate_structure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.initialize(directory)
            manifest = json.loads((package / ".master-system.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema"], "rw-master-system/v1")
            self.assertEqual(manifest["generator"]["version"], "0.2.1")
            self.assertFalse(manifest["generator"]["network_telemetry"])
            self.assertFalse(manifest["public_release_allowed"])
            self.assertTrue((package / ".gitignore").is_file())
            self.assertTrue((package / "PRIVACY.md").is_file())

            validation = run_script("validate_master.py", str(package))
            self.assertEqual(validation.returncode, 0, validation.stderr)
            mvp = run_script("validate_master.py", str(package), "--level", "mvp")
            self.assertNotEqual(mvp.returncode, 0)
            self.assertIn("at least one accepted source", mvp.stderr)

    def test_complete_mvp_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.initialize(directory)
            self.make_mvp(package)
            result = run_script("validate_master.py", str(package), "--level", "mvp", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout)["valid"])

    def test_release_requires_explicit_gate_and_sanitized_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.initialize(directory)
            self.make_mvp(package, public_source=True)
            blocked = run_script("validate_master.py", str(package), "--level", "release")
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("public_release_allowed true", blocked.stderr)

            manifest_path = package / ".master-system.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["public_release_allowed"] = True
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            allowed = run_script("validate_master.py", str(package), "--level", "release")
            self.assertEqual(allowed.returncode, 0, allowed.stderr)

            private_source = package / "corpus" / "articles" / "private.md"
            private_source.write_text("private fixture\n", encoding="utf-8")
            private_blocked = run_script("validate_master.py", str(package), "--level", "release")
            self.assertNotEqual(private_blocked.returncode, 0)
            self.assertIn("private directory contains releasable content", private_blocked.stderr)

    def test_refuses_existing_package(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "sample-expert"
            package.mkdir()
            result = run_script(
                "init_master.py",
                "--root",
                directory,
                "--id",
                "sample-expert",
                "--display-name",
                "Sample Expert",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stderr)

    def test_rejects_invalid_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_script(
                "init_master.py",
                "--root",
                directory,
                "--id",
                "Bad ID",
                "--display-name",
                "Bad ID",
            )
            self.assertNotEqual(result.returncode, 0)

    def test_malformed_manifest_and_csv_fail_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.initialize(directory)
            (package / ".master-system.json").write_text("[]\n", encoding="utf-8")
            (package / "evidence" / "sources.csv").write_text(
                "source_id,source_id,title\na,b,c\n", encoding="utf-8"
            )
            result = run_script("validate_master.py", str(package))
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertIn("manifest must be a JSON object", result.stderr)
            self.assertIn("columns do not match", result.stderr)

    def test_audit_detects_secret_email_hidden_text_and_env_variant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env.production").write_text("SYNTHETIC=true\n", encoding="utf-8")
            synthetic_key = "sk-" + "abcdefghijklmnopqrstuvwxyz" + "1234"
            synthetic_email = "contact" + "@" + "private.test"
            (root / "fixture.md").write_text(
                f"synthetic {synthetic_key} {synthetic_email} \u202e\n",
                encoding="utf-8",
            )
            result = run_script("audit_public_release.py", str(root), "--working-tree-only")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("sensitive filename", result.stderr)
            self.assertIn("OpenAI-style key", result.stderr)
            self.assertIn("personal email address", result.stderr)
            self.assertIn("hidden Unicode", result.stderr)

    def test_audit_detects_symlinked_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            (root / "linked").symlink_to(target, target_is_directory=True)
            result = run_script("audit_public_release.py", str(root), "--working-tree-only")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink requires manual review", result.stderr)

    def test_audit_allows_nonsensitive_tooling_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / ".github" / "ISSUE_TEMPLATE" / "config.yml"
            config.parent.mkdir(parents=True)
            config.write_text("blank_issues_enabled: true\n", encoding="utf-8")
            result = run_script("audit_public_release.py", str(root), "--working-tree-only")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_audit_detects_personal_email_in_git_metadata_without_echoing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "README.md").write_text("synthetic fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
            env = os.environ.copy()
            synthetic_email = "person" + "@" + "private.test"
            env.update(
                {
                    "GIT_AUTHOR_NAME": "Synthetic Author",
                    "GIT_COMMITTER_NAME": "Synthetic Author",
                    "GIT_AUTHOR_EMAIL": synthetic_email,
                    "GIT_COMMITTER_EMAIL": synthetic_email,
                }
            )
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "fixture"], check=True, env=env)
            subprocess.run(["git", "-C", str(root), "branch", "exposed-old"], check=True)
            clean_env = os.environ.copy()
            clean_env.update(
                {
                    "GIT_AUTHOR_NAME": "Synthetic Author",
                    "GIT_COMMITTER_NAME": "Synthetic Author",
                    "GIT_AUTHOR_EMAIL": "1+fixture" + "@" + "users.noreply.github.com",
                    "GIT_COMMITTER_EMAIL": "1+fixture" + "@" + "users.noreply.github.com",
                }
            )
            subprocess.run(
                ["git", "-C", str(root), "commit", "-q", "--amend", "--no-edit", "--reset-author"],
                check=True,
                env=clean_env,
            )
            result = run_script("audit_public_release.py", str(root))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("personal email in commit metadata", result.stderr)
            self.assertNotIn(synthetic_email, result.stderr)

    def test_audit_detects_personal_email_in_annotated_tag(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "README.md").write_text("synthetic fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "README.md"], check=True)
            clean_env = os.environ.copy()
            clean_env.update(
                {
                    "GIT_AUTHOR_NAME": "Synthetic Author",
                    "GIT_COMMITTER_NAME": "Synthetic Author",
                    "GIT_AUTHOR_EMAIL": "1+fixture" + "@" + "users.noreply.github.com",
                    "GIT_COMMITTER_EMAIL": "1+fixture" + "@" + "users.noreply.github.com",
                }
            )
            subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "fixture"], check=True, env=clean_env)
            private_email = "tagger" + "@" + "private.test"
            tag_env = clean_env.copy()
            tag_env["GIT_COMMITTER_EMAIL"] = private_email
            subprocess.run(
                ["git", "-C", str(root), "tag", "-a", "private-tag", "-m", "fixture"],
                check=True,
                env=tag_env,
            )
            result = run_script("audit_public_release.py", str(root))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("personal email in tag metadata", result.stderr)
            self.assertNotIn(private_email, result.stderr)

    def test_public_repository_audit(self) -> None:
        result = run_script("audit_public_release.py", str(REPO), "--working-tree-only")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cross_platform_distribution(self) -> None:
        result = subprocess.run(
            [sys.executable, str(DIST_VALIDATOR)], text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
