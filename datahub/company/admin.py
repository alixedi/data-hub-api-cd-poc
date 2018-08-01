from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from reversion.admin import VersionAdmin

from datahub.core.admin import ReadOnlyAdmin
from datahub.metadata.admin import DisableableMetadataAdmin
from .models import (
    Advisor,
    CompaniesHouseCompany,
    Company,
    CompanyCoreTeamMember,
    Contact,
    ExportExperienceCategory,
)


admin.site.register(ExportExperienceCategory, DisableableMetadataAdmin)


class CompanyCoreTeamMemberInline(admin.TabularInline):
    """Inline admin for CompanyCoreTeamMember"""

    model = CompanyCoreTeamMember
    fields = ('id', 'adviser', )
    extra = 1
    formfield_overrides = {
        models.UUIDField: {'widget': forms.HiddenInput},
    }
    raw_id_fields = (
        'adviser',
    )


@admin.register(Company)
class CompanyAdmin(VersionAdmin):
    """Company admin."""

    search_fields = (
        'name',
        'id',
        'company_number',
    )
    raw_id_fields = (
        'parent',
        'global_headquarters',
        'one_list_account_owner',
        'account_manager',
        'archived_by',
        'created_by',
        'modified_by',
    )
    readonly_fields = (
        'archived_documents_url_path',
        'reference_code',
    )
    list_display = (
        'name',
        'registered_address_country',
    )
    inlines = (
        CompanyCoreTeamMemberInline,
    )


@admin.register(Contact)
class ContactAdmin(VersionAdmin):
    """Contact admin."""

    search_fields = (
        'pk',
        'first_name',
        'last_name',
        'company__pk',
        'company__name',
    )
    raw_id_fields = (
        'company',
        'adviser',
        'archived_by',
        'created_by',
        'modified_by',
    )
    readonly_fields = (
        'archived_documents_url_path',
    )
    list_display = (
        '__str__',
        'company',
    )


@admin.register(CompaniesHouseCompany)
class CHCompany(ReadOnlyAdmin):
    """Companies House company admin."""

    search_fields = ['name', 'company_number']


@admin.register(Advisor)
class AdviserAdmin(VersionAdmin, UserAdmin):
    """Adviser admin."""

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'password'
            )
        }),
        ('Personal info', {
            'fields': (
                'first_name',
                'last_name',
                'contact_email',
                'telephone_number',
                'dit_team'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'dit_team', 'is_active', 'is_staff',)
    search_fields = (
        '=pk',
        'first_name',
        'last_name',
        'email',
        '=dit_team__pk',
        'dit_team__name',
    )
    ordering = ('email',)
