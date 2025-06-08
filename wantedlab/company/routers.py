from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status

from wantedlab.company.schemas import (
    CompanySchema,
    PaginatedAutocompleteResponse,
    PaginatedCompanyResponse,
    TagUpdateResponse,
)

from .views import CompanyView

router = APIRouter(
    prefix="/companies",
    tags=["companies"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/search/keyword",
    response_model=PaginatedAutocompleteResponse,
    summary="회사 자동완성 검색",
    description="회사 이름으로 자동완성 검색을 수행합니다. 페이지네이션을 지원합니다.",
    responses={
        200: {
            "description": "성공적으로 회사 목록을 반환",
            "content": {
                "application/json": {
                    "example": {
                        "items": [{"id": 1, "name": "원티드랩"}, {"id": 2, "name": "원티드"}],
                        "total": 2,
                        "offset": 0,
                        "limit": 10,
                    }
                }
            },
        }
    },
)
async def list_companies_autocomplete(
    company_name: Annotated[str, Query(description="검색할 회사 이름 (부분 일치)")],
    offset: Annotated[int, Query(ge=0, description="건너뛸 항목 수")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="반환할 최대 항목 수")] = 10,
) -> PaginatedAutocompleteResponse:
    return await CompanyView.list_companies_autocomplete(
        company_name=company_name,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/search",
    response_model=CompanySchema,
    status_code=status.HTTP_200_OK,
    summary="회사 정보 검색",
    description="회사 이름으로 정확한 회사 정보를 검색합니다.",
    responses={
        404: {
            "description": "회사를 찾을 수 없음",
            "content": {"application/json": {"example": {"detail": "Company not found"}}},
        }
    },
)
async def search_company_by_name(
    name: Annotated[str, Query(min_length=1, description="검색할 회사의 정확한 이름")],
):
    company = await CompanyView.get_company_by_name(name)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.get(
    "/tag/{tag}",
    response_model=PaginatedCompanyResponse,
    summary="태그로 회사 검색",
    description="특정 태그가 지정된 모든 회사를 검색합니다. 페이지네이션을 지원합니다.",
)
async def list_companies_by_tag(
    tag: Annotated[str, Path(description="검색할 태그")],
    offset: Annotated[int, Query(ge=0, description="건너뛸 항목 수")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="반환할 최대 항목 수")] = 10,
) -> PaginatedCompanyResponse:
    return await CompanyView.list_companies_company_by_tag(
        full_tag=tag,
        offset=offset,
        limit=limit,
    )


@router.post(
    "/{company_id}/tags",
    response_model=TagUpdateResponse,
    status_code=status.HTTP_200_OK,
    summary="회사에 태그 추가",
    description="지정된 회사에 새로운 태그를 추가합니다.",
    responses={404: {"description": "회사를 찾을 수 없음"}, 400: {"description": "잘못된 태그 요청"}},
)
async def add_tag_to_company(
    company_id: Annotated[int, Path(description="태그를 추가할 회사 ID")],
    tag_id: Annotated[int, Body(description="추가할 태그 ID")],
):
    return await CompanyView.add_company_tag(company_id, tag_id)


@router.delete(
    "/{company_id}/tags/{tag_id}",
    response_model=TagUpdateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회사에서 태그 제거",
    description="지정된 회사에서 특정 태그를 제거합니다.",
    responses={
        404: {"description": "회사 또는 태그를 찾을 수 없음"},
    },
)
async def remove_tag_from_company(
    company_id: Annotated[int, Path(description="태그를 제거할 회사 ID")],
    tag_id: Annotated[int, Path(description="제거할 태그 ID")],
):
    return await CompanyView.delete_company_tag(company_id, tag_id)
