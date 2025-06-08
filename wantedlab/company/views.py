from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q, QuerySet
from fastapi import HTTPException

from wantedlab.company.models import TAG_INFO_MAP, Company, CompanyTag
from wantedlab.company.schemas import (
    AutocompletedCompanySchema,
    PaginatedAutocompleteResponse,
    CompanySchema,
    CompanyTagSchema,
    PaginatedCompanyResponse,
    TagUpdateResponse,
)


class CompanyView:
    @staticmethod
    async def list_companies_autocomplete(
        company_name: str,
        offset: int,
        limit: int,
    ) -> PaginatedAutocompleteResponse:
        companies: QuerySet[Company] = await sync_to_async(Company.objects.filter)(
            Q(name_ko__icontains=company_name)
            | Q(name_en__icontains=company_name)
            | Q(name_ja__icontains=company_name)
        )

        total = await sync_to_async(companies.count)()

        paginated_companies = companies[offset : offset + limit]

        items = [
            AutocompletedCompanySchema(
                id=company.id,
                name_ko=company.name_ko,
                name_en=company.name_en,
                name_ja=company.name_ja,
            )
            for company in await sync_to_async(list)(paginated_companies)
        ]

        return PaginatedAutocompleteResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    async def get_company_by_name(company_name: str) -> CompanySchema | None:
        try:
            company: Company = await sync_to_async(Company.objects.get)(
                Q(name_ko=company_name) | Q(name_en=company_name) | Q(name_ja=company_name)
            )
        except Company.DoesNotExist:
            return None
        except Company.MultipleObjectsReturned:
            raise HTTPException(status_code=400, detail="회사를 찾을 수 없습니다.")

        tags = await sync_to_async(list)(company.tags.all())
        return CompanySchema(
            id=company.id,
            name_ko=company.name_ko,
            name_en=company.name_en,
            name_ja=company.name_ja,
            tags=[
                CompanyTagSchema(
                    id=tag.id,
                    name=tag.name,
                    number=tag.number,
                )
                for tag in tags
            ],
        )

