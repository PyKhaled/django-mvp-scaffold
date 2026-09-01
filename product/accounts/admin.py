from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from hijack.contrib.admin import HijackUserAdminMixin
from product.accounts.models import User, Group, UserInformation


admin.site.unregister(User)
admin.site.unregister(Group)

class UserInformationInlineAdmin(admin.StackedInline):
    model = UserInformation
    extra = 1


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin):
    """
    Enhanced Django Group admin with permission management and member tracking.
    """
    list_display = ('name', 'permission_count', 'member_count')
    list_filter = ('permissions__content_type',)
    search_fields = ('name', 'permissions__name')
    filter_horizontal = ('permissions',)
    ordering = ('name',)

    def permission_count(self, obj):
        """Display number of permissions assigned to the group."""
        count = obj.perm_count
        return f"{count} permission{'s' if count != 1 else ''}"
    permission_count.short_description = 'Permissions'

    def member_count(self, obj):
        """Display number of users in the group."""
        count = obj.member_count_val
        return f"{count} member{'s' if count != 1 else ''}"
    member_count.short_description = 'Members'

    def get_queryset(self, request):
        """Optimize queryset with permission and member count annotations."""
        qs = super().get_queryset(request)
        return qs.annotate(
            perm_count=Count('permissions', distinct=True),
            member_count_val=Count('user', distinct=True)
        )


@admin.register(User)
class UserAdmin(HijackUserAdminMixin, DjangoUserAdmin):
    """
    Enhanced User admin with optimized queries, security hardening, and audit features.
    """
    list_display = ("username", "email", "first_name", "last_name", "account_type", "status", "last_login")
    list_filter = ("is_staff", "is_active", "last_login", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-date_joined",)
    inlines = [UserInformationInlineAdmin]
    actions = ['activate', 'deactivate']
    list_per_page = 50
    list_select_related = ('userinformation',)
    raw_id_fields = ()

    @admin.display(description="Status", boolean=True)
    def status(self, obj):
        return obj.is_active

    @admin.display(description="Account type", ordering="is_staff")
    def account_type(self, obj):
        return "Employee" if obj.is_staff else "Customer"

    @admin.action(description="Activate selected users")
    def activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) activated successfully.", messages.SUCCESS)

    @admin.action(description="Deactivate selected users")
    def deactivate(self, request, queryset):
        # Safety check: prevent current user from deactivating themselves
        queryset = queryset.exclude(id=request.user.id)
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated successfully.", messages.SUCCESS)

    def get_queryset(self, request):
        """Optimize queries to prevent N+1 problems."""
        qs = super().get_queryset(request)
        return qs.select_related('userinformation')
