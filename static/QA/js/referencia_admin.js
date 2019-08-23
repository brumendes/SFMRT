var $ = django.jQuery.noConflict();

(function($){
    $(function(){
        $(document).ready(function() {
            $('#id_acelerador').bind('change', acelerador_change);
            $('#id_energia >option').show();
            $('#id_energia').bind('change', energia_change);
            $('#id_condicao >option').show();
        });
});
})(django.jQuery);

function acelerador_change()
{
    var acelerador_id = $('#id_acelerador').val();
    $.ajax({
            type     : 'GET',
            url      : '/energia_choices_admin/',
            data     : {'acelerador_id': acelerador_id},
            dataType : 'json',
            success  : function(data){
                $('#id_energia>option').remove();
                $('#id_energia').prepend("<option value='' selected='selected'>---------</option>");
                for (var i = 0; i <= data.length; i++) {
                    $('#id_energia').append("<option value=" + data[i].id + ">" + data[i].name + "</option>");
                }
            }
    });
};

function energia_change()
{
    var energia_id = $('#id_energia').val();
    $.ajax({
            type     : 'GET',
            url      : '/condicao_choices_admin/',
            data     : {'energia_id': energia_id},
            dataType : 'json',
            success  : function(data){
                $('#id_condicao>option').remove();
                for (var i = 0; i <= data.length; i++) {
                    $('#id_condicao').append("<option value=" + data[i].id + ">" + data[i].name + "</option>");
                }
            }
    });
};