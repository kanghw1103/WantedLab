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


