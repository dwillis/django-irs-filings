from django.contrib import admin
from irs.models import F8872, Contribution, Expenditure, Committee


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('EIN', 'name')
    search_fields = ('EIN', 'name')
    readonly_fields = ('EIN',)


@admin.register(F8872)
class F8872Admin(admin.ModelAdmin):
    list_display = ('form_id_number', 'organization_name', 'begin_date',
                    'end_date', 'schedule_a_total', 'schedule_b_total', 'is_amended')
    list_filter = ('is_amended', 'form_type', 'begin_date', 'end_date')
    search_fields = ('form_id_number', 'organization_name', 'EIN')
    readonly_fields = ('form_id_number', 'insert_datetime')
    date_hierarchy = 'end_date'
    raw_id_fields = ('committee', 'amended_by')

    fieldsets = (
        ('Basic Information', {
            'fields': ('form_id_number', 'form_type', 'organization_name', 'EIN', 'committee')
        }),
        ('Period', {
            'fields': ('begin_date', 'end_date', 'quarter_indicator', 'monthly_report_month')
        }),
        ('Totals', {
            'fields': ('schedule_a_total', 'schedule_b_total')
        }),
        ('Indicators', {
            'fields': ('initial_report_indicator', 'amended_report_indicator',
                      'final_report_indicator', 'change_of_address_indicator',
                      'schedule_a_indicator', 'schedule_b_indicator')
        }),
        ('Amendment Info', {
            'fields': ('is_amended', 'amended_by')
        }),
        ('Metadata', {
            'fields': ('insert_datetime',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('contributor_name', 'contribution_amount', 'contribution_date',
                    'organization_name', 'contributor_address_state')
    list_filter = ('contribution_date', 'contributor_address_state', 'entity_type')
    search_fields = ('contributor_name', 'contributor_first_name', 'contributor_last_name',
                    'contributor_corporation_name', 'organization_name', 'EIN')
    readonly_fields = ('schedule_a_id', 'form_id_number', 'record_type')
    date_hierarchy = 'contribution_date'
    raw_id_fields = ('filing', 'committee')

    fieldsets = (
        ('Contributor Information', {
            'fields': ('contributor_name', 'contributor_first_name', 'contributor_last_name',
                      'contributor_middle_name', 'contributor_corporation_name', 'entity_type')
        }),
        ('Contribution Details', {
            'fields': ('contribution_amount', 'contribution_date', 'agg_contribution_ytd',
                      'contributor_employer', 'contributor_occupation')
        }),
        ('Address', {
            'fields': ('contributor_address_line_1', 'contributor_address_line_2',
                      'contributor_address_city', 'contributor_address_state',
                      'contributor_address_zip_code', 'contributor_address_zip_ext'),
            'classes': ('collapse',)
        }),
        ('Filing Information', {
            'fields': ('organization_name', 'EIN', 'committee', 'filing',
                      'form_id_number', 'schedule_a_id', 'record_type')
        }),
    )


@admin.register(Expenditure)
class ExpenditureAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'expenditure_amount', 'expenditure_date',
                    'expenditure_purpose', 'organization_name')
    list_filter = ('expenditure_date', 'recipient_address_state')
    search_fields = ('recipient_name', 'expenditure_purpose', 'organization_name', 'EIN')
    readonly_fields = ('schedule_b_id', 'form_id_number', 'record_type')
    date_hierarchy = 'expenditure_date'
    raw_id_fields = ('filing', 'committee')

    fieldsets = (
        ('Recipient Information', {
            'fields': ('recipient_name', 'recipient_employer', 'recipient_occupation')
        }),
        ('Expenditure Details', {
            'fields': ('expenditure_amount', 'expenditure_date', 'expenditure_purpose')
        }),
        ('Address', {
            'fields': ('recipient_address_line_1', 'recipient_address_line_2',
                      'recipient_address_city', 'recipient_address_state',
                      'recipient_address_zip_code', 'recipient_address_zip_ext'),
            'classes': ('collapse',)
        }),
        ('Filing Information', {
            'fields': ('organization_name', 'EIN', 'committee', 'filing',
                      'form_id_number', 'schedule_b_id', 'record_type')
        }),
    )
