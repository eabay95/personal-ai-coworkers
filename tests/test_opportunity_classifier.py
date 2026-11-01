from tools.opportunity_search import classify_opportunity


def test_internship():
    result = classify_opportunity(
        "Software Engineering Intern"
    )

    assert result == "Internship"


def test_international_false_positive():
    result = classify_opportunity(
        "Applied AI Architect, International Policy"
    )

    assert result is None


def test_research_fellowship():
    result = classify_opportunity(
        "Anthropic Fellows Program, ML Systems"
    )

    assert result == "Research / Fellowship"


def test_unrelated_position():
    result = classify_opportunity(
        "Account Executive, Startups"
    )

    assert result is None