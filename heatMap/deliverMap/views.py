from django.shortcuts import render,HttpResponse
from django.conf import settings
import pymysql,json
# Create your views here.

def index(request):

    return  render(request,'eCharts/heatmap-bmap.html')

def getData(request):

    def mysql_conn():
        connection = pymysql.connect(host='10.0.2.55',
                                     port=3300,
                                     user='mysql',
                                     password='mysql123',
                                     db='crefx',
                                     charset='utf8',
                                     # cursorclass=pymysql.cursors.DictCursor
                                     )
        return connection
    cur = mysql_conn().cursor()
    sql = '''select r_address_location
                    from gt_timelimit t
                    where t.r_org_name = '北京分公司'
                    and t.to_city = '北京市'
                    and t.shipping_date between '20180215' and '20180317'
                    and t.r_address like '北京北京市海淀区%' '''
    cur.execute(sql)
    data = cur.fetchall()

    data_list = []
    for item in data:
        if not item:continue
        if not item[0]:continue
        temp = []
        item = json.loads(item[0])
        temp.append(item.get('lng'))
        temp.append(item.get('lat'))
        temp.append(int(item.get('count'))-50)
        data_list.append(temp)

    data_list = json.dumps(data_list)
    return HttpResponse(data_list)