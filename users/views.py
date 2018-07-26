#coding:utf-8
# Create your views here.
from django.shortcuts import render,render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse
from .models import User as Users
import datetime
from  .models import *
from django.http import JsonResponse
from io import StringIO, BytesIO
import xlwt
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import xlrd
from xlrd import xldate_as_datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

##############################################################################################################
#工具函数
def get_len(rawqueryset):
    def __len__(self):
        params = ["""'%s'""" % p for p in self.params]
        sql = 'SELECT COUNT(*) FROM (' + (rawqueryset.raw_query % tuple(params)) + ') B;'
        cursor = connection.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        return row[0]
    return __len__
#导出Excel
def output(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=Devices.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet(u'Sheet1')
    sheet.write(0, 0, '*basemodel_ptr_id*')
    sheet.write(0, 1, '*sn*')
    sheet.write(0, 2, 'Psn')
    sheet.write(0, 3, '*DataRoomID*')
    sheet.write(0, 4, '*CabinetID*')
    sheet.write(0, 5, 'deviceType*')
    sheet.write(0, 6, 'deviceMap')
    sheet.write(0, 7, 'company')
    sheet.write(0, 8, 'model')
    sheet.write(0, 9, '*deviceSize*')
    sheet.write(0, 10, 'adminIP')
    sheet.write(0, 11, 'produceIP')
    sheet.write(0, 12, 'system')
    sheet.write(0, 13, 'uplinkdev')
    sheet.write(0, 14, 'downlinkdev')
    sheet.write(0, 15, '*updatetime*')
    sheet.write(0, 16, 'deviceUser')
    sheet.write(0, 17, 'updateUserID')
    sheet.write(0, 18, 'deviceDes')
    sheet.write(0, 19, '*DataRoom*')
    sheet.write(0, 20, '*Cabinetname*')
    sheet.write(0, 21, '*OutMaintain*')
    sheet.write(0, 22, 'isVirtual')
    sheet.write(0, 23, 'isActive')
    sheet.write(0, 24, 'Status')
    sheet.write(0, 25, 'isMaintain')

    row = 1
    for i in Devices.objects.all():
        sheet.write(row, 0, i.basemodel_ptr_id)
        sheet.write(row, 1, i.sn)
        sheet.write(row, 2, i.Psn)
        sheet.write(row, 3, i.DataRoomID)
        sheet.write(row, 4, i.CabinetID)
        sheet.write(row, 5, i.deviceType)
        sheet.write(row, 6, i.deviceMap)
        sheet.write(row, 7, i.company)
        sheet.write(row, 8, i.model)
        sheet.write(row, 9, i.deviceSize)
        sheet.write(row, 10, i.adminIP)
        sheet.write(row, 11, i.produceIP)
        sheet.write(row, 12, i.system)
        sheet.write(row, 13, i.uplinkdev)
        sheet.write(row, 14, i.downlinkdev)
        sheet.write(row, 15, i.updatetime)
        sheet.write(row, 16, i.deviceUser)
        sheet.write(row, 17, i.updateUserID)
        sheet.write(row, 18, i.deviceDes)
        sheet.write(row, 19, i.DataRoom)
        sheet.write(row, 20, i.Cabinetname)
        sheet.write(row, 21, i.OutMaintain)
        sheet.write(row, 22, i.isVirtual)
        sheet.write(row, 23, i.isActive)
        sheet.write(row, 24, i.Status)
        sheet.write(row, 25, i.isMaintain)
        row += 1
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response
#导入Excel
def outputCabinets(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=Cabinets.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet(u'Sheet1')
    sheet.write(0, 0, '*basemodel_ptr_id*')
    sheet.write(0, 1, '*CabinetName*')
    sheet.write(0, 2, '*DataRoomID*')
    sheet.write(0, 3, '*Capacity*')
    sheet.write(0, 4, 'CabinetDes')

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response
#日志记录：
def WriteLog(str):
    log = Log()
    log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ":"+str+"</br>"
    log.save()

##############################################################################################################

#session登录装饰器
def valid_login(func):
    def inner(request):
        user = request.session.get("username","")
        if user: #如果user不为空
            userData = Users.objects.get(username = user)
            all_dict = {
                "user" : userData.username,
                "passwd" : userData.passwd,
                "email" : userData.email,
                "phone" : userData.phone,
                "permission": userData.getPermissionID(),
            }
            request.session["UserData"] = all_dict
            return func(request)
        else:
            return HttpResponseRedirect("/user/login")
    return inner
#权限判定
def isPermission(val):
    if val == 1:
        return True
    else:
        return False

def userValid(user):
    userlist = Users.objects.filter(username = user) # select * from Users where username = user;
    if userlist:
        # return {"passwd" : userlist[0].passwd}
        return True
    else:
        return False

def basemodelValid(id):

    if Dataroom.objects.filter(basemodel_ptr_id=id).exists():
        return 2
    elif Cabinet.objects.filter(basemodel_ptr_id=id).exists():
        return 3
    elif Devices.objects.filter(basemodel_ptr_id=id).exists():
        return 4
    else:
        pass

#登录逻辑
def login(request):
    if request.method == "POST" and request.POST:
        #获取用户提交上来的用户名和密码
        user = request.POST["user"]
        if user == "":
            return render_to_response("signin.html", {'script': "alert", 'wrong': '用户名为空'})
        else:
            password = request.POST["password"]
            if userValid(user): #如果用户存在
                data = Users.objects.get(username=user) #通过用户类对象获取用户名
                passwd = data.passwd
                if passwd == password: #判断密码相同
                    response = HttpResponseRedirect("/user/index") #实例化一个reponse响应
                    response.set_cookie("user",user) #对应响应设置cookie
                    request.session["username"] = user #设置session
                    log = Log()
                    log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +user+":登录成功</br>"
                    log.save()
                    return response  #返回首页
                elif not passwd == password:
                    return render_to_response("signin.html", {'script': "alert", 'wrong': '密码错误'})
                else:
                    return render_to_response("index.html",locals())
            else:
                return render_to_response("signin.html",{'script':"alert",'wrong':'账号不存在'})
    else:
        return render_to_response("signin.html",locals())

def logout(request):
    del request.session["username"]
    log = Log()
    log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +  ":登出</br>"
    log.save()
    return HttpResponseRedirect('/user/login')
#注册逻辑
def register(request):
    if request.method == "POST" and request.POST:
        if not request.POST["user"] == "" and not request.POST["passwd"] == "" and not request.POST["email"] == "" and not request.POST["phone"] == "":
            if User.objects.all().values('username'):
                u=Users()
                u.username=request.POST["user"]
                u.passwd=request.POST["passwd"]
                u.email=request.POST["email"]
                u.phone=request.POST["phone"]
                u.save()
                P = User_Permission()
                P.userID = User.objects.get(username=request.POST["user"]).id
                P.PermissionID = 2
                P.save()
            else:
                u = Users()
                u.username = request.POST["user"]
                u.passwd = request.POST["passwd"]
                u.email = request.POST["email"]
                u.phone = request.POST["phone"]
                u.save()
                P = User_Permission()
                P.userID = User.objects.get(username=request.POST["user"]).id
                P.PermissionID = 1
                P.save()
        else:
            return render_to_response("signup.html", {'script': "alert", 'wrong': '请填写完整信息'})
        # return render_to_response("signin.html", locals())
        return HttpResponseRedirect("/user/login")

    else:
        return render_to_response("signup.html",locals())

@valid_login
def UserList(request):
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    userdata = User.objects.all()
    return render_to_response("UserList.html",locals())

@valid_login
def UserEdit(request):
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    userdata = User.objects.all()
    return render_to_response("UserEdit.html",locals())

@valid_login
def GroupList(request):
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    Groupdata = Group.objects.all()
    return render_to_response("GroupList.html",locals())

#机房select
def dataroomselect(request):
    dataroomList = Dataroom.objects.all()
    list1 = []
    for item in dataroomList:
        list1.append([item.basemodel_ptr_id,item.DataroomName])
    # print(list1)
    return JsonResponse({'data': list1 })
#机柜select
def cabinetselect(request,pid):
    # print(pid)
    cabinetList = Cabinet.objects.filter(DataRoomID=pid)
    list1 = []
    for item in cabinetList:
        list1.append([item.basemodel_ptr_id,item.CabinetName])
    return JsonResponse({'data': list1})
#日志显示
def GetDeviceLog(request):
    Deviceslog = Log.objects.all().values("ExcelLog")
    list1 = []
    for item in Deviceslog:
        # print(type(item))
        list1.append(item['ExcelLog'])
    list2 = list1[-20:]
    # print(list2)
    return JsonResponse({'dic' : "".join(list2)})

#首页
@valid_login
def index(request):
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    user = request.session["UserData"]["user"]
    # user = request.COOKIES.get("user","None")
    # if request.session.get("username",""):
    #     return render_to_response("index.html",locals())
    # else:
    #     return HttpResponseRedirect("/user/login")
    return render_to_response("index.html", locals())

# #cookie验证登录
# def index(request):
#     user = request.COOKIES.get("user","None")
#     if request.session.get("userdata",""):
#         return render_to_response("index.html",locals())
#     else:
#         return HttpResponseRedirect("/user/login")
##############################################################################################################
#增加机房
@valid_login
def DataroomAdd(request):
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    user = request.session["UserData"]["user"]
    if isPermission(request.session["UserData"]["permission"]):
        if request.method == "POST" and request.POST:
            dr = Dataroom()
            dr.DataroomName = request.POST["name"]
            dr.DataroomDes = request.POST["description"]
            dr.save()
            log = Log()
            log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "["+dr.DataroomName + "]机房资产添加成功，操作员："+user+"</br>"
            log.save()
            return HttpResponseRedirect("/user/DataroomList")
        else:
            return render_to_response("DataroomAdd.html", locals())
    else:
        alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
        return render_to_response("DataroomList.html", locals())
#机房清单
@valid_login
def DataroomList(request):
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    user = request.session["UserData"]["user"]
    dataroomData = Dataroom.objects.all()

    return render_to_response("DataroomList.html", locals())

@valid_login
def DelDataroom(request):
    user = request.session["UserData"]["user"]
    if isPermission(request.session["UserData"]["permission"]):
        if request.method == "POST" and request.POST:
            id = int(request.POST["id"])
            # print(id)
            if not Dataroom.objects.get(basemodel_ptr_id=id).getCabinetcount() == 0:
                return JsonResponse({"statue": "HasCabinet"})
            else:
                dr = Dataroom.objects.get(basemodel_ptr_id = id)
                delname = dr.DataroomName
                dr.delete()
                log = Log()
                log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + delname + "]机房资产删除成功，操作员：" + user + "</br>"
                log.save()
                return JsonResponse({"statue":"success"})

        else:
            return JsonResponse({"statue":"error"})
    else:
        return JsonResponse({"statue": "NoPermission"})
##############################################################################################################
#增加机柜
@valid_login
def CabinetAdd(request):
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    user = request.session["UserData"]["user"]
    obj = ImportForm(request.POST)
    if isPermission(request.session["UserData"]["permission"]):
        if request.method == "POST" and request.POST:
            cb = Cabinet()
            cb.CabinetName = request.POST["name"]
            cb.DataRoomID = request.POST["Dataroom_list"]
            cb.Capacity = request.POST["Capacity"]
            cb.CabinetDes = request.POST["description"]
            if Cabinet.objects.filter(CabinetName=cb.CabinetName):  # select * from Users where username = user;
                return render_to_response("CabinetAdd.html", {'script': "alert", 'wrong': '机柜号已经存在，请重新添加'})
            else:
                cb.save()
                log = Log()
                log.ExcelLog = datetime.datetime.now().strftime( '%Y-%m-%d %H:%M:%S') + "[" + cb.CabinetName + "]机柜资产添加成功，操作员：" + user + "</br>"
                log.save()
                return HttpResponseRedirect("/user/CabinetList")
        else:
            return render_to_response("CabinetAdd.html", locals())
    else:
        alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
        return render_to_response("CabinetList.html", locals())

@valid_login
def CabinetsAdd(request):
    user = request.session["UserData"]["user"]
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    if request.method == "POST" and request.FILES.get("list"):
        excel = request.FILES.get("list")  # 获取前端上传的文件
        print("excel is : ", excel)
        print(type(excel))
        # 前内存的文件存入本地
        path = default_storage.save(settings.MEDIA_ROOT + 'Cabinetlist.xls', ContentFile(excel.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        print(type(tmp_file))
        print(tmp_file)
        # 获得游标对象, 用于逐行遍历数据库数据
        cursor = connection.cursor()
        sql = "INSERT INTO users_cabinet (basemodel_ptr_id,CabinetName,DataRoomID,Capacity,CabinetDes)VALUES (%s, %s, %s, %s, %s)"
        # 用xlrd打开excel
        data = xlrd.open_workbook(tmp_file)
        # 选择要读取的子表
        sheet = data.sheet_by_name("Sheet1")
        # r为行数，逐行读取，遍历0到n行
        for r in range(1, sheet.nrows):

            # basemodel_ptr_id列检测:
            try:
                basemodel_ptr_id = int(sheet.cell(r, 0).value)
            except:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行basemodel_ptr_id 有误，不能为空且要为整数'}
                return render_to_response("CabinetsAdd.html", locals())

            if basemodelValid(basemodel_ptr_id) == 2:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'basemodel_ptr_id:'+str(basemodel_ptr_id)+'为DataRoomID,不可用'}
                return render_to_response("CabinetsAdd.html", locals())
            if basemodelValid(basemodel_ptr_id) == 3:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'basemodel_ptr_id:'+str(basemodel_ptr_id)+'机柜ID已存在,不可用'}
                return render_to_response("CabinetsAdd.html", locals())
            if basemodelValid(basemodel_ptr_id) == 4:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'basemodel_ptr_id:'+str(basemodel_ptr_id)+'为设备ID,不可用'}
                return render_to_response("CabinetsAdd.html", locals())

            # CabinetName列检测:
            CabinetName = sheet.cell(r, 1).value
            if Cabinet.objects.filter(CabinetName=CabinetName).exists():
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'CabinetName已存在，请确认信息'}
                return render_to_response("CabinetsAdd.html", locals())

            # DataRoomID列检测:
            DataRoomID = sheet.cell(r, 2).value
            if Dataroom.objects.filter(basemodel_ptr_id=DataRoomID).exists():
                pass
            elif DataRoomID == "":
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'DataRoomID 为必填项'}
                return render_to_response("CabinetsAdd.html", locals())
            else:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'DataRoomID所标识机房不存在，请确认信息'}
                return render_to_response("CabinetsAdd.html", locals())

            #容量非空检测
            Capacity = int(sheet.cell(r, 3).value)
            if Capacity == "":
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'Capacity 为必填项'}
                return render_to_response("CabinetsAdd.html", locals())
            CabinetDes = sheet.cell(r, 4).value

            # 检测无误确认basemodel_ptr_id外键插入。
            try:
                BaseModel.objects.get(id=basemodel_ptr_id)
            except:
                cursor.execute("INSERT INTO users_basemodel(id,delete_flag) VALUES (%s,%s)",
                               (basemodel_ptr_id, "N"))
            #插入数据库
            values = (basemodel_ptr_id, CabinetName, DataRoomID, Capacity, CabinetDes)
            cursor.execute(sql, values)
            log = Log()
            log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ":导入第" + str(r + 1) + "行成功。</br>"
            log.save()
            # except:
            #     alert = {'script': "alert", 'wrong': '数据库存操作失败'}
            #     return render_to_response("CabinetsAdd.html", locals())
        #关闭游标
        cursor.close()
        connection.commit()
        return HttpResponseRedirect("/user/CabinetList")
    else:
        return render_to_response("CabinetsAdd.html", locals())

