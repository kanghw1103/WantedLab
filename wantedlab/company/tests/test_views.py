import pytest
from asgiref.sync import sync_to_async
from fastapi import HTTPException

from wantedlab.company.models import Company, CompanyTag, Tag
from wantedlab.company.views import CompanyView

pytestmark = [pytest.mark.django_db, pytest.mark.asyncio]


@pytest.fixture(autouse=True)
async def cleanup_database():
    # given
    await sync_to_async(Company.objects.all().delete)()
    await sync_to_async(Tag.objects.all().delete)()
    await sync_to_async(CompanyTag.objects.all().delete)()


@pytest.fixture
async def company() -> Company:
    return await sync_to_async(Company.objects.create)(
        name_ko="원티드랩",
        name_en="Wantedlab",
        name_ja="ウォンテッドラボ",
    )


@pytest.fixture
async def tag() -> Tag:
    return await sync_to_async(Tag.objects.create)(
        name="개발",
        number=1,
    )


@pytest.fixture
async def company_tag(company: Company, tag: Tag) -> CompanyTag:
    return await sync_to_async(CompanyTag.objects.create)(
        company=company,
        tag=tag,
    )


async def test_list_companies_autocomplete(company: Company):
    # given
    company_name = "원티드"
    offset = 0
    limit = 10

    # when
    result = await CompanyView.list_companies_autocomplete(
        company_name=company_name,
        offset=offset,
        limit=limit,
    )

    # then
    assert result.total == 1
    assert result.offset == offset
    assert result.limit == limit
    assert len(result.items) == 1
    assert result.items[0].id == company.id
    assert result.items[0].name_ko == company.name_ko
    assert result.items[0].name_en == company.name_en
    assert result.items[0].name_ja == company.name_ja


async def test_get_company_by_name_ko(company: Company, company_tag: CompanyTag, tag: Tag):
    # given
    company_name = "원티드랩"

    # when
    result = await CompanyView.get_company_by_name(company_name)

    # then
    assert result is not None
    assert result.id == company.id
    assert result.name_ko == company.name_ko
    assert result.name_en == company.name_en
    assert result.name_ja == company.name_ja
    assert len(result.tags) == 1
    assert result.tags[0].id == tag.id
    assert result.tags[0].name == tag.name
    assert result.tags[0].number == tag.number


async def test_get_company_by_name_en(company: Company, company_tag: CompanyTag, tag: Tag):
    # given
    company_name = "Wantedlab"

    # when
    result = await CompanyView.get_company_by_name(company_name)

    # then
    assert result is not None
    assert result.id == company.id
    assert result.name_ko == company.name_ko
    assert result.name_en == company.name_en
    assert result.name_ja == company.name_ja
    assert len(result.tags) == 1
    assert result.tags[0].id == tag.id
    assert result.tags[0].name == tag.name
    assert result.tags[0].number == tag.number


async def test_get_company_by_name_ja(company: Company, company_tag: CompanyTag, tag: Tag):
    # given
    company_name = "ウォンテッドラボ"

    # when
    result = await CompanyView.get_company_by_name(company_name)

    # then
    assert result is not None
    assert result.id == company.id
    assert result.name_ko == company.name_ko
    assert result.name_en == company.name_en
    assert result.name_ja == company.name_ja
    assert len(result.tags) == 1
    assert result.tags[0].id == tag.id
    assert result.tags[0].name == tag.name
    assert result.tags[0].number == tag.number


async def test_get_company_by_name_not_found():
    # given
    company_name = "존재하지 않는 회사"

    # when
    result = await CompanyView.get_company_by_name(company_name)

    # then
    assert result is None


async def test_list_companies_company_by_tag(company: Company, company_tag: CompanyTag, tag: Tag):
    # given
    full_tag = f"tag_{tag.number}"
    offset = 0
    limit = 10

    # when
    result = await CompanyView.list_companies_company_by_tag(
        full_tag=full_tag,
        offset=offset,
        limit=limit,
    )

    # then
    assert result.total == 1
    assert result.offset == offset
    assert result.limit == limit
    assert len(result.items) == 1
    assert result.items[0].id == company.id
    assert result.items[0].name_ko == company.name_ko
    assert result.items[0].name_en == company.name_en
    assert result.items[0].name_ja == company.name_ja
    assert len(result.items[0].tags) == 1
    assert result.items[0].tags[0].id == tag.id
    assert result.items[0].tags[0].name == tag.name
    assert result.items[0].tags[0].number == tag.number


async def test_list_companies_company_by_tag_not_found():
    # given
    full_tag = f"tag_{999}"
    offset = 0
    limit = 10

    # when & then
    with pytest.raises(HTTPException) as exc_info:
        await CompanyView.list_companies_company_by_tag(
            full_tag=full_tag,
            offset=offset,
            limit=limit,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "태그를 찾을 수 없습니다."


async def test_add_company_tag(company: Company, tag: Tag):
    # given
    company_id = company.id
    tag_id = tag.id

    # when
    result = await CompanyView.add_company_tag(company_id, tag_id)

    # then
    assert result.company_id == company_id
    assert len(result.tags) == 1
    assert result.tags[0].name == tag.name
    assert result.tags[0].number == tag.number


async def test_add_company_tag_company_not_found(tag: Tag):
    # given
    company_id = 999
    tag_id = tag.id

    # when & then
    with pytest.raises(HTTPException) as exc_info:
        await CompanyView.add_company_tag(company_id, tag_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "회사를 찾을 수 없습니다."


async def test_add_company_tag_invalid_tag_number(company: Company):
    # given
    company_id = company.id
    tag_id = 999

    # when & then
    with pytest.raises(HTTPException) as exc_info:
        await CompanyView.add_company_tag(company_id, tag_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "태그를 찾을 수 없습니다."


async def test_delete_company_tag(company: Company, company_tag: CompanyTag, tag: Tag):
    # given
    company_id = company.id
    tag_id = tag.id

    # when
    result = await CompanyView.delete_company_tag(company_id, tag_id)

    # then
    assert result.company_id == company_id
    assert len(result.tags) == 0


async def test_delete_company_tag_company_not_found(tag: Tag):
    # given
    company_id = 999
    tag_id = tag.id

    # when & then
    with pytest.raises(HTTPException) as exc_info:
        await CompanyView.delete_company_tag(company_id, tag_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "회사를 찾을 수 없습니다."


async def test_delete_company_tag_tag_not_found(company: Company):
    # given
    company_id = company.id
    tag_id = 999

    # when & then
    with pytest.raises(HTTPException) as exc_info:
        await CompanyView.delete_company_tag(company_id, tag_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "태그를 찾을 수 없습니다."
