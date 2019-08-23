var $ = django.jQuery.noConflict();

(function($){
    $(function(){
        $(document).ready(function() {
            $('#id_medida-__prefix__-energia').bind('change', energia_change);
            $('#id_medida-__prefix__-energia >option').show();
        });
});
})(django.jQuery);

function energia_change()
{
    var energia_id = $('#id_medida-0-energia').val();
    $.ajax({
            type     : 'GET',
            url      : '/condicao_choices_admin/',
            data     : {'energia_id': energia_id},
            dataType : 'json',
            success  : function(data){
                $('#id_medida-0-condicao>option').remove();
                for (var i = 0; i <= data.length; i++) {
                    $('#id_medida-0-condicao').append("<option value=" + data[i].id + ">" + data[i].name + "</option>");
                }
            }
    });
};