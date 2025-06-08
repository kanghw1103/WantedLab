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


