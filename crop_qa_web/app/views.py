import re
import json
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse
from pure_pagination import Paginator

from app.sent2vec.utils import search
from .models import Farming


def farm_index(request):
    farms = Farming.objects.filter(crop="水稻").order_by("-pub_time")

    try:
        page = int(request.GET.get('page', 1))  # 页码
        paginator = Paginator(farms, 20, request=request)  # 获取有多少页
        farms = paginator.page(page)  # 获取指定页的数据
    except Exception as e:
        return HttpResponseRedirect('/')

    return render(request, 'app/index.html', {
        'farms': farms
    })


def farm_search(request):
    # search_for = request.GET['search_for']
    search_for = request.POST.get('search_for', None)
    if search_for:
        result = search(search_for)
        qs_id = result[1]
        farms = [Farming.objects.filter(id=qid).first() for qid in qs_id]
        print(farms[0]['title'])
        print(farms[0]['content'])
        return render(request, 'app/index.html', {
            'result': farms[0],
            'farms': farms[1:]
        })
    else:
        return redirect(farm_index)


def farm_search_api(request):
    search_for = request.POST.get('search_for', None)
    print(search_for)
    if search_for:
        result = search(search_for)
        qs_id = result[1]
        farms = [Farming.objects.filter(id=qid).first() for qid in qs_id]
        print(farms[0]['title'])
        print(farms[0]['content'])

        sim_q = farms[0]['title']
        ans = ''.join(farms[0]['content'])
        ans = re.sub('<.*?>', '', ans)
        source_url = farms[0]['url']
        # ans = re.sub('\W+', '', ans)
        print(sim_q)
        print(ans)
        res = {'sim_q': sim_q, 'ans': ans, 'source_url': source_url}
        print(res)
        response = '找到最相似的问题：\n' + sim_q + '\n\n' + '答案：\n' + ans + '\n\n' + '来源地址：\n' + source_url
        return HttpResponse(json.dumps(response, ensure_ascii=False), content_type="application/json")

        # return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="application/json")
        # return render(request, 'app/index.html', {
        #     'result': farms[0],
        #     'farms': farms[1:]
        # })
    else:
        return redirect(farm_index)


def farm_detail(request, farm_id):
    farm = Farming.objects.filter(position_id=farm_id).first()
    return render(request, 'app/detail.html', {'farm': farm, 'farm_detail': ''.join(farm.farm_detail)})


def not_found(request, error):
    return render(request, 'app/404.html')