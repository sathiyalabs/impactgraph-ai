from analyzer.repository import (
    get_current_commit,
    temporary_checkout,
)


repository = "data/sample_repo"

original = get_current_commit(repository)

print("Before:", original[:8])

old_commit = "b3e3a9c6094292799179ed49ee39e61c7a4766bb"

with temporary_checkout(repository, old_commit):
    print("Inside:", get_current_commit(repository)[:8])

print("After:", get_current_commit(repository)[:8])