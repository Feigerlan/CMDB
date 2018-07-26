# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('delete_flag', models.CharField(verbose_name='删除标志', max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='DeviceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('Uplinkport', models.CharField(verbose_name='上联口', max_length=32)),
                ('Downlinkport', models.CharField(verbose_name='下联口', max_length=32)),
                ('Cpu', models.CharField(verbose_name='cpu占用率', max_length=32)),
                ('Memory', models.CharField(verbose_name='内存占用率', max_length=32)),
                ('Disk', models.CharField(verbose_name='磁盘占用率', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('groupname', models.CharField(verbose_name='组名称', max_length=32)),
                ('description', models.TextField(verbose_name='组描述')),
            ],
            options={
                'verbose_name': '组管理',
                'verbose_name_plural': '组管理',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('ExcelLog', models.TextField(verbose_name='设备导入日志', max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('PermissionName', models.CharField(verbose_name='权限名称', max_length=32)),
                ('description', models.TextField(verbose_name='权限描述')),
            ],
            options={
                'verbose_name': '权限管理',
                'verbose_name_plural': '权限管理',
            },
        ),
        migrations.CreateModel(
            name='Permission_Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('PermissionID', models.IntegerField(verbose_name='权限ID')),
                ('Permissionname', models.CharField(verbose_name='权限', max_length=32, blank=True)),
                ('groupID', models.IntegerField(verbose_name='组ID')),
                ('groupname', models.CharField(verbose_name='组名称', max_length=32, blank=True)),
            ],
            options={
                'verbose_name': '组权限',
                'verbose_name_plural': '组权限',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('passwd', models.CharField(verbose_name='密码', max_length=32)),
                ('username', models.CharField(verbose_name='用户名', max_length=32)),
                ('email', models.EmailField(verbose_name='邮箱', max_length=254)),
                ('phone', models.CharField(verbose_name='电话', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='User_Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('userID', models.IntegerField(verbose_name='户ID')),
                ('username', models.CharField(verbose_name='用户名', max_length=32, blank=True)),
                ('groupID', models.IntegerField(verbose_name='组ID')),
                ('groupname', models.CharField(verbose_name='组名称', max_length=32, blank=True)),
            ],
            options={
                'verbose_name': '用户组管理',
                'verbose_name_plural': '用户组管理',
            },
        ),
        migrations.CreateModel(
            name='User_Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('userID', models.IntegerField(verbose_name='用户ID')),
                ('username', models.CharField(verbose_name='用户名', max_length=32, blank=True)),
                ('PermissionID', models.IntegerField(verbose_name='权限ID')),
                ('Permissionname', models.CharField(verbose_name='权限', max_length=32, blank=True)),
            ],
            options={
                'verbose_name': '用户权限',
                'verbose_name_plural': '用户权限',
            },
        ),
        migrations.CreateModel(
            name='UserServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('userID', models.IntegerField(verbose_name='用户ID')),
                ('serviceID', models.IntegerField(verbose_name='服务ID')),
            ],
        ),
        migrations.CreateModel(
            name='Cabinet',
            fields=[
                ('basemodel_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='users.BaseModel')),
                ('CabinetName', models.CharField(verbose_name='机柜名称', max_length=32)),
                ('DataRoomID', models.IntegerField(verbose_name='机房ID')),
                ('Capacity', models.CharField(verbose_name='机柜容量', max_length=32)),
                ('CabinetDes', models.CharField(verbose_name='机柜描述', max_length=64)),
            ],
            bases=('users.basemodel',),
        ),
        migrations.CreateModel(
            name='Dataroom',
            fields=[
                ('basemodel_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='users.BaseModel')),
                ('DataroomName', models.CharField(verbose_name='机房名称', max_length=32)),
                ('DataroomDes', models.CharField(verbose_name='机房描述', max_length=64)),
            ],
            bases=('users.basemodel',),
        ),
        migrations.CreateModel(
            name='Devices',
            fields=[
                ('basemodel_ptr', models.OneToOneField(primary_key=True, serialize=False, auto_created=True, parent_link=True, to='users.BaseModel')),
                ('sn', models.CharField(verbose_name='序列号', max_length=32)),
                ('Psn', models.CharField(verbose_name='资产编号', max_length=32)),
                ('DataRoomID', models.IntegerField(verbose_name='机房ID')),
                ('CabinetID', models.IntegerField(verbose_name='机柜ID')),
                ('deviceType', models.IntegerField(verbose_name='设备类型')),
                ('deviceMap', models.CharField(verbose_name='设备位置', max_length=32)),
                ('company', models.CharField(verbose_name='设备品牌', max_length=32)),
                ('model', models.CharField(verbose_name='设备型号', max_length=32)),
                ('deviceSize', models.CharField(verbose_name='设备大小', max_length=32)),
                ('adminIP', models.CharField(verbose_name='管理IP', max_length=32)),
                ('produceIP', models.CharField(verbose_name='业务IP', max_length=32)),
                ('system', models.CharField(verbose_name='操作系统', max_length=32)),
                ('uplinkdev', models.CharField(verbose_name='上联设备SN', max_length=32)),
                ('downlinkdev', models.CharField(verbose_name='下联设备SN', max_length=32)),
                ('updatetime', models.DateField(verbose_name='更新时间')),
                ('deviceUser', models.CharField(verbose_name='设备使用人', max_length=32)),
                ('updateUserID', models.IntegerField(verbose_name='操作员ID')),
                ('deviceDes', models.CharField(verbose_name='设备描述', max_length=64)),
                ('DataRoom', models.CharField(verbose_name='机房位置', max_length=32)),
                ('Cabinetname', models.CharField(verbose_name='机柜号', max_length=32)),
                ('OutMaintain', models.DateField(verbose_name='过保时间')),
                ('isVirtual', models.CharField(verbose_name='是否虚拟化', max_length=32)),
                ('isActive', models.CharField(verbose_name='是否上架', max_length=32)),
                ('Status', models.CharField(verbose_name='运行状态', max_length=32)),
                ('isMaintain', models.CharField(verbose_name='是否在保', max_length=32)),
            ],
            bases=('users.basemodel',),
        ),
    ]