#机柜清单
@valid_login
def CabinetList(request):
    dataroom = ImportForm(request.POST)
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    user = request.session["UserData"]["user"]
    # sql = "select users_cabinet.basemodel_ptr_id,CabinetName,DataroomName,Capacity from users_cabinet,users_dataroom where users_dataroom.basemodel_ptr_id = users_cabinet.DataRoomID"
    # CabinetData = Cabinet.objects.raw(sql)
    # print(type(CabinetData))
    # for i in CabinetData:
        # print(type(i))
    CabinetData = Cabinet.objects.all()
    page_num = 1
    paginator = Paginator(CabinetData, 10)
    page_list = paginator.page_range
    # 确定页码
    # page_list = range(1, page_total + 1)
    if request.method == "GET" and request.GET.get("page"):
        #自带分页方法
        page_num = int(request.GET.get("page"))
        page_numnext = page_num + 1
        page_numlast = page_num - 1
    try:
        CabinetData = paginator.page(page_num)  # 获取某页对应的记录
    except PageNotAnInteger:  # 如果页码不是个整数
        CabinetData = paginator.page(1)  # 取第一页的记录
    except EmptyPage:  # 如果页码太大，没有相应的记录
        CabinetData = paginator.page(paginator.num_pages)  # 取最后一页的记录
        # 全部删除功能
    if request.method == "POST":
        if isPermission(request.session["UserData"]["permission"]):
            #获取勾选机柜的ID的列表
            check_box_list = request.POST.getlist('check_box_list')
            #判断列表存在
            if check_box_list:
                #遍历列表机柜确认机柜上都没有设备，否则直接返回告警
                for check in check_box_list:
                    if not Cabinet.objects.get(basemodel_ptr_id=check).getdevicescout() == 0:
                        alert = {'script': "alert", 'wrong': '所选机柜中有机柜上有设备，无法执行所此操作，请确认信息。'}
                        return render_to_response("CabinetList.html", locals())

                for i in check_box_list:
                    Cabinetsel = Cabinet.objects.get(basemodel_ptr_id=i)
                    delname = Cabinetsel.CabinetName
                    log = Log()
                    log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + delname + "]机柜资产删除成功，操作员：" + user + "</br>"
                    log.save()
                    Cabinetsel.delete()

                return HttpResponseRedirect("/user/CabinetList")
            else:
                return render(request, "CabinetList.html", locals())
        else:
            alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
            return render_to_response("CabinetList.html", locals())

    return render(request,"CabinetList.html", locals())

