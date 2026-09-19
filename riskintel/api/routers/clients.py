from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from riskintel.api.deps import get_repo
from riskintel.domain import Client, Community, ExposureProfile, SharingConsent
from riskintel.storage import Repository

router = APIRouter(prefix="/clients", tags=["clients"])
community_router = APIRouter(prefix="/communities", tags=["clients"])


@router.post("", response_model=Client, status_code=201)
def create_client(client: Client, repo: Repository = Depends(get_repo)) -> Client:
    return repo.add_client(client)


@router.get("", response_model=list[Client])
def list_clients(repo: Repository = Depends(get_repo)) -> list[Client]:
    return repo.list_clients()


@router.get("/{client_id}", response_model=Client)
def get_client(client_id: str, repo: Repository = Depends(get_repo)) -> Client:
    client = repo.get_client(client_id)
    if client is None:
        raise HTTPException(404, "client not found")
    return client


@router.post("/{client_id}/exposures", response_model=ExposureProfile, status_code=201)
def add_exposure(client_id: str, exposure: ExposureProfile, repo: Repository = Depends(get_repo)) -> ExposureProfile:
    if exposure.client_id != client_id:
        raise HTTPException(400, "client_id mismatch")
    return repo.add_exposure(exposure)


@router.post("/{client_id}/consents", response_model=SharingConsent, status_code=201)
def add_consent(client_id: str, consent: SharingConsent, repo: Repository = Depends(get_repo)) -> SharingConsent:
    if consent.client_id != client_id:
        raise HTTPException(400, "client_id mismatch")
    return repo.add_consent(consent)


@router.get("/{client_id}/consents", response_model=list[SharingConsent])
def list_consents(client_id: str, repo: Repository = Depends(get_repo)) -> list[SharingConsent]:
    return repo.consents_for(client_id)


@community_router.post("", response_model=Community, status_code=201)
def create_community(community: Community, repo: Repository = Depends(get_repo)) -> Community:
    return repo.add_community(community)

