from django.contrib import admin
from django.conf.urls import url
from users import models


# Register your models here.
urlpatterns = [
    url(r'^admin/', admin.site.urls)
]

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id','PermissionName','description']

class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ['username','userID','PermissionID',"Permissionname"]

class GroupAdmin(admin.ModelAdmin):
    list_display = ['id','groupname','description']

class UserGroupAdmin(admin.ModelAdmin):
    list_display = ['userID','username','groupID','groupname']

class PermissionGroupAdmin(admin.ModelAdmin):
    list_display = ['groupID','groupname','Permissionname','PermissionID']

admin.site.register(models.Permission,PermissionAdmin)
admin.site.register(models.User_Permission,UserPermissionAdmin)
admin.site.register(models.Group,GroupAdmin)
admin.site.register(models.User_Group,UserGroupAdmin)
admin.site.register(models.Permission_Group,PermissionGroupAdmin)



