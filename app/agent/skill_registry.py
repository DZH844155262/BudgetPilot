from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SKILLS_DIR = PROJECT_ROOT / "skills"


def list_skills() -> list[str]:
    """列出当前项目中可用的Skill。"""

    if not SKILLS_DIR.exists():
        return []

    skills = []

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"

        if skill_file.exists():
            skills.append(skill_dir.name)

    return sorted(skills)


def load_skill(
    skill_name: str,
) -> str:
    """读取指定Skill的SKILL.md内容。"""

    cleaned_name = skill_name.strip()

    if not cleaned_name:
        raise ValueError(
            "skill_name不能为空"
        )

    # 防止 ../ 等路径穿越
    if (
        "/" in cleaned_name
        or "\\" in cleaned_name
        or ".." in cleaned_name
    ):
        raise ValueError(
            "非法的skill_name"
        )

    skill_file = (
        SKILLS_DIR
        / cleaned_name
        / "SKILL.md"
    )

    if not skill_file.exists():
        raise ValueError(
            f"未找到Skill: {cleaned_name}"
        )

    content = skill_file.read_text(
        encoding="utf-8"
    ).strip()

    if not content:
        raise ValueError(
            f"Skill内容为空: {cleaned_name}"
        )

    return content
def load_skill_metadata(
    skill_name: str,
) -> dict[str, str]:
    """读取Skill顶部frontmatter中的name和description。"""

    content = load_skill(
        skill_name
    )

    lines = content.splitlines()

    if (
        len(lines) < 3
        or lines[0].strip() != "---"
    ):
        raise ValueError(
            f"Skill缺少frontmatter: {skill_name}"
        )

    metadata: dict[str, str] = {}

    for line in lines[1:]:
        stripped = line.strip()

        if stripped == "---":
            break

        if ":" not in stripped:
            continue

        key, value = stripped.split(
            ":",
            1,
        )

        key = key.strip()
        value = value.strip()

        if key in {
            "name",
            "description",
        }:
            metadata[key] = value

    if not metadata.get("name"):
        raise ValueError(
            f"Skill缺少name: {skill_name}"
        )

    if not metadata.get(
        "description"
    ):
        raise ValueError(
            f"Skill缺少description: {skill_name}"
        )

    return metadata