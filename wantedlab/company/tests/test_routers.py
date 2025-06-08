import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from httpx import AsyncClient
from pytest import MonkeyPatch

from wantedlab.company.routers import router
from wantedlab.company.views import CompanyView

pytestmark = [pytest.mark.asyncio]

client = TestClient(router)


@pytest.fixture
async def async_client():
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


async def mock_list_companies_autocomplete(*args, **kwargs):
    return {
        "items": [
            {
                "id": 1,
                "name_ko": "원티드랩",
                "name_en": "Wantedlab",
                "name_ja": "ウォンテッドラボ",
            }
        ],
        "total": 1,
        "offset": 0,
        "limit": 10,
    }


async def mock_get_company_by_name(*args, **kwargs):
    return {
        "id": 1,
        "name_ko": "원티드랩",
        "name_en": "Wantedlab",
        "name_ja": "ウォンテッドラボ",
        "tags": [{"id": 1, "name": "태그1", "number": 1}, {"id": 2, "name": "태그2", "number": 2}],
    }


async def mock_get_company_by_name_not_found(*args, **kwargs):
    return None


async def mock_list_companies_by_tag(*args, **kwargs):
    return {
        "items": [
            {
                "id": 1,
                "name_ko": "원티드랩",
                "name_en": "Wantedlab",
                "name_ja": "ウォンテッドラボ",
                "tags": [{"id": 1, "name": "개발", "number": 1}],
            }
        ],
        "total": 1,
        "offset": 0,
        "limit": 10,
    }


async def mock_add_company_tag(*args, **kwargs):
    return {
        "company_id": 1,
        "tags": [{"id": 1, "name": "태그1", "number": 1}],
    }


async def mock_delete_company_tag(*args, **kwargs):
    return {
        "company_id": 1,
        "tags": [],
    }


def test_list_companies_autocomplete(monkeypatch: MonkeyPatch):
    # given
    company_name = "원티드랩"
    monkeypatch.setattr(
        CompanyView,
        "list_companies_autocomplete",
        mock_list_companies_autocomplete,
    )

    # when
    response = client.get(
        "/companies/search/keyword",
        params={"company_name": company_name},
    )

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [
            {
                "id": 1,
                "name_ko": "원티드랩",
                "name_en": "Wantedlab",
                "name_ja": "ウォンテッドラボ",
            }
        ],
        "total": 1,
        "offset": 0,
        "limit": 10,
    }


def test_search_company_by_name(monkeypatch: MonkeyPatch):
    # given
    company_name = "원티드랩"
    monkeypatch.setattr(
        CompanyView,
        "get_company_by_name",
        mock_get_company_by_name,
    )

    # when
    response = client.get(
        "/companies/search",
        params={"name": company_name},
    )

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": 1,
        "name_ko": "원티드랩",
        "name_en": "Wantedlab",
        "name_ja": "ウォンテッドラボ",
        "tags": [{"id": 1, "name": "태그1", "number": 1}, {"id": 2, "name": "태그2", "number": 2}],
    }


def test_search_company_by_name_not_found(monkeypatch: MonkeyPatch):
    # given
    company_name = "존재하지 않는 회사"
    monkeypatch.setattr(
        CompanyView,
        "get_company_by_name",
        mock_get_company_by_name_not_found,
    )

    # when
    with pytest.raises(HTTPException) as exc_info:
        client.get(
            "/companies/search",
            params={"name": company_name},
        )

    # then
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Company not found"


def test_list_companies_by_tag(monkeypatch: MonkeyPatch):
    # given
    tag = "tag_1"
    monkeypatch.setattr(
        CompanyView,
        "list_companies_company_by_tag",
        mock_list_companies_by_tag,
    )

    # when
    response = client.get(f"/companies/tag/{tag}")

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [
            {
                "id": 1,
                "name_ko": "원티드랩",
                "name_en": "Wantedlab",
                "name_ja": "ウォンテッドラボ",
                "tags": [{"id": 1, "name": "개발", "number": 1}],
            }
        ],
        "total": 1,
        "offset": 0,
        "limit": 10,
    }


def test_add_tag_to_company(monkeypatch: MonkeyPatch):
    # given
    company_id = 1
    tag_request = 1
    monkeypatch.setattr(
        CompanyView,
        "add_company_tag",
        mock_add_company_tag,
    )

    # when
    response = client.post(
        f"/companies/{company_id}/tags",
        json=tag_request,
    )

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "company_id": 1,
        "tags": [{"id": 1, "name": "태그1", "number": 1}],
    }


def test_remove_tag_from_company(monkeypatch: MonkeyPatch):
    # given
    company_id = 1
    tag_id = 1
    monkeypatch.setattr(
        CompanyView,
        "delete_company_tag",
        mock_delete_company_tag,
    )

    # when
    response = client.delete(f"/companies/{company_id}/tags/{tag_id}")

    # then
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "company_id": 1,
        "tags": [],
    }
