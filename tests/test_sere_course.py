"""Tests for sere_course.py — the college course holds together."""

from sere_aries import PROFESSOR_NOTES
from sere_course import UNITS, LESSONS, lesson_plan, syllabus, validate_curriculum


def test_curriculum_validates_clean():
    assert validate_curriculum() == []


def test_six_units_twentysix_lessons():
    assert len(UNITS) == 6
    assert len(LESSONS) == 26


def test_every_lesson_technique_exists():
    for lid, lesson in LESSONS.items():
        t = lesson["technique"]
        assert t is None or t in PROFESSOR_NOTES, lid


def test_defense_requires_offense_first():
    # The course rule: a defense lesson must have an offense lesson in its
    # prerequisite ancestry — you cannot defend what you have not wielded.
    # For ATT&CK techniques the bar is stricter: the offense lesson must be
    # on the SAME technique. (Quantum/standards lessons wield conceptually —
    # nobody hands a trainee a quantum computer.)
    def ancestry(lid, seen=None):
        seen = seen or set()
        for req in LESSONS[lid]["requires"]:
            seen.add(req)
            ancestry(req, seen)
        return seen

    for lid, lesson in LESSONS.items():
        if lesson["side"] != "defense":
            continue
        anc = ancestry(lid)
        assert any(LESSONS[a]["side"] == "offense" for a in anc), \
            f"{lid}: no offense lesson in ancestry"
        if lesson["technique"] and lesson["technique"].startswith("T"):
            assert any(
                LESSONS[a]["side"] == "offense"
                and LESSONS[a]["technique"] == lesson["technique"]
                for a in anc
            ), f"{lid}: no prior offense lesson on technique"


def test_every_unit_has_both_sides():
    for unit in (UNITS[0], UNITS[1], UNITS[2], UNITS[4]):
        sides = {LESSONS[lid]["side"] for lid in unit["lessons"]}
        assert "offense" in sides and "defense" in sides, unit["title"]


def test_lesson_plan_renders_lecture_lab_sparring():
    plan = lesson_plan("2.1")
    assert "LECTURE" in plan and "LAB" in plan and "SPARRING" in plan
    assert "T1566" in plan  # the lecture pulls the professor's notes
    assert "Prerequisites" in plan
    capstone = lesson_plan("4.2")
    assert "crucible" in capstone


def test_syllabus_lists_everything():
    catalog = syllabus()
    assert "SERE-101" in catalog
    for lid in LESSONS:
        assert lid in catalog


def test_every_lesson_lab_and_sparring_present():
    for lid, lesson in LESSONS.items():
        assert lesson["lab"].strip(), f"{lid}: lab empty"
        assert lesson["artifact"].strip(), f"{lid}: artifact empty"
        assert lesson["sparring"].strip(), f"{lid}: sparring empty"


def test_lesson_plan_renders_every_technique_lesson():
    for lid, lesson in LESSONS.items():
        if lesson["technique"]:
            plan = lesson_plan(lid)  # must not KeyError on professor notes
            assert "LECTURE" in plan and "LAB" in plan and "SPARRING" in plan, lid
