from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.forms import modelformset_factory
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from datetime import date
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

from io import BytesIO
import csv
import xlwt

from QA.models import Acelerador, Condicao, Medida, Registo, Referencia, Energia
from QA.forms import MedidaForm, VerificacaoForm, BaseMedidasFormSet, RegistoForm, ReferenciaForm
from QA.tools import Printer


# Create your views here.
class HomeView(LoginRequiredMixin, ListView):
    template_name = 'QA/home.html'
    model = Acelerador


class AceleradorDetailView(LoginRequiredMixin, ListView):
    template_name = 'QA/acelerador_detail.html'
    order_by = ('registo__data', 'data_criacao')

    def get_queryset(self, **kwargs):
        self.acelerador = get_object_or_404(Acelerador, slug=self.kwargs['acelerador'])
        self.energia = get_object_or_404(Energia, slug=self.request.GET.get('energia', self.acelerador.energias.first()))
        self.initial_date = self.request.GET.get('initial_date', date(date.today().year - 1, date.today().month, date.today().day))
        self.final_date = self.request.GET.get('final_date', date.today())
        new_context = Medida.objects.filter(registo__acelerador=self.acelerador).filter(registo__data__gte=self.initial_date, registo__data__lte=self.final_date).filter(
            energia=self.energia)
        medidas = [
            [str(m.registo.data.strftime('%Y-%m-%d')),
            m.valor,
            m.get_point_style(),
            m.referencia.valor,
            m.referencia.valor * 0.980,
            m.referencia.valor * 0.985,
            m.referencia.valor * 1.015,
            m.referencia.valor * 1.020,
            ] for m in new_context]
        return medidas

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial_date = self.request.GET.get('initial_date', date(date.today().year - 1, date.today().month, date.today().day).strftime('%Y-%m-%d'))
        final_date = self.request.GET.get('final_date', date.today().strftime('%Y-%m-%d'))
        refs_list = self.energia.referencias.all()
        if self.acelerador.referencias_acelerador.all():
            context['load_qa'] = True
        else:
            context['load_qa'] = None
        if refs_list.filter(acelerador=self.acelerador):
            ref = refs_list.filter(acelerador=self.acelerador).order_by('-data').latest()
        else:
            ref = None
        form = ReferenciaForm(acelerador=self.acelerador, energia=self.energia, utilizador=self.request.user)          
        context['acelerador'] = self.acelerador
        context['energia'] = self.energia
        context['initial_date'] = initial_date
        context['final_date'] = final_date
        context['ref'] = ref
        context['form'] = form
        return context


