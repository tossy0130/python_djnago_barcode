from django.shortcuts import render , get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import redirect

from django.contrib import messages

# TemplateView 用
from django.views import generic
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.edit import UpdateView

# UpdateView 用
from django.urls import reverse_lazy

# model
from .models import *
from django.db.models import Q

### kanai_app model 読み込み
# from .models import (Product,Test_shouhin_01,User,Test_shouhin_010,Post)
from .models import (Product,Test_shouhin_01,Test_shouhin_010,Post)

################################ ログイン用
from django.contrib.auth.views import LoginView
from .forms import *

################################ アカウント登録用
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.signing import BadSignature, SignatureExpired, dumps, loads
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import get_template
from django.contrib import messages

################################ メール送信後　URL 認証用
from django.conf import settings

################################ CSV エクスポート用
from io import TextIOWrapper, StringIO
import csv

import urllib

### ログイン制御　排他処理
from django.contrib.auth.mixins import LoginRequiredMixin # クラス用
from django.contrib.auth.decorators import login_required # 関数用

### バーコード　&  QR コード　作成用
from PIL import Image
import qrcode
from io import BytesIO
import barcode
from barcode.writer import ImageWriter


############################# 表示画面トップ #############################
class Lp(generic.TemplateView):

    template_name = 'kanai_app/lp.html'

    def get_context_data(self, **kwargs):
    
        context = super(Lp, self).get_context_data(**kwargs)
        ### Receipe テーブルの値を格納 => template　ビューで使える用にする
        all_item = Product.objects.all()

        ### 新着情報　を　渡す
        news_item = Post.objects.order_by('pk').last()

        context['items'] = all_item

        context['news'] = news_item

        return context

    

################ 表示画面用　検索
class LpList(generic.ListView):

    ### Test_shouhin_010 テーブル のデータを代入
    model = Test_shouhin_010
    template_name = 'kanai_app/test_item_list.html'

    def get_queryset(self):

        ### Test_shouhin_010 テーブル
        get_item = Test_shouhin_010.objects.all()

        ### Toriatukai_Cate テーブル
        target_02 = Toriatukai_Cate.objects.all()

        if 'q' in self.request.GET and self.request.GET['q'] != None:
            q = self.request.GET['q']

            ### Test_shouhin_010_code を　検索対象にする
            get_item = Test_shouhin_010.objects.filter(
                         Q(Test_shouhin_010_code__icontains = q) |  ### コード
                         Q(T_Medium_code_02__Medium_title__icontains = q) | ### 中カテゴリー
                         Q(Test_shouhin_010_name__icontains = q) |  ### メーカー名
                         Q(Test_shouhin_010_str__icontains = q) |   ### 商品名
                         Q(description_item__icontains = q)
                         )
            
            ### 検索　ワードを　取得
            messages.add_message(self.request, messages.INFO, q)
        
        return get_item

################ 企業情報 ページ ################
class Corporate_info(generic.TemplateView):

    template_name = 'kanai_app/Corporate_info.html'


################ 採用情報 ページ ################
class Employment_info(generic.TemplateView):

    template_name = 'kanai_app/employment_info.html'

################ 問い合わせ ページ ################
class Contact_info(generic.TemplateView):

    template_name = 'kanai_app/contact_info.html'


    
################ 管理画面　トップ ################
@login_required
def kanri_top(request):
    return render(request, 'kanai_app/kanri-top.html')



########################### CSV import 01
@login_required
def upload(request):
    
    ### フォームからアップロードされたファイルが　csvファイルか そうじゃないかで　分岐
    #  <input type="file" class="dropify" data-default-file="ファイルを選択してください" name="csv">
    # name='csv' の値を if 'csv' in equest.FILES で判定
    if 'csv' in request.FILES :

        ############# csv アップロード時の処理
        ### TextIOWrapper => ファイル書き込み
        form_data = TextIOWrapper(request.FILES['csv'].file, encoding='UTF-8')

        ### リスト形式で　CSVファイルの読み込み
        csv_file = csv.reader(form_data)

        ### プレビュー用　リスト
        temp_list = []
        view_list = []

        for line in csv_file:
            
            # get_or_create => 値の重複をさける, 同じものがあれば登録できない
            test_shouhin_01, created = Test_shouhin_01.objects.get_or_create(pk=line[0])

            ### 表示用
            view_list.append(line[0])

            # テスト 商品コード
            test_shouhin_01.Test_shouhin_01_code = line[1]
            ### 表示用
            view_list.append(line[1])

            # テスト メーカー名
            test_shouhin_01.Test_shouhin_01_name = line[2]
            ### 表示用
            view_list.append(line[2])

            # テスト 商品名
            test_shouhin_01.Test_shouhin_01_str = line[3]
            ### 表示用
            view_list.append(line[3])

            # テスト　画像パス
            test_shouhin_01.Test_shouhin_01_image = line[4]
            ### 表示用
            view_list.append(line[4])

            test_shouhin_01.save() # 保存

            ########### Table Receipe のデータを　インポート
         
         #   receipe, created = Receipe.objects.get_or_create(pk=line[6])

         #  receipe.title = line[7]

         #   receipe.content = line[8]

         #  receipe.image = line[9]

         #   receipe.save()

       # temp_list.append(view_list)

        context = {
            'view_list':view_list
        }
       ########################### OK メッセージ
       # return render(request, 'kanai_app/csv_import.html')
        return render(request, 'kanai_app/success/su_01.html', context)
    else:
        return render(request, 'kanai_app/csv_import.html')

