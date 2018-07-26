#coding:utf-8
from django.db import models
from django import forms
from django.db import connection


# class MyManager(models.Manager):
#     def raw_as_qs(self, raw_query, params=()):
#         """Execute a raw query and return a QuerySet.  The first column in the
#         result set must be the id field for the model.
#         :type raw_query: str | unicode
#         :type params: tuple[T] | dict[str | unicode, T]
#         :rtype: django.db.models.query.QuerySet
#         """
#         cursor = connection.cursor()
#         try:
#             cursor.execute(raw_query, params)
#             return self.filter(id__in=[x[0] for x in cursor])
#         finally:
#             cursor.close()
#
# class MyModel(models.Model):
#     objects = MyManager()
# # class ImportFile(forms.Form):
# #     uploadfile = forms.FileField()
#

# Create your models here.
#select下拉框
class ImportForm(forms.Form):
    Device_type_list = (
        (1, "服务器"),
        (2, "网络设备"),
        (3, "安全设备"),
        (4, "存储设备")
    )

    Permission_Type = (
        (1,"管理员权限"),
        (2,"操作员权限"),
        (3,"审记员权限")
    )

    #固定下拉选项，Device_type为post值，widget为下拉内容，下同。
    device_type = forms.IntegerField(
        widget = forms.Select(choices=Device_type_list)
    )

    PermissionType = forms.IntegerField(
        widget=forms.Select(choices=Permission_Type)
    )

    #动态不定下拉选项
    Dataroom_list = forms.IntegerField(
    widget=forms.Select()
    )
    def __init__(self,*args,**kwargs):
        super(ImportForm,self).__init__(*args,**kwargs)
        #查询数据库获取下拉内容，根据主键basemodel_ptr_id查询获取name字段。并赋值给选项
        self.fields['Dataroom_list'].widget.choices = Dataroom.objects.all().values_list('basemodel_ptr_id','DataroomName')

class CabinetSelect(forms.Form):
    # 机柜动态不定下拉选项
    Cabinet_list = forms.IntegerField(
        widget=forms.Select()
    )
    def __init__(self, *args, **kwargs):
        super(CabinetSelect, self).__init__(*args, **kwargs)
        # 查询数据库获取下拉内容，根据主键basemodel_ptr_id查询获取name字段。并赋值给选项
        self.fields['Cabinet_list'].widget.choices = Cabinet.objects.all().values_list('basemodel_ptr_id', 'CabinetName')

class BaseModel(models.Model):
    delete_flag = models.CharField(max_length=4, verbose_name="删除标志")

class Devices(BaseModel):
    sn = models.CharField(max_length=32, verbose_name="序列号")
    Psn = models.CharField(max_length=32,verbose_name="资产编号")
    DataRoomID = models.IntegerField(verbose_name="机房ID")
    CabinetID = models.IntegerField(verbose_name="机柜ID")
    deviceType = models.IntegerField(verbose_name="设备类型")
    deviceMap = models.CharField(max_length=32, verbose_name="设备位置")
    company = models.CharField(max_length=32, verbose_name="设备品牌")
    model = models.CharField(max_length=32, verbose_name="设备型号")
    deviceSize = models.CharField(max_length=32,verbose_name="设备大小")
    adminIP = models.CharField(max_length=32, verbose_name="管理IP")
    produceIP = models.CharField(max_length=32, verbose_name="业务IP")
    system = models.CharField(max_length=32, verbose_name="操作系统")
    uplinkdev = models.CharField(max_length=32, verbose_name="上联设备SN")
    downlinkdev = models.CharField(max_length=32, verbose_name="下联设备SN")
    updatetime = models.DateField(verbose_name="更新时间")
    deviceUser = models.CharField(max_length=32,verbose_name="设备使用人")
    updateUserID = models.IntegerField(verbose_name="操作员ID")
    deviceDes = models.CharField(max_length=64, verbose_name="设备描述")
    DataRoom = models.CharField(max_length=32, verbose_name="机房位置")
    Cabinetname = models.CharField(max_length=32,verbose_name="机柜号")
    OutMaintain = models.DateField(verbose_name="过保时间")
    isVirtual = models.CharField(max_length=32, verbose_name="是否虚拟化")
    isActive = models.CharField(max_length=32,verbose_name="是否上架")
    Status = models.CharField(max_length=32,verbose_name="运行状态")#正常，异常，故障
    isMaintain = models.CharField(max_length=32,verbose_name="是否在保")
    def getUsername(self):
        return User.objects.get(id=self.updateUserID).username

