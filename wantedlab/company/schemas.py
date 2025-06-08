from pydantic import BaseModel, Field


class AutocompletedCompanySchema(BaseModel):
    id: int
    name_ko: str | None
    name_en: str | None
    name_ja: str | None


class PaginatedAutocompleteResponse(BaseModel):
    items: list[AutocompletedCompanySchema]
    total: int
    limit: int
    offset: int


class CompanyTagSchema(BaseModel):
    id: int
    name: str
    number: int


class CompanySchema(BaseModel):
    id: int
    name_ko: str | None
    name_en: str | None
    name_ja: str | None
    tags: list[CompanyTagSchema] | None


class PaginatedCompanyResponse(BaseModel):
    items: list[CompanySchema]
    total: int
    limit: int
    offset: int


