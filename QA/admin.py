from django.contrib import admin
from QA.models import Fabricante, Acelerador, Energia, Referencia, Condicao, Medida, Verificacao, Registo


# Register your models here.
class AceleradorAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'nserie', 'modelo')
    filter_horizontal = ('energias',)


class EnergiaAdmin(admin.ModelAdmin):
    exclude = ['slug', ]
    list_display = ('id', 'slug', 'tipo', 'valor', 'obs')
    list_filter = ['tipo']


class ReferenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'acelerador', 'energia', 'valor', 'data', 'utilizador')
    list_filter = ['acelerador', 'energia', 'data']
    list_per_page = 15

    class Media:
        js = ('/static/QA/js/referencia_admin.js',)


class CondicaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'gantry', 'dfp', 'campo', 'cone', 'dose', 'colimador', 'pmma', 'notas')


class MedidaInline(admin.TabularInline):
    model = Medida
    extra = 0

    class Media:
        js = ('/static/QA/js/medida_admin.js',)


class VerificacaoInline(admin.TabularInline):
    model = Verificacao
    extra = 0


class MedidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'registo', 'energia', 'valor', 'referencia')
    list_filter = ['registo__acelerador', 'energia', 'registo__data']
    list_per_page = 15

    def get_ref(self, obj):
        return obj.get_current_reference(obj.registo.acelerador, obj.energia, obj.registo.data)

    def get_ref_value(self, obj):
        return self.get_ref(obj).valor
    get_ref_value.short_description = 'Valor Referência'
    get_ref_value.admin_order_field = 'ref__valor'

    def get_ref_date(self, obj):
        return self.get_ref(obj).data
    get_ref_date.short_description = 'Data Referência'
    get_ref_date.admin_order_field = 'ref__data'


class VerificacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'registo', 'dfp', 'lasers', 'campo')
    list_filter = ['registo__acelerador', 'registo__data']
    list_per_page = 15


class RegistoAdmin(admin.ModelAdmin):
    list_display = ('id', 'acelerador', 'data', 'autor')
    inlines = [MedidaInline, VerificacaoInline]
    list_filter = ['acelerador']
    list_per_page = 15

    class Media:
        js = ('/static/QA/js/registo_admin.js',)


admin.site.register(Fabricante)
admin.site.register(Acelerador, AceleradorAdmin)
admin.site.register(Energia, EnergiaAdmin)
admin.site.register(Referencia, ReferenciaAdmin)
admin.site.register(Condicao, CondicaoAdmin)
admin.site.register(Medida, MedidaAdmin)
admin.site.register(Verificacao, VerificacaoAdmin)
admin.site.register(Registo, RegistoAdmin)
