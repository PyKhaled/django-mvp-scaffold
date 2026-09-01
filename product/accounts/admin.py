from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin, GroupAdmin
from hijack.contrib.admin import HijackUserAdminMixin
from product.accounts.models import User, Group, UserInformation

admin.site.unregister(Group)
admin.site.unregister(User)

class UserInformationInlineAdmin(admin.StackedInline):
    model = UserInformation
    extra = 1


@admin.register(Group)
class GroupAdmin(GroupAdmin):
    pass


@admin.register(User)
class UserAdmin(HijackUserAdminMixin, DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "account_type", "status", "last_login")
    list_filter = ("is_staff", "is_active", "last_login", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-date_joined",)
    inlines = [UserInformationInlineAdmin]
    actions = ['activate', 'deactivate']

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
        queryset = queryset.exclude(id=request.user.id)
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated successfully.", messages.SUCCESS)
