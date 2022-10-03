from django.urls import path
from . import views
from django.contrib import admin


### ログイン用
from django.contrib.auth import views as django_auth_views

app_name = 'kanai_app'

urlpatterns = [

   ######################### 表示用　ページ #########################

    path('lp', views.Lp.as_view(), name="lp"),

    path('lp/toriatukai/', views.category_all, name="toriatukai"),

    path('lp/toriatukai/<int:Medium_code>/',views.GET_Medium_code, name='GET_Medium_code'),

    path('lp/toriatukai/detail<int:pk>',views.Medium_Shouhin_detail, name='Medium_Shouhin_detail'),

    ### 検索
    path('lp/test_list/', views.LpList.as_view(), name='LpList'),
    path('lp/test_list/detail<int:pk>/', views.detail, name='detail'),

    ####### 企業情報 ページ
    path('lp/Corporate_info/', views.Corporate_info.as_view(), name="Corporate_info"),

    ####### 採用情報　ページ
    path('lp/employment_info/', views.Employment_info.as_view(), name="employment_info"),

    ####### お問い合わせ　ページ
    path('lp/contact_info/', views.Contact_info.as_view(), name="contact_info"),

    ######################### 管理画面ページ #########################

    path('kanri_top/',views.kanri_top, name="kanri_top"),

     ### ログイン Login
   # path('', views.Login.as_view(), name='login'),
    ### ログアウト
#   path('logout', django_auth_views.LogoutView.as_view(), name="logout"),
     
    ### サインアップ
#   path('sign_up/', views.SignUp.as_view(), name='sign_up'), 
#   path('sign_up/done/<token>', views.SignUpDone.as_view(), name='sign_up_done'),

    ### CSV アップロード
    path('csv_upload/', views.upload, name="csv_upload_01"),
    path('csv_download/', views.csv_download, name="csv_download"),

    ### WEB表示　取扱商品　大カテゴリー　追加
    path('To_Cate_new/', views.Toriatukai_Cate_new, name="Toriatukai_Cate_new"),

    ### 中カテゴリー　追加
    path('Ch_Cate_new/', views.Medium_categoryForm_new, name="Medium_categoryForm_new"),
    path('Ch_Cate_new/ch_list/', views.Medium_categoryListView.as_view(), name="Medium_categoryListView"),
    path('Ch_Cate_new/update/<int:pk>',views.Medium_categoryUpdateView.as_view(), name="Medium_categoryUpdateView"),

    path('Ch_Cate_new/delete/<int:pk>',views.Medium_categoryDeleteView.as_view(), name="medium_categorydelete"),
    
    ### テスト商品ページ 新規追加
    path('Test_S_01', views.Test_shouhin_010_new, name="Test_shouhin_010_new"),
    ### 商品一覧ページ
    path('kanri_s/', views.Test_shouhin_010_Kanri_ListView.as_view(), name="kanri_s"),
    path('kanri_s/<int:pk>/update/', views.Test_shouhin_010_Kanri_UpdateView.as_view(), name="kanri_s-uodate"),

    ################# オリジナル商品管理
    path('Or_cate_new/', views.Original_Cate_new, name="Original_Cate_new"),

    ####　オリジナル商品　カテゴリー　一覧
    path('Or_cate_list/', views.Original_CateListView.as_view(), name="Original_CateListView"),

    ######### 新着情報　（news） 登録情報
    path('create_news/', views.Post_new, name="create_news"),

    ############################## マスター関連
    ###### メーカー　新規登録
    path('maker_master/new', views.Maker_master_new, name="Maker_master_new"),
    path('maker_master/list', views.Maker_masterListView.as_view(), name="Maker_masterListView"),

    ###### ブランド　登録
    path('brand_master/new/', views.Brand_master_new, name="Brand_master_new"),
    path('brand_master/list', views.Brand_master_ListView.as_view(), name="Brand_master_ListView"),

    ############################## バーコード, QRコード生成
    path('create_qr/', views.QR_Create.as_view(), name="create_qr"),
    path('create_qr/list/', views.listqr, name="listqr"),


    ### ユーザー関係
  #  path('user_list/', views.UserListView.as_view(), name="user_list"),

]