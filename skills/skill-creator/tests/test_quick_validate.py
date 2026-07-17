import pytest

from hamcrest import (
    assert_that,
    equal_to,
    contains_string,
    is_,
    none,
)

from quick_validate import (
    exact_case_exists,
    check_name_convention,
    validate_skill
)

EXACT_DESCRIPTOIN = "a" * 1024
LONG_DESCRIPTOIN = "a" * 1025
LONG_COMPATIBILITY = "a" * 501


@pytest.mark.unit
class TestExactCaseExists:
    """Tests for exact_case_exists function"""

    def test_path_does_not_exist(self, tmp_path):
        non_existent = tmp_path / "non-existent"
        result = exact_case_exists(non_existent)
        assert_that(result, is_(False))

    @pytest.mark.parametrize("name, expected", [
        ("TestFile.txt", True),
        ("testfile.txt", False),
        ("TESTFILE.TXT", False),
        ("TestFile.TXT", False),
    ])
    def test_file_case_sensitivity(self, tmp_path, name, expected):
        actual_file = tmp_path / "TestFile.txt"
        actual_file.touch()

        test_path = tmp_path / name
        result = exact_case_exists(test_path)
        assert_that(result, is_(expected))

    @pytest.mark.parametrize("dir_name, expected", [
        ("TestDir", True),
        ("testdir", False),
        ("TESTDIR", False),
    ])
    def test_directory_case_sensitivity(self, tmp_path, dir_name, expected):
        actual_dir = tmp_path / "TestDir"
        actual_dir.mkdir()

        test_path = tmp_path / dir_name
        result = exact_case_exists(test_path)
        assert_that(result, is_(expected))

    @pytest.mark.parametrize("filename", [
        "file-with_special.chars.txt",
        "lowercase.txt",
        "UPPERCASE.TXT",
        "MixedCase.File",
    ])
    def test_various_filename_patterns(self, tmp_path, filename):
        test_file = tmp_path / filename
        test_file.touch()

        result = exact_case_exists(test_file)
        assert_that(result, is_(True))


@pytest.mark.unit
class TestCheckNameConvention:
    """Tests for check_name_convention function"""

    @pytest.mark.parametrize("name", [
        "my-skill",
        "skill",
        "my-awesome-skill",
        "skill123",
        "my-skill-v2",
        "a",
        "skill-with-numbers-123",
    ])
    def test_valid_names(self, name):
        is_valid, error_msg = check_name_convention(name)

        assert_that(is_valid, is_(True))
        assert_that(error_msg, none())

    @pytest.mark.parametrize("name,expected_error", [
        ("My-Skill", "kebab-case"),
        ("my_Skill", "kebab-case"),
        ("my skill", "kebab-case"),
        ("MySkill", "kebab-case"),
        ("skill!", "kebab-case"),
        ("skill@name", "kebab-case"),
    ])
    def test_invalid_characters(self, name, expected_error):
        is_valid, error_msg = check_name_convention(name)

        assert_that(is_valid, is_(False))
        assert_that(error_msg, contains_string(expected_error))

    @pytest.mark.parametrize("name,error_contains", [
        ("-skill", "start/end with hyphen"),
        ("skill-", "start/end with hyphen"),
        ("-my-skill-", "start/end with hyphen"),
        ("my--skill", "consecutive hyphens"),
        ("", "empty"),
        ("   ", "empty"),
        ("a" * 65, "too long"),
        (123, "must be a string"),
    ])
    def test_invalid_names(self, name, error_contains):
        is_valid, error_msg = check_name_convention(name)

        assert_that(is_valid, is_(False))
        assert_that(error_msg, contains_string(error_contains))

    @pytest.mark.parametrize("name", [
        "a" * 64,  # exactly 64 characters
        "  my-skill  ",  # with leading/trailing spaces (trimmed)
    ])
    def test_valid_edge_cases(self, name):
        is_valid, error_msg = check_name_convention(name)

        assert_that(is_valid, is_(True))
        assert_that(error_msg, none())