@valid_login
def CabinetAll(request):
    dataroom = ImportForm(request.POST)
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    user = request.session["UserData"]["user"]

    CabinetData = Cabinet.objects.all()

    if request.method == "POST":
        if isPermission(request.session["UserData"]["permission"]):
            check_box_list = request.POST.getlist('check_box_list')
            if check_box_list:
                for i in check_box_list:
                    Cabinetsel = Cabinet.objects.get(basemodel_ptr_id=i)
                    delname = Cabinetsel.CabinetName
                    Cabinetsel.delete()
                    log = Log()
                    log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + delname + "]机柜资产删除成功，操作员：" + user + "</br>"
                    log.save()
                return HttpResponseRedirect("/user/CabinetList")
            else:
                return render(request, "CabinetList.html", locals())
        else:
            alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
            return render_to_response("CabinetList.html", locals())

    return render(request,"CabinetList.html", locals())

@valid_login
def DelCabinet(request):
    user = request.session["UserData"]["user"]
    if isPermission(request.session["UserData"]["permission"]):

        if request.method == "POST" and request.POST:
            id = int(request.POST["id"])
            if not Cabinet.objects.get(basemodel_ptr_id=id).getdevicescout() == 0:
                return JsonResponse({"statue": "HasDevices"})
            else :
                cabinet = Cabinet.objects.get(basemodel_ptr_id = id)
                delname = cabinet.CabinetName
                cabinet.delete()
                log = Log()
                log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + delname + "]机柜资产删除成功，操作员：" + user + "</br>"
                log.save()
                return JsonResponse({"statue":"success"})
        else:
            return JsonResponse({"statue":"error"})
    else:
        return JsonResponse({"statue": "NoPermission"})

