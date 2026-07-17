import pytest

from hamcrest import (
    assert_that,
    equal_to,
    contains_string,
    is_,
    none,
)

from init_skill import title_case_skill_name, init_skill


@pytest.mark.unit
class TestTitleCaseSkillName:
    """Tests for title_case_skill_name function"""

    @pytest.mark.parametrize("input_name, expected", [
        ("skill", "Skill"),
        ("my-new-skill", "My New Skill"),
        ("api-v2-helper", "Api V2 Helper"),
        ("My-Skill", "My Skill"),
        ("", ""),
    ])
    def test_title_case_conversion(self, input_name, expected):
        result = title_case_skill_name(input_name)
        assert_that(result, equal_to(expected))


@pytest.mark.unit
class TestInitSkill:
    """Tests for init_skill function"""

    def test_complete_directory_structure(self, tmp_path, capsys):
        skill_name = "test-skill"
        skill_display_name = "Test Skill"

        skill_dir = init_skill(skill_name, str(tmp_path))
        print(skill_dir)

        # Verify skill directory
        assert_that(skill_dir, equal_to(tmp_path / skill_name))
        assert_that(skill_dir.exists(), is_(True))

        # Verify SKILL.md
        skill_md = skill_dir / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        assert_that(content, contains_string(skill_name))
        assert_that(content, contains_string(skill_display_name))

        # Verify scripts/ directory
        example_script = skill_dir / "scripts" / "example.py"
        script_content = example_script.read_text(encoding="utf-8")
        assert_that(script_content, contains_string(skill_name))

        # Verify references/ directory
        api_reference = skill_dir / "references" / "api_reference.md"
        ref_content = api_reference.read_text(encoding="utf-8")
        assert_that(ref_content, contains_string(skill_display_name))

        # Verify assets/ directory
        example_asset = skill_dir / "assets" / "example_asset.txt"
        assert_that(example_asset.exists(), is_(True))

        # Verify evals/ directory
        evals_json = skill_dir / "evals" / "evals.json"
        evals_content = evals_json.read_text(encoding="utf-8")
        assert_that(evals_content, contains_string("example-skill"))

        # Verify tests/ directory
        conftest_py = skill_dir / "tests" / "conftest.py"
        conftest_content = conftest_py.read_text(encoding="utf-8")
        assert_that(conftest_content, contains_string(
            "sys.path.insert(0, scripts_dir)"))

        # Verify template files
        readme = skill_dir / "README.md"
        changelog = skill_dir / "CHANGELOG.md"
        license_file = skill_dir / "LICENSE.txt"
        assert_that(readme.exists(), is_(True))
        assert_that(changelog.exists(), is_(True))
        assert_that(license_file.exists(), is_(True))

        # Verify output messages
        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("initialized successfully"))
        assert_that(captured.out, contains_string("Next steps"))

    def test_directory_already_exists(self, tmp_path, capsys):
        skill_name = "existing-skill"

        # Create the directory first
        existing_dir = tmp_path / skill_name
        existing_dir.mkdir()

        result = init_skill(skill_name, str(tmp_path))

        assert_that(result, none())

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string("already exists"))

    def test_mkdir_error(self, tmp_path, mocker, capsys):
        skill_name = "test-skill"

        # Mock mkdir to raise an exception
        mocker.patch(
            "init_skill.Path.mkdir",
            side_effect=PermissionError("Permission denied")
        )

        result = init_skill(skill_name, str(tmp_path))

        assert_that(result, none())

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string(
            "Error creating directory: Permission denied"))

    def test_write_error(self, tmp_path, mocker, capsys):
        skill_name = "test-skill"

        mocker.patch(
            "init_skill.Path.write_text",
            side_effect=IOError("Write error")
        )

        result = init_skill(skill_name, str(tmp_path))

        assert_that(result, none())

        captured = capsys.readouterr()
        assert_that(captured.out, contains_string(
            "Error creating SKILL.md: Write error"))
