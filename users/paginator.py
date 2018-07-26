from django.core.paginator import Paginator

def paginator(data_list, per_page, page_no):
  """封装Django分页"""
  pages = Paginator(data_list, per_page)

  # 防止超出页数
  if not page_no > 0:
    page_no = 1
  if page_no > pages.num_pages:
    page_no = pages.num_pages

  p = pages.page(page_no) # 获取本页数据

  data = dict() # 获取分页信息
  data['count'] = pages.count
  data['page_num'] = pages.num_pages
  data['per_page'] = per_page
  data['current'] = page_no
  data['start_index'] = p.start_index() - 1

  return p.object_list, page_no, data


class QueryWrapper(object):
  """查询集包装器。实现django Paginator需要的必要方法，实现和query一样使用Paginator分页"""

  def __init__(self, sql, params=None, db="default"):
    """
    :param sql: sql语句
    :param params: sql语句的params参数
    :param db: 数据库名称（Django配置）
    """
    self.db = db
    self.sql = sql
    self.params = params

  def count(self):
    """计算总页数"""
    sql = """select count(*) from (%s) _count""" % self.sql
    # sql封装方法请参考https://my.oschina.net/watcher/blog/1573503
    return fetchone_sql((sql, self.params), db=self.db, flat=True) # 返回总页数

  def __getslice__(self, x, y):
    """ self.__getslice(x, y) = self[x:y]"""
    sql = self.sql + ' LIMIT {start}, {num}'.format(start=x, num=y - x)
    # sql封装方法请参考https://my.oschina.net/watcher/blog/1573503
    return fetchall_to_dict((sql, self.params), db=self.db) # 字典列表形式返回


def demo_orm():
  """使用Django的ORM分页"""
  # 示例：查询status=1的用户分页，每页10条，取第2页数据（假设数据量足够）
  status = 1
  per_page = 10
  page_no = 2

  # 使用Django的ORM
  from django.contrib.auth.models import User

  query = User.objects.filter(status=status).values("id", "username", "first_name")
  one_page_data_list, page_no, page_data = paginator(query, per_page, page_no)
  # one_page_data_list 即为第二页数据，例如：[{"id": 1, "username": "111", "first_name": "aaa"}]
  print(one_page_data_list)


def demo_raw():
  """使用原生sql实现相同分页"""
  # 示例：查询status=1的用户分页，每页10条，取第2页数据（假设数据量足够）
  status = 1
  per_page = 10
  page_no = 2

  sql = "select id, username, first_name from auth_user where status=%(status)s"
  params = {"status": status} # 使用params防止sql注入
  query = QueryWrapper(sql, params, "default")
  one_page_data_list, page_no, page_data = paginator(query, per_page, page_no)
  # one_page_data_list 同ORM获取数据一样
  print(one_page_data_list)


if __name__ == "__main__":
  demo_orm()
  demo_raw()