########################### CSV ダウンロード
def csv_download(request):

    # レスポンスの設定
    response = HttpResponse(content_type='text/csv, charset=Shift-JIS')

    filename = urllib.parse.quote((u'CSV_test.csv').encode("utf8")) # ダウンロードするファイル名
    response['Content-Disposition'] = 'attachment; filename*=UTF-8\'\'{}'.format(filename)

    writer = csv.writer(response)

    ### ヘッダー出力 2021-05-28 テストなのでヘッダーはまだ　ださない
#    header = [] db カラムを入れる

    ### データ出力

    for item in  Test_shouhin_01.objects.all() :
        writer.writerow([item.pk, item.Test_shouhin_01_code, item.Test_shouhin_01_name,
        item.Test_shouhin_01_str, item.Test_shouhin_01_image])

    return response

########################### CSV ダウンロード END



################# 取扱商品カテゴリー　一覧
@login_required
def category_all(request):

        ### 取扱商品テーブル　一覧取得   -Toriatukai_code => 降順　Toriatukai_code => 昇順
        cate_list_01 = Toriatukai_Cate.objects.all().order_by('Toriatukai_code')
        cate_list_val = Toriatukai_Cate.objects.values()

        ### 中カテゴリーテーブル　一覧取得
        m_cate_list = Medium_category.objects.all().order_by('Medium_code')
        m_cate_val = Medium_category.objects.values()

        ca_list = {
            'cate_list_01':cate_list_01,
            'cate_list_val':cate_list_val,
            'm_cate_list': m_cate_list,
            'm_cate_val':m_cate_val,
        }

        return render(request, 'kanai_app/toriatukai/t-index.html', ca_list)


################# 取扱商品　大カテゴリー登録用
@login_required
def Toriatukai_Cate_new(request):
    
    params = {'message': '', 'form': None}

    if request.method == 'POST':
        form = Toriatukai_CateForm(request.POST)

        if form.is_valid():
            form.save()

            
            return redirect('kanai_app:kanri_top')

        ### エラーだった場合
        else:
            params['message'] = '入力エラー。再入力してください。'
            params['form'] = form

    else:
        params['form'] = Toriatukai_CateForm()
    
    return render(request, 'kanai_app/web_kanri/cate_new.html',params)

################# 中カテゴリー　追加
@login_required
def Medium_categoryForm_new(request):

    params = {'message': '', 'form': None}

    if request.method == 'POST':
        form = Medium_categoryForm(request.POST, request.FILES)

        if form.is_valid():
            
            form.save()
            return redirect('kanai_app:kanri_top')

        ### エラーだった場合
        else:
            params['message'] = '入力エラーです。再度入力してください。'
            params['form'] = form


    else:
        params['form'] = Medium_categoryForm()

    return render(request, 'kanai_app/web_kanri/h_cate_new.html', params)

################# 中カテゴリー　登録済みリスト　一覧表示
class Medium_categoryListView(generic.ListView, LoginRequiredMixin):

     model = Medium_category

     queryset = Medium_category.objects.order_by('Medium_code')

     template_name = 'kanai_app/web_kanri/h_cate_list.html'
    
     paginate_by = 15
     ###### 削除処理 ######
     def post(self, request):
         post_pks = request.POST.getlist('delete')  # <input type="checkbox" name="delete"のnameに対応
         Medium_category.objects.filter(pk__in=post_pks).delete()
         return redirect('kanai_app:Medium_categoryListView')

################# 中カテゴリー　登録済みリスト　更新
class Medium_categoryUpdateView(LoginRequiredMixin, UpdateView):

    model = Medium_category

    template_name = 'kanai_app/web_kanri/h_cate_update.html'

    fields = ('Medium_code', 'Medium_title', 'Medium_image', 'M_Toriatukai_code', 'M_code')
    
    ### リダイレクト 
    success_url = reverse_lazy("kanai_app:Medium_categoryListView")