##############################################################################################################
#增加设备
@valid_login
def DeviceAdd(request):
    obj = ImportForm(request.POST)
    cabinetselect = CabinetSelect(request.POST)
    user = request.session["UserData"]["user"]
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    #判断权限
    if isPermission(request.session["UserData"]["permission"]):

        if Dataroom.objects.all() and Cabinet.objects.all():
            if request.method == "POST" and request.POST:
                s = Devices()
                s.sn = request.POST["sn"]
                s.Psn = request.POST["Psn"]
                s.DataRoomID = request.POST["Dataroom_list"]
                s.DataRoom = Dataroom.objects.get(basemodel_ptr_id=s.DataRoomID).DataroomName
                s.CabinetID = request.POST["Cabinet_list"]
                s.Cabinetname = Cabinet.objects.get(basemodel_ptr_id=s.CabinetID).CabinetName
                s.deviceMap = request.POST["deviceMap"]
                s.deviceSize = request.POST["deviceSize"]
                s.deviceType = request.POST["device_type"]
                s.company = request.POST["company"]
                s.model = request.POST["model"]
                s.adminIP = request.POST["adminIP"]
                s.produceIP = request.POST["produceIP"]
                # s.system = request.POST["system"]
                s.uplinkdev = request.POST["uplinkdev"]
                s.downlinkdev = request.POST["downlinkdev"]
                s.deviceUser = request.POST["deviceUser"]
                s.updatetime = request.POST["updatetime"]
                s.updateUserID = User.objects.get(username=user).id
                s.deviceDes = request.POST["descripotion"]
                s.OutMaintain = request.POST["OutMaintain"]
                try:
                    Devices.objects.get(sn=s.sn)
                    alert = {'script': "alert", 'wrong': '设备SN已存在，请重新确认SN。'}
                    return render_to_response("DeviceAdd.html", locals())
                except:
                    if not Cabinet.objects.get(basemodel_ptr_id=s.CabinetID).DataRoomID == int(s.DataRoomID):
                        alert = {'script': "alert", 'wrong': '所选机房没有该机柜'}
                        return render_to_response("DeviceAdd.html",locals())
                    elif Cabinet.objects.get(basemodel_ptr_id=s.CabinetID).AbleCapcity() < int(s.deviceSize):
                        alert = {'script': "alert", 'wrong': '所选机柜已经没有可用空间'}
                        return render_to_response("DeviceAdd.html", locals())
                    else:
                        s.save()
                        log = Log()
                        log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + s.sn + "]设备资产添加成功，操作员：" + user + "</br>"
                        log.save()
                        return HttpResponseRedirect("/user/DeviceList")
            else:
                return render_to_response("DeviceAdd.html",locals())
        else:
            alert = {'script': "alert", 'wrong': '您的机房或机柜为空，请先添加机房或机柜资源'}
            return render_to_response("DeviceAdd.html",locals())
    else:
        alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
        return render_to_response("DevicesList.html", locals())