@pytest.mark.unit
class TestValidateSkill:
    """Tests for validate_skill function"""

    def test_valid_skill(self, test_skill):
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(True))
        assert_that(message, equal_to("Skill is valid!"))

    @pytest.mark.parametrize("test_skill, expected_error", [
        ({
            "skill_name": "InvalidSkillName"
        }, "Invalid skill folder name"),
        ({
            "skill_name": "mismatched-skill-test"
        }, "mismatched with folder name"),
        ({
            "skill_md_name": "skill.md"
        }, "SKILL.md not found"),
    ], indirect=["test_skill"])
    def test_folder_and_file_errors(self, test_skill, expected_error):
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(False))
        assert_that(message, contains_string(expected_error))

    def test_missing_skill_md(self, tmp_path):
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        is_valid, message = validate_skill(skill_dir)
        assert_that(is_valid, is_(False))
        assert_that(message, contains_string("SKILL.md not found"))

    @pytest.mark.parametrize("test_skill, expected_error", [
        ({
            "skill_content": "Test Skill"
        }, "No YAML frontmatter"),
        ({
            "skill_content": """Missing opening dashes
name: test-skill
description: A test skill
---
"""
        }, "No YAML frontmatter found"),
        ({
            "skill_content": """---
name: test-skill
description: A test skill
Missing closing dashes
"""
        }, "Invalid frontmatter format"),
        ({
            "skill_content": """---
name: test-skill
description: A test skill
invalid yaml: [unclosed
---
"""
        }, "Invalid YAML"),
    ], indirect=["test_skill"])
    def test_frontmatter_errors(self, test_skill, expected_error):
        """Test frontmatter related errors"""
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(False))
        assert_that(message, contains_string(expected_error))

    @pytest.mark.parametrize("test_skill,expected_error", [
        ({
            "skill_content": """---
description: A test skill
---
"""
        }, "Missing 'name'"),
        ({
            "skill_content": """---
name: test-skill
---
"""
        }, "Missing 'description'"),
        ({
            "skill_content": """---
name: InvalidName
description: A test skill
---
"""
        }, "kebab-case"),
    ], indirect=["test_skill"])
    def test_required_field_errors(self, test_skill, expected_error):
        """Test required field validation errors"""
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(False))
        assert_that(message, contains_string(expected_error))

    @pytest.mark.parametrize("test_skill,expected_valid", [
        ({
            "skill_content": f"""---
name: test-skill
description: {LONG_DESCRIPTOIN}
---
"""
        }, False),
        ({
            "skill_content": f"""---
name: test-skill
description: {EXACT_DESCRIPTOIN}
---
"""
        }, True),
    ], indirect=["test_skill"])
    def test_description_length_validation(self, test_skill, expected_valid):
        """Test description length validation"""
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(expected_valid))
        if not expected_valid:
            assert_that(message, contains_string("too long"))

    @pytest.mark.parametrize("test_skill,expected_error", [
        ({
            "skill_content": """---
name: test-skill
description: 123
---
"""
        }, "must be a string"),
        ({
            "skill_content": f"""---
name: test-skill
description: A test skill
unexpected_field: some value
---
"""
        }, "Unexpected key"),
    ], indirect=["test_skill"])
    def test_field_type_and_property_errors(self, test_skill, expected_error):
        """Test field type and property validation errors"""
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(False))
        assert_that(message, contains_string(expected_error))

    @pytest.mark.parametrize("test_skill", [{
        "skill_content": f"""---
name: test-skill
description: A test skill
license: MIT
allowed-tools: [tool1, tool2]
metadata:
  version: 1.0
  author: test
compatibility: version >= 1.0
---
"""
    }], indirect=True)
    def test_allowed_properties(self, test_skill):
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(True))

    @pytest.mark.parametrize("test_skill", [
        {
            "skill_content": f"""---
name: test-skill
description: >
  A test skill
  with folded block scalar
---
"""
        },
        {
            "skill_content": f"""---
name: test-skill
description: |
  A test skill
  with literal block scalar
---
"""
        },
    ], indirect=["test_skill"])
    def test_allowed_block_scalars(self, test_skill):
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(True))

    @pytest.mark.parametrize("test_skill,expected_error", [
        ({
            "skill_content": f"""---
name: test-skill
description: A test skill
compatibility: {LONG_COMPATIBILITY}
---
"""
        }, "too long"),
        ({
            "skill_content": """---
name: test-skill
description: A test skill
compatibility: 123
---
"""
        }, "must be a string"),
        ({
            "skill_content": """---
- item1
- item2
---
"""
        }, "must be a YAML dictionary"),
    ], indirect=["test_skill"])
    def test_compatibility_and_structure_errors(self, test_skill, expected_error):
        """Test compatibility and structure validation errors"""
        is_valid, message = validate_skill(test_skill)

        assert_that(is_valid, is_(False))
        assert_that(message, contains_string(expected_error))