class QACreateView(LoginRequiredMixin, CreateView):
    template_name = 'QA/registo_create.html'
    model = Registo
    form_class = RegistoForm

    def get_form_kwargs(self):
        kwargs = super(QACreateView, self).get_form_kwargs()
        data_qa = date.today().strftime("%Y-%m-%d")
        user_initial = self.request.user
        acelerador = Acelerador.objects.get(slug=self.kwargs['acelerador'])
        kwargs['user_initial'] = user_initial
        kwargs['data_qa'] = data_qa
        kwargs['acelerador'] = acelerador
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        condicoes = Condicao.objects.all()
        data_qa = date.today().strftime("%d-%m-%Y")
        acelerador = Acelerador.objects.get(slug=self.kwargs['acelerador'])
        energias = acelerador.energias.all().order_by('valor').order_by('-tipo')
        refs = []
        initial_values = []
        value_labels_list = []
        for e in energias:
            if e.referencias.all().filter(acelerador=acelerador):
                latest_ref = e.referencias.all().filter(acelerador=acelerador).latest()
                refs.append(latest_ref)
                initial_values.append({'energia': e, 'ref': latest_ref})
                value_labels_list.append(str(e))
        MedidasFormSet = modelformset_factory(Medida, form=MedidaForm, formset=BaseMedidasFormSet, extra=len(refs))
        if self.request.POST:
            context['verform'] = VerificacaoForm(self.request.POST)
            context['formset'] = MedidasFormSet(self.request.POST, initial=initial_values,
                                                value_labels_list=value_labels_list)
        else:
            context['verform'] = VerificacaoForm
            context['formset'] = MedidasFormSet(queryset=Medida.objects.none(), initial=initial_values,
                                                value_labels_list=value_labels_list)
        context['acelerador'] = acelerador
        context['condicoes'] = condicoes
        context['data_qa'] = data_qa
        context['refs'] = refs
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        form = self.get_form()
        verform = context['verform']
        formset = context['formset']
        if form.is_valid() and formset.is_valid() and verform.is_valid():
            form.save()
            med_instances = formset.save(commit=False)
            for med_instance in med_instances:
                med_instance.registo = form.instance
                med_instance.referencia = med_instance.get_current_reference()
                if med_instance.analyse() == 'warning':
                    messages.add_message(self.request, messages.WARNING,
                                         str(med_instance.energia) + ' próximo da tolerância! Avise o SFM.')
                elif med_instance.analyse() == 'fail':
                    messages.add_message(self.request, messages.ERROR,
                                         str(med_instance.energia) + ' fora da tolerância! Contacte o SFM.')
                med_instance.save()
            ver_instance = verform.save(commit=False)
            ver_instance.registo = form.instance
            if ver_instance.analyse() == "fail":
                messages.add_message(self.request, messages.ERROR, 'Falha na verificação mecânica! Contacte o SFM.')
            ver_instance.save()
            messages.add_message(self.request, messages.SUCCESS, 'QA realizado com sucesso!')
        else:
            messages.add_message(self.request, messages.ERROR, 'Formulário inválido. Reveja por favor.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('QA:acelerador_detail', kwargs={'acelerador': self.kwargs['acelerador']})


class RegistoListView(LoginRequiredMixin, ListView):
    template_name = 'QA/registos_list.html'
    model = Registo
    paginate_by = 10
    order_by = ('data', 'data_criacao')

    def get_queryset(self, **kwargs):
        acelerador = get_object_or_404(Acelerador, slug=self.kwargs['acelerador'])
        initial_date = self.request.GET.get('initial_date', date(date.today().year - 1, date.today().month, date.today().day))
        final_date = self.request.GET.get('final_date', date.today())
        new_context = acelerador.registos.filter(data__gte=initial_date, data__lte=final_date)
        return new_context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        acelerador = get_object_or_404(Acelerador, slug=self.kwargs['acelerador'])
        initial_date = self.request.GET.get('initial_date', date(date.today().year - 1, date.today().month, date.today().day).strftime('%Y-%m-%d'))
        final_date = self.request.GET.get('final_date', date.today().strftime('%Y-%m-%d'))
        context['acelerador'] = acelerador
        context['initial_date'] = initial_date
        context['final_date'] = final_date
        return context


class RegistoUpdateView(LoginRequiredMixin, DetailView):
    template_name = 'QA/registo_detail.html'
    model = Registo

    def get_object(self, queryset=None):
        object = Registo.objects.get(id=self.kwargs['registo_id'])
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        condicoes = Condicao.objects.all()
        context['condicoes'] = condicoes
        return context


def ref_create_view(request, acelerador, energia):
    if request.method == "POST":
        form = ReferenciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Referência criada com sucesso!')
            return HttpResponseRedirect(reverse('QA:acelerador_detail', kwargs={'acelerador': acelerador}))
        else:
            print(form.errors)


def energia_choices(request):
    acelerador_id = request.GET.get('acelerador_id', None)
    if acelerador_id:
        acelerador = Acelerador.objects.get(id=acelerador_id)
        energias = acelerador.energias.all()
    else:
        energias = Energia.objects.all()
    energias_list = [{'id': e.id, 'name': str(e)} for e in energias]
    return JsonResponse(energias_list, safe=False, content_type='application/javascript')


def teste(request):
    print(request)
    return JsonResponse('teste', safe=False, content_type='application/javascript')


def condicao_choices(request):
    energia_id = request.GET.get('energia_id', None)
    if energia_id:
        energia = Energia.objects.get(id=energia_id)
        condicao = Condicao.objects.filter(tipo=energia.tipo)
    else:
        condicao = Condicao.objects.all()
    data = [{'id': c.id, 'name': str(c)} for c in condicao]
    return JsonResponse(data, safe=False, content_type='application/javascript')


def export_to_pdf(request, registo_id):
    registo = Registo.objects.get(id=registo_id)
    response = HttpResponse(content_type='application/pdf')
    response_text = 'attachment; filename="' + str(registo) + '.pdf"'
    response['Content-Disposition'] = response_text
    buffer = BytesIO()
    printer = Printer(buffer, 'A4')
    pdf = printer.to_pdf(registo)
    response.write(pdf)
    return response


def export_to_excel(request, slug, energia_id, data_inicial, data_final):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="medidas.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Acelerador', 'Data', 'Energia', 'Referência', 'Valor', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    acelerador = Acelerador.objects.get(slug=slug)
    medidas = Medida.objects.filter(registo__acelerador=acelerador).filter(energia=energia_id).filter(
        registo__data__gte=data_inicial, registo__data__lte=data_final).order_by('registo__data')

    rows = medidas.values_list('registo__acelerador__slug', 'registo__data', 'energia__slug', 'referencia__valor',
                               'valor')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


def export_to_csv(request, slug, energia_id, data_inicial, data_final):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="medidas.csv"'

    writer = csv.writer(response)
    writer.writerow(['Acelerador', 'Data', 'Energia', 'Referência', 'Valor'])

    acelerador = Acelerador.objects.get(slug=slug)
    medidas = Medida.objects.filter(registo__acelerador=acelerador).filter(energia=energia_id).filter(
        registo__data__gte=data_inicial, registo__data__lte=data_final).order_by('registo__data')

    medidas = medidas.values_list('registo__acelerador__slug', 'registo__data', 'energia__slug', 'referencia__valor',
                                  'valor')
    for m in medidas:
        writer.writerow(m)

    return response