class DeviceStatus(models.Model):
    Uplinkport = models.CharField(max_length=32, verbose_name="上联口")
    Downlinkport = models.CharField(max_length=32, verbose_name="下联口")
    Cpu = models.CharField(max_length=32, verbose_name="cpu占用率")
    Memory = models.CharField(max_length=32, verbose_name="内存占用率")
    Disk = models.CharField(max_length=32, verbose_name="磁盘占用率")

class Cabinet(BaseModel):
    CabinetName = models.CharField(max_length=32, verbose_name="机柜名称")
    DataRoomID = models.IntegerField(verbose_name="机房ID")
    # Dataroom = models.IntegerField(verbose_name="机房名称")
    Capacity = models.CharField(max_length=32,verbose_name="机柜容量")
    # AbleCapacity = models.CharField(max_length=32,verbose_name="机柜可用量")
    CabinetDes = models.CharField(max_length=64,verbose_name="机柜描述")
    #获取设备数目
    def getdevicescout(self):
        return len(Devices.objects.filter(CabinetID=self.basemodel_ptr_id))
    #获取机房名称
    def getDataRoomName(self):
        return Dataroom.objects.get(basemodel_ptr_id=self.DataRoomID).DataroomName
    #计算剩余可用容量
    def AbleCapcity(self):
        deviceuse = 0
        for device in Devices.objects.filter(CabinetID=self.basemodel_ptr_id):
            devicespace = int(device.deviceSize) + 1
            deviceuse = deviceuse+devicespace
        ablecap =  int(self.Capacity)-deviceuse
        return ablecap

class Dataroom(BaseModel):
    DataroomName = models.CharField(max_length=32,verbose_name="机房名称")
    DataroomDes = models.CharField(max_length=64,verbose_name="机房描述")
    #设备数量
    def getDevicescount(self):
        return len(Devices.objects.filter(DataRoom=self.DataroomName))
    #机柜数量
    def getCabinetcount(self):
        return len(Cabinet.objects.filter(DataRoomID=self.basemodel_ptr_id))

class User(models.Model):
    passwd = models.CharField(max_length=32, verbose_name="密码")
    username = models.CharField(max_length=32, verbose_name="用户名")
    # city = models.CharField(max_length=32, verbose_name="城市")
    email = models.EmailField(verbose_name="邮箱")
    phone = models.CharField(max_length=32,verbose_name="电话")
    def getPermissionID(self):
        return User_Permission.objects.get(userID = self.id).PermissionID
    def getPermission(self):
        PID = User_Permission.objects.get(userID = self.id).PermissionID
        return Permission.objects.get(id = PID).PermissionName

class Group(models.Model):
    groupname = models.CharField(max_length=32, verbose_name="组名称")
    description = models.TextField(verbose_name="组描述")
    class Meta:
        verbose_name = ("组管理")
        verbose_name_plural = ("组管理")

class Permission(models.Model):
    PermissionName = models.CharField(max_length=32, verbose_name="权限名称")
    description = models.TextField(verbose_name="权限描述")
    class Meta:
        verbose_name = ("权限管理")
        verbose_name_plural = ("权限管理")

class User_Group(models.Model):
    userID = models.IntegerField(verbose_name="户ID")
    username = models.CharField(max_length=32, verbose_name="用户名", blank=True)
    groupID = models.IntegerField(verbose_name="组ID")
    groupname = models.CharField(max_length=32, verbose_name="组名称",blank=True)
    class Meta:
        verbose_name = ("用户组管理")
        verbose_name_plural = ("用户组管理")

class User_Permission(models.Model):
    userID = models.IntegerField(verbose_name="用户ID")
    username = models.CharField(max_length=32,verbose_name="用户名",blank=True)
    PermissionID = models.IntegerField(verbose_name="权限ID")
    Permissionname = models.CharField(max_length=32,verbose_name="权限",blank=True)
    class Meta:
        verbose_name = ("用户权限")
        verbose_name_plural = ("用户权限")

class Permission_Group(models.Model):
    PermissionID = models.IntegerField(verbose_name="权限ID")
    Permissionname = models.CharField(max_length=32,verbose_name="权限",blank=True)
    groupID = models.IntegerField(verbose_name="组ID")
    groupname = models.CharField(max_length=32, verbose_name="组名称",blank=True)
    class Meta:
        verbose_name = ("组权限")
        verbose_name_plural = ("组权限")

class UserServer(models.Model):
    userID = models.IntegerField(verbose_name="用户ID")
    serviceID = models.IntegerField(verbose_name="服务ID")

class Log(models.Model):
    ExcelLog = models.TextField(max_length=128,verbose_name="设备导入日志")



