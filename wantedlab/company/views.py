from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q, QuerySet
from fastapi import HTTPException

from wantedlab.company.models import TAG_INFO_MAP, Company, CompanyTag, Tag
from wantedlab.company.schemas import (
    AutocompletedCompanySchema,
    CompanySchema,
    CompanyTagSchema,
    PaginatedAutocompleteResponse,
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

    @staticmethod
    async def list_companies_company_by_tag(
        full_tag: str,
        offset: int,
        limit: int,
    ) -> PaginatedCompanyResponse:
        try:
            _, number = full_tag.split("_")
            tag: Tag = await sync_to_async(Tag.objects.get)(number=int(number))
            companies: QuerySet[Company] = await sync_to_async(tag.companies.all)()

            total = await sync_to_async(companies.count)()

            if not total:
                return PaginatedCompanyResponse(
                    items=[],
                    total=0,
                    limit=limit,
                    offset=offset,
                )

            paginated_companies = companies[offset : offset + limit]
            companies_list = await sync_to_async(list)(paginated_companies)

            items = []
            for company in companies_list:
                tags = await sync_to_async(list)(company.tags.all())
                items.append(
                    CompanySchema(
                        id=company.id,
                        name_ko=company.name_ko,
                        name_en=company.name_en,
                        name_ja=company.name_ja,
                        tags=[CompanyTagSchema(id=tag.id, name=tag.name, number=tag.number) for tag in tags],
                    )
                )

            return PaginatedCompanyResponse(
                items=items,
                total=total,
                limit=limit,
                offset=offset,
            )
        except Tag.DoesNotExist:
            raise HTTPException(status_code=404, detail="태그를 찾을 수 없습니다.")

    @staticmethod
    async def add_company_tag(company_id: int, tag_id: int) -> TagUpdateResponse:
        try:
            company: Company = await sync_to_async(Company.objects.get)(id=company_id)
            tag: Tag = await sync_to_async(Tag.objects.get)(id=tag_id)
            await sync_to_async(company.tags.add)(tag)
            return await CompanyView._company_tag_response(company, company_id)

        except Company.DoesNotExist:
            raise HTTPException(status_code=404, detail="회사를 찾을 수 없습니다.")
        except Tag.DoesNotExist:
            raise HTTPException(status_code=404, detail="태그를 찾을 수 없습니다.")
        except IntegrityError:
            raise HTTPException(status_code=400, detail="태그가 이미 존재합니다.")

    @staticmethod
    async def delete_company_tag(company_id: int, tag_id: int) -> TagUpdateResponse:
        try:
            company: Company = await sync_to_async(Company.objects.get)(id=company_id)
            tag: Tag = await sync_to_async(Tag.objects.get)(id=tag_id)
            await sync_to_async(company.tags.remove)(tag)
            return await CompanyView._company_tag_response(company, company_id)
        except Company.DoesNotExist:
            raise HTTPException(status_code=404, detail="회사를 찾을 수 없습니다.")
        except Tag.DoesNotExist:
            raise HTTPException(status_code=404, detail="태그를 찾을 수 없습니다.")

    @staticmethod
    async def _company_tag_response(company: Company, company_id: int) -> TagUpdateResponse:
        tags = await sync_to_async(list)(company.tags.all())
        tag_schemas = [
            CompanyTagSchema(
                id=tag.id,
                name=tag.name,
                number=tag.number,
            )
            for tag in tags
        ]
        return TagUpdateResponse(company_id=company_id, tags=tag_schemas)