#excel表添加设备
@valid_login
def DevicesAdd(request):
    user = request.session["UserData"]["user"]
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())

    if request.method == "POST":
        excel = request.FILES.get("list")  # 获取前端上传的文件
        print("excel is : ", excel)
        print(type(excel))
        # 将内存的文件存入本地
        path = default_storage.save(settings.MEDIA_ROOT + 'excel.xls', ContentFile(excel.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        # print(type(tmp_file))
        # print(tmp_file)
        # 获得游标对象, 用于逐行遍历数据库数据
        cursor = connection.cursor()
        sql = "INSERT INTO users_devices (basemodel_ptr_id,sn, Psn, DataRoomID, CabinetID, deviceType, deviceMap,company, model, deviceSize, adminIP, produceIP, system, uplinkdev,downlinkdev,updatetime,deviceUser,updateUserID,deviceDes,DataRoom,Cabinetname,OutMaintain,isVirtual,isActive,Status,isMaintain)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # 用xlrd打开excel
        data = xlrd.open_workbook(tmp_file)
        # 选择要读取的子表
        sheet = data.sheet_by_name("Sheet1")
        # r为行数，逐行读取，遍历0到n行
        for r in range(1, sheet.nrows):
            # basemodel_ptr_id列检测:
            # try:
            #     basemodel_ptr_id = int(sheet.cell(r, 0).value)
            # except:
            #     alert = {'script': "alert", 'wrong': 'basemodel_ptr_id 为必填项'}
            #     return render_to_response("DeviceAdd.html", locals())
            # ############################
            try:
                basemodel_ptr_id = int(sheet.cell(r, 0).value)
            except:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行basemodel_ptr_id 有误，不能为空且要为整数'}
                return render_to_response("DeviceAdd.html", locals())

            if basemodelValid(basemodel_ptr_id) == 2:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行basemodel_ptr_id:'+str(basemodel_ptr_id)+'为DataRoomID,不可用'}
                return render_to_response("DeviceAdd.html", locals())
            if basemodelValid(basemodel_ptr_id) == 3:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行basemodel_ptr_id:'+str(basemodel_ptr_id)+'机柜ID已存在,不可用'}
                return render_to_response("DeviceAdd.html", locals())
            if basemodelValid(basemodel_ptr_id) == 4:
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行basemodel_ptr_id:'+str(basemodel_ptr_id)+'为设备ID,不可用'}
                return render_to_response("DeviceAdd.html", locals())
            ###########################
            # 读取sn列并检测sn
            sn = sheet.cell(r, 1).value
            if Devices.objects.filter(sn=sn).exists():
                log = "导入第" + str(r) + "行成功。\n"
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行sn已存在，请确认信息'}
                return render_to_response("DeviceAdd.html", locals())
            # 读取Psn列
            Psn = sheet.cell(r, 2).value
            #DataRoomID列检测
            try:
                DataRoomID = int(sheet.cell(r, 3).value)
            except:
                try:
                    DataRoom = sheet.cell(r, 19).value
                    DataRoomID = Dataroom.objects.get(DataroomName=DataRoom).basemodel_ptr_id
                except:
                    log = "导入第" + str(r) + "行成功。\n"
                    alert = {'script': "alert", 'wrong': '第' + str(r + 1) + 'DataRoomID 取值失败，通过机房名称取值出错，请确认信息。'}
                    return render_to_response("DeviceAdd.html", locals())
            #CabinetID列检测
            try:
                CabinetID = int(sheet.cell(r, 4).value)
            except:
                try:
                    Cabinetname = sheet.cell(r, 20).value
                    CabinetID = Cabinet.objects.get(CabinetName=Cabinetname).basemodel_ptr_id
                except:
                    log = "导入第" + str(r) + "行成功。\n"
                    alert = {'script': "alert", 'wrong': '第' + str(r + 1) + 'CabinetID 取值失败，通过机柜名称取值出错，请确认信息。'}
                    return render_to_response("DeviceAdd.html", locals())
            # deviceType列检测
            try:
                deviceType = int(sheet.cell(r, 5).value)
            except:
                log = "导入第" + str(r) + "行成功。\n"
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行deviceType 为必填项(1.服务器，2.网络设备，3.安全设备，4.存储设备)'}
                return render_to_response("DeviceAdd.html", locals())

            deviceMap = sheet.cell(r, 6).value
            company = sheet.cell(r, 7).value
            model = sheet.cell(r, 8).value
            deviceSize = sheet.cell(r, 9).value
            adminIP = sheet.cell(r, 10).value
            produceIP = sheet.cell(r, 11).value
            system = sheet.cell(r, 12).value
            uplinkdev = sheet.cell(r, 13).value
            downlinkdev = sheet.cell(r, 14).value
            #更新日期列检测
            try:
                updatetime = xldate_as_datetime(sheet.cell(r, 15).value,0)
            except:
                log = "导入第" + str(r) + "行成功。\n"
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行updatetime 为必填项可用excel常用日期格式'}
                return render_to_response("DeviceAdd.html", locals())

            deviceUser = sheet.cell(r, 16).value
            updateUserID = User.objects.get(username=user).id
            deviceDes = sheet.cell(r, 18).value
            DataRoom = sheet.cell(r, 19).value
            Cabinetname = sheet.cell(r, 20).value
            # 更新日期列检测
            try:
                OutMaintain = xldate_as_datetime(sheet.cell(r, 21).value, 0)
            except:
                log = "导入第" + str(r) + "行成功。\n"
                alert = {'script': "alert", 'wrong': '第'+str(r+1)+'行OutMaintain 为必填项可用excel常用日期格式'}
                return render_to_response("DeviceAdd.html", locals())

            isVirtual = sheet.cell(r, 22).value
            isActive = sheet.cell(r, 23).value
            Status = sheet.cell(r, 24).value
            isMaintain = sheet.cell(r, 25).value

            values = (basemodel_ptr_id, sn, Psn, DataRoomID, CabinetID, deviceType, deviceMap, company, model,deviceSize,adminIP,
            produceIP, system, uplinkdev, downlinkdev, updatetime, deviceUser, updateUserID, deviceDes, DataRoom,
            Cabinetname, OutMaintain, isVirtual, isActive, Status, isMaintain)

            #插入外键
            try:
                BaseModel.objects.get(id=basemodel_ptr_id)
            except:
                cursor.execute("INSERT INTO users_basemodel(id,delete_flag) VALUES (%s,%s)",
                               (basemodel_ptr_id, "N"))

            # #如果没有机房ID不存在，插入机房名称和机房ID
            # try:
            #     BaseModel.objects.get(id=DataRoomID)
            # except:
            #     cursor.execute("INSERT INTO users_basemodel(id,delete_flag) VALUES (%s,%s)", (DataRoomID, "N"))
            #     cursor.execute("INSERT INTO users_dataroom(basemodel_ptr_id,DataroomName,description) VALUES (%s,%s,%s)",
            #                    (DataRoomID, DataRoom, ""))

            cursor.execute(sql, values)
            log = Log()
            log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+":导入第"+str(r+1)+"行成功。</br>"
            print(log.ExcelLog)
            log.save()

        cursor.close()
        connection.commit()
        return render_to_response("DevicesAdd.html", locals())
    else:
        return render_to_response("DevicesAdd.html", locals())

#设备清单
@valid_login
def DeviceList(request):
    user = request.session["UserData"]["user"]
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    page_num = 1 #给页码一个初始赋值没有get到页码默认第一页
    #如果get到页码
    if request.method == "GET" and request.GET.get("page"):
        page_num = request.GET.get("page")
        page_num = int(page_num)
        page_numnext = page_num+1
        page_numlast = page_num-1

    dataroom = ImportForm(request.POST)
    # sql = "select users_devices.basemodel_ptr_id,users_devices.sn,users_devices.CabinetID,users_devices.deviceMap,users_devices.company,users_devices.model,users_devices.produceIP,users_devices.updatetime,users_dataroom.DataroomName from users_dataroom,users_devices where users_dataroom.basemodel_ptr_id = users_devices.DataRoomID"
    deviceData = Devices.objects.all()
    # setattr(type(deviceData), '__len__', get_len(deviceData))
    page_total = len(deviceData)/10
    #页码向上取整
    if page_total != int(page_total):
        page_total += 1
    page_total = int(page_total)
    # 确定页码
    page_list = range(1,page_total+1)
    #页码内容
    page_device = deviceData[(int(page_num)-1)*10:int(page_num)*10]
    #全部删除功能
    if request.method == "POST":
        # 判断权限
        if isPermission(request.session["UserData"]["permission"]):
            check_box_list = request.POST.getlist('check_box_list')
            if check_box_list:
                for i in check_box_list:
                    device = Devices.objects.get(basemodel_ptr_id=i)
                    delname = device.sn
                    device.delete()
                    log = Log()
                    log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + delname + "]设备资产删除成功，操作员：" + user + "</br>"
                    log.save()
                return HttpResponseRedirect("/user/DeviceList")
            else:
                return render(request, "DevicesList.html", locals())
        else:
            alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
            return render_to_response("DevicesList.html", locals())

    return render(request, "DevicesList.html", locals())


@valid_login
def DeviceAll(request):
    user = request.session["UserData"]["user"]
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())

    dataroom = ImportForm(request.POST)
    page_device = Devices.objects.all()
    # 全部删除功能
    #权限
    if isPermission(request.session["UserData"]["permission"]):
        if request.method == "POST":
            check_box_list = request.POST.getlist('check_box_list')
            print(check_box_list)
            if check_box_list:
                for i in check_box_list:
                    device = Devices.objects.get(basemodel_ptr_id=i)
                    print(device.sn)
                    delname = device.sn
                    device.delete()
                    log = Log()
                    log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + delname + "]设备资产删除成功，操作员：" + user + "</br>"
                    log.save()
                return HttpResponseRedirect("/user/DeviceList")
            else:
                return render(request, "DevicesList.html", locals())

        return render(request, "DevicesList.html", locals())
    else:
        alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
        return render_to_response("DevicesList.html", locals())

@valid_login
def DeviceSearch(request):
    user = request.session["UserData"]["user"]
    page_num = 1
    # 设备统计
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())

    if request.method == "GET" and request.GET.get("page"):
        page_num = request.GET.get("page")
        page_num = int(page_num)
        page_numnext = page_num + 1
        page_numlast = page_num - 1

    #下拉框
    dataroom = ImportForm(request.POST)
    #获取关键字
    if request.method == "GET" and request.GET.get("searchkey"):
        key = request.GET.get("searchkey")
        print(key)

    else:
        key = ""
    if request.method == "GET" and request.GET.get("Dataroom_list"):
        Dataroom_list = request.GET.get("Dataroom_list")
        print(Dataroom_list)
    else:
        Dataroom_list = ""

    if Devices.objects.filter(produceIP=key):
        deviceData = Devices.objects.filter(produceIP=key)
    elif Devices.objects.filter(sn=key):
        deviceData = Devices.objects.filter(sn=key)
    elif Devices.objects.filter(Psn=key):
        deviceData = Devices.objects.filter(Psn=key)
    elif Devices.objects.filter(company=key):
        deviceData = Devices.objects.filter(company=key)
    elif Devices.objects.filter(Cabinetname=key).exists():
        deviceData = Devices.objects.filter(Cabinetname=key)
    # page_total = len(deviceData)
    # if page_total != int(page_total):
    #     page_total += 1
    # page_total = int(page_total)
    # page_list = range(1, page_total + 1)  # 确定页码
    page_device = deviceData
    # [(int(page_num) - 1) * 10:int(page_num) * 10]
    return render_to_response("DevicesList.html", locals())