################# 中カテゴリー　削除
class Medium_categoryDeleteView(DeleteView):
     
    model = Medium_category
    template_name = "kanai_app/web_kanri/h_cate_delete.html";
    success_url = reverse_lazy("kanai_app:Medium_categoryListView")
    
 

################# 登録追加用

################# テスト商品 01 Table ユーザー　登録処理
@login_required
def Test_shouhin_010_new(request):

    params = {'message': '', 'form': None}

    if request.method == 'POST':

        form = Test_shouhin_010Form(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('kanai_app:kanri_top')

    else : 
        ### POST されてなかったら Form　を表示させる
        params['form'] = Test_shouhin_010Form()

    return render(request, 'kanai_app/web_kanri/test_shouhin_01.html', params)


################# カテゴリーコードを取得して、a href= で　カテゴリー先へ飛ばす
@login_required
def GET_Medium_code(request, Medium_code):

    Medium_code = Test_shouhin_010.objects.filter(T_Medium_code_02 = Medium_code)
    

    get_list = {
        'Medium_code':Medium_code,
    }

    return render(request, 'kanai_app/toriatukai/t_01.html', get_list)


################## テスト商品ページ　詳細ページ　作成
@login_required
def Medium_Shouhin_detail(request, pk):

    ### プライマリキー　で Test_shouhin_010(Table) から　オブジェクト取得
    get_detail_item = Test_shouhin_010.objects.filter(pk=pk)

    ### get パラメーター取得  m_code
   
    if "m_code" in request.GET:
            get_val = request.GET.get('m_code')
            query_obj = Test_shouhin_010.objects.filter(Test_shouhin_010_code = get_val)
            
            if get_val == "001":
                kanren_val = "002"
                kanren_query = Test_shouhin_010.objects.filter(Test_shouhin_010_code = kanren_val)
            else:
                kanren_val = "001"
                kanren_query = Test_shouhin_010.objects.filter(Test_shouhin_010_code = kanren_val)

    else :
            ### GET の値が　セットされて　いない場合　デフォルトの値をセット
            param_value = request.GET.get(key="m_code", default="hogehoge")
            

    get_detail_list = {
        'get_detail_item':get_detail_item,
        'query_obj' : query_obj,
        'kanren_query' : kanren_query
    }

    return render(request, 'kanai_app/toriatukai/detail/test_detail.html',get_detail_list)



################## オリジナル　カテゴリー　作成
@login_required
def Original_Cate_new(request):

    params = {'message': '', 'form': None}

    if request.method == 'POST':

        form = Original_CateForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            return redirect('kanai_app:kanri_top')
        
        ### エラーだった場合
        else :
            params['form'] = '入力エラーです。再度入力してください。'
            params['form'] = form
    else:
        params['form'] = Original_CateForm()

    return render(request, 'kanai_app/web_kanri/ori-kate_new.html', params)

############### オリジナル　カテゴリー　一覧
class Original_CateListView(generic.ListView, LoginRequiredMixin):

    template_name = 'kanai_app/original/or_shouhin_list.html'

    model = Original_Cate

    context_object_name  = 'or_shouhin_list'

############### 登録商品　一覧
class Test_shouhin_010_Kanri_ListView(generic.ListView, LoginRequiredMixin):

    template_name = 'kanai_app/web_kanri/shouhin_kanri_list.html'

    context_object_name = 'shouhin_list'

    model = Test_shouhin_010

    queryset = Test_shouhin_010.objects.order_by('pk')

############### 登録商品 UpdateView　更新
class Test_shouhin_010_Kanri_UpdateView(generic.UpdateView, LoginRequiredMixin):

    template_name = 'kanai_app/web_kanri/shouhin_kanri_update.html'

    model = Test_shouhin_010

    fields = ('Test_shouhin_010_code','Test_shouhin_010_name','Test_shouhin_010_str',
            'Test_shouhin_010_code_02','Test_shouhin_010_name_02','Test_shouhin_010_image',
            'T_Medium_code_02','jan_code','counter','search_hinmei','description_item','kikaku',
            'siyou_name_01','siyou_content_01','siyou_name_02','siyou_content_02',
            'siyou_name_03','siyou_content_03','siyou_name_04','siyou_content_04',
            'siyou_name_05','siyou_content_05','haiban_flg',
            'sh_thumbnail_02','sh_thumbnail_03',
            'shouhin_flg')

    ### リダイレクト 
    success_url = reverse_lazy("kanai_app:kanri_s")


############### フィールド　名取得  tabsle => Test_shouhin_010
@login_required
def getfnamaes(self, models):

    meta_fields = Test_shouhin_010._meta.get_fields()
    print(meta_fields)

    ret = list()

    for i, meta_fields in enumerate(meta_fields):
        
        if i > 0:
            ret.append(meta_fields.name)
    
    return ret

###############  news 記事エリア　新規作成
@login_required
def Post_new(request):

    params = {'message': '', 'form': None}

    if request.method == 'POST':

        form = Post_newForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('kanai_app:kanri_top')
        
        ### POST が　エラー　だった場合
        else :
            params['message'] = '入力エラーです。再度入力してください。'
            params['form'] = form

    else :
        params['form'] = Post_newForm()

    return render(request, 'kanai_app/news/news_01.html', params)

###################### 検索結果　WEB 表示
def detail(request, pk):

      ### プライマリキー　で Test_shouhin_010(Table) から　オブジェクト取得
    get_detail_item = Test_shouhin_010.objects.filter(pk=pk)

    ### get パラメーター取得  m_code

    get_detail_list = {
        'get_detail_item':get_detail_item
    }

    return render(request, 'kanai_app/detail_item_list.html',get_detail_list)
  

################## メーカー　登録　新規　作成 ################## 
@login_required
def Maker_master_new(request):

    params = {'message': '', 'form': None}

    if request.method == 'POST':

        form = Maker_master_Form(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            return redirect('kanai_app:Maker_master_ListView')
        
        ### エラーだった場合
        else :
            params['form'] = '入力エラーです。再度入力してください。'
            params['form'] = form
    else:

        params['form'] = Maker_master_Form()

    

    return render(request, 'kanai_app/master/maker_master_new.html', params)

################## メーカー 一覧
class Maker_masterListView(generic.ListView, LoginRequiredMixin):

    model = Maker_master
    context_object_name = "maker_list"

    queryset = Maker_master.objects.order_by('maker_code')

    template_name = 'kanai_app/master/maker_master_list.html'

    ### ページネーション　設定
    paginate_by = 20

    ###### 削除処理 ######
    def post(self, request):
         post_pks = request.POST.getlist('delete')  # <input type="checkbox" name="delete"のnameに対応
         Maker_master.objects.filter(pk__in=post_pks).delete()
         return redirect('kanai_app:Maker_master_ListView')


################## ブランド　登録　新規　作成 ################## 
@login_required
def Brand_master_new(request):

    if "m_c" in request.GET:
            get_val = request.GET.get('m_c')

            query_obj = Maker_master.objects.filter(maker_code = get_val)

    params = {'message': '', 'form': None}

    if request.method == 'POST':

        form = Brand_master_Form(request.POST)

        if form.is_valid():

            form.save()

            return redirect('kanai_app:Brand_master_ListView')
        
        ### エラーだった場合
        else :
            params['form'] = '入力エラーです。再度入力してください。'
            params['form'] = form
    else:
        params['form'] = Brand_master_Form()

        params['query_obj'] = query_obj


    return render(request, 'kanai_app/master/brand_master_new.html', params)

################## ブランド 一覧
class Brand_master_ListView(generic.ListView, LoginRequiredMixin):

    model = Brand_master
    context_object_name = "brand_list"

    queryset = Brand_master.objects.order_by('brand_code')

    template_name = 'kanai_app/master/brand_master_list.html'

    ### ページネーション　設定
    paginate_by = 20

    ###### 削除処理 ######
    def post(self, request):
         post_pks = request.POST.getlist('delete')  # <input type="checkbox" name="delete"のnameに対応
         Brand_master.objects.filter(pk__in=post_pks).delete()
         return redirect('kanai_app:Brand_master_ListView')


##################################### バーコード , QR コード生成 ################
class QR_Create(CreateView):

    template_name = 'kanai_app/web_kanri/create_qr.html'
    model = Jan_QR
    fields = ('cr_jan_01', 'cr_qr_01',)

    try :
        success_url = reverse_lazy('kanai_app:')

    except:

        print('バーコード, QRコード生成できませんでした。')

####### バーコード, QRコード表示用    
def listqr(request):

    if request.method == 'POST':

        get_jan = request.POST.get('jan')

        get_qr = request.POST.get('qr')
        
        ### バーコード生成 ###
        a = barcode.get_barcode_class('ean13')
        bb_code = a(get_jan, writer=ImageWriter())
        b_code = bb_code.save('barcode')

        ### QR コード生成 ###
        qr_g = qrcode.make(get_qr)
        buffer = BytesIO()
        qr_g.save(buffer, format="PNG")
        qr = base64.b64encode(buffer.getvalue()).decode().replace("'", "")

    context = {
        'b_code' :b_code,
        'qr': qr,
    }

    return render(request, 
    'kanai_app/web_kanri/create_qr_list.html',
    context)













