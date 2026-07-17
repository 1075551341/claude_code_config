import sys
import pytest

from hamcrest import (
    assert_that,
    equal_to,
    contains_string,
)

from quick_validate import main


@pytest.mark.e2e
class TestMainCLI:
    """End-to-end tests for main CLI function"""

    def test_valid_skill(self, test_skill, mocker, capsys):
        mocker.patch.object(
            sys, "argv", ["quick_validate.py", str(test_skill)]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(0))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("Skill is valid!"))

    def test_invalid_skill(self, tmp_path, mocker, capsys):
        skill_dir = tmp_path / "InvalidSkill"
        skill_dir.mkdir()

        mocker.patch.object(
            sys, "argv", ["quick_validate.py", str(skill_dir)]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(1))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("Invalid skill folder name"))

    def test_missing_args(self, mocker, capsys):
        mocker.patch.object(
            sys, "argv", ["quick_validate.py"]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(1))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("Usage:"))

    def test_too_many_args(self, mocker, capsys):
        mocker.patch.object(
            sys, "argv", ["quick_validate.py", "path1", "path2"]
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert_that(exc_info.value.code, equal_to(1))

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("Usage:"))
