import sys
import pytest

from hamcrest import (
    assert_that,
    equal_to,
    contains_string,
)

from init_skill import main


@pytest.mark.e2e
class TestMainCLI:
    """End-to-end tests for main CLI function"""

    def test_with_valid_args(self, tmp_path, mocker, capsys):
        skill_file = "init_skill.py"
        skill_name = "test-skill"

        mocker.patch.object(
            sys, "argv", [skill_file, skill_name, "--path", str(tmp_path)]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(0))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("Initializing skill:"))
        assert_that(captured.out, contains_string(skill_name))
        assert_that(captured.out, contains_string("Location:"))

    def test_missing_args(self, mocker, capsys):
        skill_file = "init_skill.py"
        skill_name = "test-skill"

        # Test missing --path argument
        mocker.patch.object(sys, "argv", [skill_file, skill_name])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(1))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("Usage:"))
        assert_that(captured.out, contains_string("Examples:"))

    def test_with_wrong_args(self, mocker, capsys):
        skill_file = "init_skill.py"
        skill_name = "test-skill"

        mocker.patch.object(
            sys, "argv", [skill_file, skill_name, "--dir", "/some/path"]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(1))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string(
            "Usage: init_skill.py <skill-name> --path <path>"))

    def test_empty_skill_name(self, mocker, tmp_path, capsys):
        skill_file = "init_skill.py"
        skill_name = ""

        mocker.patch.object(
            sys, "argv", [skill_file, skill_name, "--path", str(tmp_path)]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(1))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string(
            "Error: Skill directory already exists"))

    def test_cli_script_execution_help(self, mocker, capsys):
        skill_file = "init_skill.py"
        skill_name = "test-skill"

        mocker.patch.object(
            sys, "argv", [skill_file, skill_name, "--help"]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(1))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("Usage:"))
        assert_that(captured.out, contains_string("Examples:"))
