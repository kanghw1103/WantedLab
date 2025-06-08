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

