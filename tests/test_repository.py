from analyzer.repository import get_current_commit


def test_get_current_commit():
    repository = "data/real_repos/flask"

    commit = get_current_commit(repository)

    assert commit
    assert len(commit) == 40