from django.urls import path
from QA.views import HomeView, AceleradorDetailView, QACreateView, RegistoListView, RegistoUpdateView, energia_choices, condicao_choices, export_to_pdf, export_to_excel, export_to_csv, ref_create_view, teste
from django.conf import settings
from django.conf.urls.static import static

app_name = 'QA'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('<slug:acelerador>/', AceleradorDetailView.as_view(), name='acelerador_detail'),
    path('<slug:acelerador>/NovoQA/', QACreateView.as_view(), name='qa_create'),
    path('<slug:acelerador>/Registos/', RegistoListView.as_view(), name='registos_list'),
    path('<slug:acelerador>/Registos/<int:registo_id>/', RegistoUpdateView.as_view(), name='registo_detail'),
    path('<slug:acelerador>/<slug:energia>/NovaReferenciaModal/', ref_create_view, name='ref_create_modal'),
    path('energia_choices_admin/', teste, name='energia_choices_admin'),
    path('condicao_choices_admin/', condicao_choices, name='condicao_choices_admin'),
    path('export_to_pdf/<int:registo_id>/', export_to_pdf, name='export_to_pdf'),
    path('export_to_excel/<slug:slug>/<int:energia_id>/<slug:data_inicial>/<slug:data_final>/', export_to_excel,
         name='export_to_excel'),
    path('export_to_csv/<slug:slug>/<int:energia_id>/<slug:data_inicial>/<slug:data_final>/', export_to_csv,
         name='export_to_csv'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
