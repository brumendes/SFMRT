from django.db import models
from django.urls import reverse
from django.shortcuts import get_object_or_404

TIPO_CHOICES = (
    ("Electrões", "Electrões"),
    ("Fotões", "Fotões"),
)


# Create your models here.
class Fabricante(models.Model):
    fabricante = models.CharField("Fabricante", max_length=20)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s" % self.fabricante


class Energia(models.Model):
    slug = models.SlugField("Designação", max_length=20, unique=True)
    tipo = models.CharField(choices=TIPO_CHOICES, max_length=20)
    valor = models.IntegerField(help_text="Valor nominal da energia (MV - fotões; MeV - electrões).")
    obs = models.CharField(max_length=50, null=True, blank=True, help_text="Exemplo: SRS")
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("tipo", "valor", "obs")]


    def save(self, *args, **kwargs):
        self.slug = self.get_name()
        super(Energia, self).save(*args, **kwargs)

    def get_latest_ref(self):
        return self.referencias.latest()

    def get_name(self):
        if not self.obs:
            if self.tipo == "Electrões":
                unidade = "MeV"
            else:
                unidade = "MV"
            return "%s%s" % (self.valor, unidade)
        else:
            if self.tipo == "Electrões":
                unidade = "MeV"
            else:
                unidade = "MV"
            return "%s%s%s" % (self.valor, unidade, self.obs)

    def __str__(self):
        return "%s" % self.get_name()


class Acelerador(models.Model):
    slug = models.SlugField("Nome", max_length=20, unique=True)
    nserie = models.CharField("Número de Série", max_length=10)
    fabricante = models.ForeignKey(Fabricante, null=True, blank=True, on_delete=models.SET_NULL)
    modelo = models.CharField("Modelo", max_length=10)
    energias = models.ManyToManyField(Energia, related_name="aceleradores")
    imagem = models.ImageField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Aceleradores"

    def get_absolute_url(self):
        return reverse('QA:acelerador_detail', kwargs={'acelerador': self.slug})

    def get_latest_registo(self):
        return self.registos.latest()

    def __str__(self):
        return '%s' % self.slug


class Condicao(models.Model):
    CAMPO_CHOICES = (
        ("5x5", "5x5"),
        ("8x8", "8x8"),
        ("10x10", "10x10"),
        ("12x12", "12x12"),
        ("15x15", "15x15"),
        ("20x20", "20x20"),
        ("25x25", "25x25"),
    )
    CONE_CHOICES = (
        ("10x10", "10x10"),
        ("15x15", "15x15"),
        ("20x20", "20x20"),
        ("25x25", "25x25"),
    )
    tipo = models.CharField(choices=TIPO_CHOICES, max_length=20, blank=True)
    gantry = models.FloatField(help_text="Ângulo de inclinição da Gantry.")
    dfp = models.FloatField(help_text="Distância Foco-pele em cm.")
    campo = models.CharField(choices=CAMPO_CHOICES, max_length=10, help_text="Tamanho de campo em cm2")
    cone = models.CharField(choices=CONE_CHOICES, blank=True, max_length=10, help_text="Só para electrões")
    dose = models.FloatField(help_text="Dose em MU")
    colimador = models.FloatField(help_text="Posição do colimador.")
    pmma = models.FloatField(help_text="Espessura de placas de PMMA em mm (só para fotões).")
    notas = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Condição"
        verbose_name_plural = "Condições"

    def __str__(self):
        return '%s' % self.tipo


class Referencia(models.Model):
    utilizador = models.CharField(max_length=30)
    acelerador = models.ForeignKey(Acelerador, on_delete=models.CASCADE, related_name='referencias_acelerador')
    energia = models.ForeignKey(Energia, on_delete=models.CASCADE, related_name='referencias')
    valor = models.FloatField(help_text="Introduza o valor de referência para as condições de medida seleccionadas.")
    data = models.DateField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Referência"
        verbose_name_plural = "Referências"
        get_latest_by = 'data'

    def get_tolerance_sup(self):
        tolerance_sup = self.valor * 1.020
        return tolerance_sup

    def get_tolerance_inf(self):
        tolerance_inf = self.valor * 0.980
        return tolerance_inf

    def __str__(self):
        return '%s %s' % (self.energia, self.data)


class Registo(models.Model):
    acelerador = models.ForeignKey(Acelerador, on_delete=models.CASCADE, related_name='registos')
    data = models.DateField()
    autor = models.CharField("Realizado por:", max_length=50)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'data'
        ordering = ["-data", "data_criacao"]

    def get_absolute_url(self):
        return reverse('QA:registo_detail', kwargs={'acelerador': self.acelerador.slug, 'registo_id': self.pk})

    def get_summary(self):
        results = []
        for m in self.medidas.all():
            results.append(m.analyse())
        if 'warning' in results:
            summary = 'warning'
        elif 'fail' in results:
            summary = 'fail'
        else:
            summary = 'pass'
        return summary

    def __str__(self):
        return '%s %s' % (self.acelerador, self.data)


class Medida(models.Model):
    registo = models.ForeignKey(Registo, on_delete=models.CASCADE, related_name='medidas')
    energia = models.ForeignKey(Energia, on_delete=models.CASCADE)
    referencia = models.ForeignKey(Referencia, on_delete=models.CASCADE, related_name='ref_medidas', null=True)
    valor = models.FloatField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def get_current_reference(self):
        return Referencia.objects.filter(acelerador=self.registo.acelerador, energia=self.energia).order_by('-data').latest()

    def analyse(self):
        if self.referencia:
            ref = self.referencia.valor
            valor = self.valor
            if ref * 1.015 <= valor < ref * 1.020:
                result = 'warning'
            elif ref * 0.985 <= valor < ref * 1.015:
                result = 'pass'
            elif ref * 0.980 <= valor < ref * 0.985:
                result = 'warning'
            else:
                result = 'fail'
        else:
            result = None
        return result

    def get_point_style(self):
        analyse = self.analyse()
        if analyse == 'fail':
            point_style = 'point { fill-color: red; }'
        elif analyse == 'warning':
            point_style = 'point { fill-color: orange; }'
        else:
            point_style = 'point { fill-color: green; }'
        return point_style

    def __str__(self):
        return '%s %s' % (self.registo, self.energia)


class Verificacao(models.Model):
    PASS_CHOICES = (
        ("X", "X"),
        ("V", "V"),
    )
    registo = models.ForeignKey(Registo, on_delete=models.CASCADE, related_name='verificacao')
    dfp = models.CharField("DFP", max_length=10, choices=PASS_CHOICES)
    lasers = models.CharField("Lasers", max_length=10, choices=PASS_CHOICES)
    campo = models.CharField("Tamanho de campo", max_length=10, choices=PASS_CHOICES)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Verificação"
        verbose_name_plural = "Verificações"

    def analyse(self):
        if self.dfp == "X" or self.lasers == "X" or self.campo == "X":
            result = "fail"
        else:
            result = "pass"
        return result

    def __str__(self):
        return '%s, %s' % (self.registo, "Verificação")
