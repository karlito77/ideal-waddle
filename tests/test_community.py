from riskintel.community import find_peers, pool_experience, share_issues
from riskintel.community.exchange import band_amount, pseudonym
from riskintel.demo import CONTOSO, FABRIKAM, NORTHWIND


def test_peer_ranking(repo):
    client = repo.get_client(NORTHWIND)
    peers = find_peers(client, repo.list_clients())
    assert [p.peer_id for p in peers][0] == CONTOSO           # same activity, same region
    assert all(p.peer_id != NORTHWIND for p in peers)


def test_pool_respects_consent_and_anonymisation(repo):
    # Northwind asks: Contoso shares aggregated with community, Fabrikam shares nothing
    client = repo.get_client(NORTHWIND)
    pool = pool_experience(repo, NORTHWIND, find_peers(client, repo.list_clients(), min_score=0.0))
    tokens = {s.owner_token for s in pool}
    assert tokens == {"aggregated"}
    assert all(s.banded for s in pool)
    assert len(pool) == len(repo.losses_for(CONTOSO))

    # Contoso asks: Northwind shares pseudonymised with its activity cohort (Contoso qualifies, Fabrikam wouldn't)
    contoso = repo.get_client(CONTOSO)
    pool = pool_experience(repo, CONTOSO, find_peers(contoso, repo.list_clients(), min_score=0.0))
    assert {s.owner_token for s in pool} == {pseudonym(NORTHWIND)}
    assert not any(s.banded for s in pool)

    # Fabrikam asks: activity cohort excludes it from Northwind; Contoso's community share still applies
    fab = repo.get_client(FABRIKAM)
    pool = pool_experience(repo, FABRIKAM, find_peers(fab, repo.list_clients(), min_score=0.0))
    assert {s.owner_token for s in pool} == {"aggregated"}


def test_issue_sharing_location_cohort(repo):
    fab = repo.get_client(FABRIKAM)
    shared = share_issues(repo, FABRIKAM, find_peers(fab, repo.list_clients(), min_score=0.0))
    # Contoso only shares issues with its location cohort; Fabrikam is in another region
    assert {s.owner_token for s in shared} == {pseudonym(NORTHWIND)}


def test_band_amount():
    assert band_amount(500) == 500
    assert band_amount(7_000) == 7_500
    assert band_amount(5_000_000) == 1_500_000
