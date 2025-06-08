from django.db import models


class Company(models.Model):
    name_ko = models.CharField(max_length=150, blank=True, null=True, help_text="한글 회사명")
    name_en = models.CharField(max_length=300, blank=True, null=True, help_text="영문 회사명")
    name_ja = models.CharField(max_length=300, blank=True, null=True, help_text="일본어 회사명")
    tags = models.ManyToManyField(
        "Tag",
        related_name="companies",
        through="CompanyTag",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name_ko or self.name_en or self.name_ja


class Tag(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True, help_text="태그 이름")
    number = models.IntegerField(help_text="태그 번호")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["number"],
                name="unique_tag_number",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.number}"


class CompanyTag(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "tag"],
                name="unique_company_tag",
            )
        ]
