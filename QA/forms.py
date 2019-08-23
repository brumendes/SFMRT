from django import forms
from django.forms.models import BaseModelFormSet
from QA.models import Medida, Verificacao, Registo, Referencia


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"


class MedidaForm(BaseForm):
    def __init__(self, *args, **kwargs):
        self.value_label = kwargs.pop('value_label')
        super(MedidaForm, self).__init__(*args, **kwargs)
        self.fields['valor'].label = self.value_label

    class Meta:
        model = Medida
        fields = ('energia', 'valor')
        widgets = {
            'energia': forms.HiddenInput,
        }


class BaseMedidasFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.value_labels_list = kwargs.pop('value_labels_list', None)
        super(BaseMedidasFormSet, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        kwargs = super(BaseMedidasFormSet, self).get_form_kwargs(index)
        kwargs['value_label'] = self.value_labels_list[index]
        return kwargs


class VerificacaoForm(BaseForm):
    class Meta:
        model = Verificacao
        fields = ('dfp', 'lasers', 'campo',)


class RegistoForm(BaseForm):
    def __init__(self, *args, **kwargs):
        user_initial = kwargs.pop('user_initial', None)
        data_qa = kwargs.pop('data_qa', None)
        acelerador = kwargs.pop('acelerador', None)
        super(RegistoForm, self).__init__(*args, **kwargs)
        self.fields['autor'].initial = user_initial
        self.fields['data'].initial = data_qa
        self.fields['acelerador'].initial = acelerador

    class Meta:
        model = Registo
        fields = '__all__'
        widgets = {
            'acelerador': forms.HiddenInput,
            'autor': forms.TextInput({'readonly': True}),
            'data': forms.TextInput(attrs={'type': 'date'}),
        }

    def clean(self):
        acelerador = self.cleaned_data.get("acelerador")
        data = self.cleaned_data.get("data")
        autor = self.cleaned_data.get("autor")
        if data == "2018-07-18":
            raise forms.ValidationError("Erro!")


class ReferenciaForm(BaseForm):
    def __init__(self, *args, **kwargs):
        acelerador = kwargs.pop('acelerador', None)
        energia = kwargs.pop('energia', None)
        utilizador = kwargs.pop('utilizador', None)
        super(ReferenciaForm, self).__init__(*args, **kwargs)
        self.fields['acelerador'].initial = acelerador
        self.fields['energia'].initial = energia
        self.fields['utilizador'].initial = utilizador

    class Meta:
        model = Referencia
        fields = '__all__'
        widgets = {
            'acelerador': forms.HiddenInput,
            'energia': forms.HiddenInput,
            'utilizador': forms.HiddenInput,
            'data': forms.TextInput(attrs={'type': 'date'}),
        }
