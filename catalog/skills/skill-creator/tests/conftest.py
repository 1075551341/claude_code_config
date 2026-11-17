import sys
import pytest

from pathlib import Path

# This dynamically finds the scripts folder
scripts_dir = str(Path(__file__).parent.parent / "scripts")

# Injects the scripts folder into the Python path so 'from <sut> import...' works
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)


@pytest.fixture
def test_skill(tmp_path, request):
    """Create a skill directory for testing with customizable parameters"""
    skill_name = getattr(request, 'param', {}).get('skill_name', 'test-skill')
    skill_md_name = getattr(request, 'param', {}).get(
        'skill_md_name', 'SKILL.md')
    skill_content = getattr(request, 'param', {}).get('skill_content', """---
name: test-skill
description: A test skill for validation
---

# Test Skill

This is a test skill.
""")

    skill_dir = tmp_path / skill_name
    skill_dir.mkdir()

    skill_md = skill_dir / skill_md_name
    skill_md.write_text(skill_content, encoding="utf-8")

    return skill_dir