@valid_login
def DeviceEdit(request):
    obj = ImportForm(request.POST)
    cabinetselect = CabinetSelect(request.POST)
    user = request.session["UserData"]["user"]
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    #权限判定
    if isPermission(request.session["UserData"]["permission"]):
        if request.method == "GET" :
            deviceEditID = request.GET.get("editkey")
            devicedata = Devices.objects.get(sn=deviceEditID)

        if request.method == "POST" and request.POST:
            editsn = request.POST["sn"]
            Devices.objects.filter(sn=editsn).update(Psn=request.POST["Psn"])
            Devices.objects.filter(sn=editsn).update(DataRoomID=request.POST["Dataroom_list"])
            Devices.objects.filter(sn=editsn).update(DataRoom=Dataroom.objects.get(basemodel_ptr_id=Devices.objects.get(sn=editsn).DataRoomID).DataroomName)
            Devices.objects.filter(sn=editsn).update(CabinetID=request.POST["Cabinet_list"])
            Devices.objects.filter(sn=editsn).update(Cabinetname=Cabinet.objects.get(basemodel_ptr_id=Devices.objects.get(sn=editsn).CabinetID).CabinetName)
            Devices.objects.filter(sn=editsn).update(deviceMap=request.POST["deviceMap"])
            Devices.objects.filter(sn=editsn).update(deviceSize=request.POST["deviceSize"])
            Devices.objects.filter(sn=editsn).update(deviceType=request.POST["device_type"])
            Devices.objects.filter(sn=editsn).update(company=request.POST["company"])
            Devices.objects.filter(sn=editsn).update(model=request.POST["model"])
            Devices.objects.filter(sn=editsn).update(adminIP=request.POST["adminIP"])
            Devices.objects.filter(sn=editsn).update(produceIP=request.POST["produceIP"])
            Devices.objects.filter(sn=editsn).update(uplinkdev=request.POST["uplinkdev"])
            Devices.objects.filter(sn=editsn).update(deviceUser=request.POST["deviceUser"])
            Devices.objects.filter(sn=editsn).update(updatetime=request.POST["updatetime"])
            Devices.objects.filter(sn=editsn).update(OutMaintain=request.POST["OutMaintain"])
            Devices.objects.filter(sn=editsn).update(deviceDes=request.POST["descripotion"])
            Devices.objects.filter(sn=editsn).update(updateUserID=User.objects.get(username=user).id)
            log = Log()
            log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + editsn + "]设备资产信息更新成功，操作员：" + user + "</br>"
            log.save()
            return HttpResponseRedirect("/user/DeviceList")
        else:
            return render_to_response("DeviceEdit.html",locals())
    else:
        alert = {'script': "alert", 'wrong': '权限不足,请联系管理员提升您的权限'}
        return render_to_response("DevicesList.html", locals())

