from django_filters import FilterSet, ModelChoiceFilter

from QA.models import Registo, Energia, Acelerador


class BaseFilter(FilterSet):
    def __init__(self, *args, **kwargs):
        super(FilterSet, self).__init__(*args, **kwargs)
        for field in self.form:
            field.field.widget.attrs['class'] = "form-control mt-3 ml-2"


def energias(request):
    if request is None:
        print("None")
        return Energia.objects.none()

    acelerador_slug = request.slug
    acelerador = Acelerador.objects.get(slug=acelerador_slug)
    return acelerador.energias_set.all()


class MedidasFilter(BaseFilter):
    medidas__energia = ModelChoiceFilter(label="Energia: ", queryset=energias)

    def __init_(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('request', self.request)

    class Meta:
        model = Registo
        fields = ['medidas__energia']
