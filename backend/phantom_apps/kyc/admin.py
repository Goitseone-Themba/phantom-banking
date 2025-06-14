from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import KYCRecord, KYCDocument, KYCEvent

@admin.register(KYCRecord)
class KYCRecordAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'status', 'verification_level', 'first_name', 'last_name', 
        'nationality', 'document_type', 'created_at', 'verified_at', 'admin_actions'
    ]
    list_filter = ['status', 'verification_level', 'document_type', 'nationality', 'created_at']
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name', 'document_number']
    readonly_fields = [
        'id', 'user', 'veriff_session_id', 'veriff_session_url', 'veriff_decision', 
        'veriff_code', 'veriff_reason', 'created_at', 'updated_at', 'verified_at'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'user', 'status', 'verification_level')
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'nationality')
        }),
        ('Document Information', {
            'fields': ('document_type', 'document_number')
        }),
        ('Address Information', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state_province', 'postal_code', 'country')
        }),
        ('Veriff Integration', {
            'fields': ('veriff_session_id', 'veriff_session_url', 'veriff_decision', 'veriff_code', 'veriff_reason'),
            'classes': ('collapse',)
        }),
        ('Risk Assessment', {
            'fields': ('risk_score', 'risk_level'),
            'classes': ('collapse',)
        }),
        ('Admin Section', {
            'fields': ('reviewed_by', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'verified_at', 'expires_at'),
            'classes': ('collapse',)
        })
    )

    def admin_actions(self, obj):
        if obj.status == KYCRecord.Status.PENDING:
            approve_url = reverse('admin:kyc_approve', args=[obj.id])
            reject_url = reverse('admin:kyc_reject', args=[obj.id])
            return format_html(
                '<a class="button" href="{}">Approve</a> '
                '<a class="button" href="{}">Reject</a>',
                approve_url, reject_url
            )
        return format_html('<span style="color: green;">Processed</span>')
    admin_actions.short_description = 'Actions'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:kyc_id>/approve/', self.admin_site.admin_view(self.approve_kyc), name='kyc_approve'),
            path('<uuid:kyc_id>/reject/', self.admin_site.admin_view(self.reject_kyc), name='kyc_reject'),
        ]
        return custom_urls + urls

    def approve_kyc(self, request, kyc_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        
        kyc_record = KYCRecord.objects.get(id=kyc_id)
        kyc_record.approve(reviewed_by=request.user)
        messages.success(request, f'KYC approved for {kyc_record.user.username}')
        return redirect('admin:kyc_kycrecord_changelist')

    def reject_kyc(self, request, kyc_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        
        kyc_record = KYCRecord.objects.get(id=kyc_id)
        kyc_record.reject(reason="Manually rejected by admin", reviewed_by=request.user)
        messages.warning(request, f'KYC rejected for {kyc_record.user.username}')
        return redirect('admin:kyc_kycrecord_changelist')


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ['kyc_record', 'document_type', 'file_name', 'uploaded_at', 'verified']
    list_filter = ['document_type', 'verified', 'uploaded_at']
    search_fields = ['kyc_record__user__username', 'file_name']


@admin.register(KYCEvent)
class KYCEventAdmin(admin.ModelAdmin):
    list_display = ['kyc_record', 'event_type', 'description', 'created_at', 'created_by']
    list_filter = ['event_type', 'created_at']
    search_fields = ['kyc_record__user__username', 'description']
    readonly_fields = ['kyc_record', 'event_type', 'description', 'metadata', 'created_at', 'created_by']