#设备详细信息
@valid_login
def GetDevice(request):
    user = request.session["UserData"]["user"]
    totalsec = len(Devices.objects.filter(deviceType=3))
    totalnet = len(Devices.objects.filter(deviceType=2))
    totalserver = len(Devices.objects.filter(deviceType=1))
    totaldevices = len(Devices.objects.all())
    if request.method == "GET" and request.GET.get("devicesn"):
        key = request.GET.get("devicesn")
        # print(key)
        device = Devices.objects.get(sn=key)
    return render_to_response("GetDevice.html", locals())

#设备删除
@valid_login
def DelDevice(request):
    user = request.session["UserData"]["user"]
    if isPermission(request.session["UserData"]["permission"]):
        if request.method == "POST" and request.POST:
            id = str(request.POST["id"])
            # print(id)
            device = Devices.objects.get(sn = id)
            # print(type(device.sn))
            delname = device.sn
            # print(delname)
            device.delete()
            log = Log()
            log.ExcelLog = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "[" + delname + "]设备资产删除成功，操作员：" + user + "</br>"
            log.save()
            return JsonResponse({"statue":"success"})
        else:
            return JsonResponse({"statue":"error"})
    else:
        return JsonResponse({"statue": "NoPermission"})

##############################################################################################################

def OperLog(request):
    return render_to_response("log.html",locals())


