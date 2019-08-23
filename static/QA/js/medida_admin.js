var $ = django.jQuery.noConflict();

(function($){
    $(function(){
        $(document).ready(function() {
            $('#id_acelerador').bind('change', energia_change);
            $('#id_medidas-0-energia>option').show();
        });
});
})(django.jQuery);

function energia_change()
{
    var acelerador_id = $('#id_acelerador').val();
    $.ajax({
            type     : 'GET',
            url      : '/energia_choices_admin/',
            data     : {'acelerador_id': acelerador_id},
            dataType : 'json',
            success  : function(data){
                alert(data);
                $('#id_medidas-0-energia>option').remove();
                for (var i = 0; i <= data.length; i++) {
                    $('#id_medidas-0-energia').append("<option value=" + data[i].id + ">" + data[i].name + "</option>");
                }
            }
    });
};