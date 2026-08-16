def calculate_impact_score(
    direct_impacts: int,
    indirect_impacts: int,
) -> int:
    """
    Calculate a simple explainable impact score.

    Score range: 0-100.
    """

    score = 0

    # Direct dependencies are more important.
    score += direct_impacts * 30

    # Indirect dependencies have lower weight.
    score += indirect_impacts * 15

    # Additional penalty for larger blast radius.
    total_impacts = direct_impacts + indirect_impacts

    if 2 <= total_impacts <= 3:
        score += 10
    elif total_impacts >= 4:
        score += 20

    return min(score, 100)


def get_risk_level(score: int) -> str:
    """
    Convert numerical score into a risk category.
    """

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"