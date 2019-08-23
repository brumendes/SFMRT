var $ = django.jQuery.noConflict();

(function($){
    $(function(){
        $(document).ready(function() {
            $('#id_acelerador').bind('change', acelerador_change);
            $('#id_energia >option').show();
        });
});
})(django.jQuery);

// based on acelerador, energia will be loaded

function acelerador_change()
{
    var acelerador_id = $('#id_acelerador').val();
    $.ajax({
            "type"     : "GET",
            "url"      : "QA/energia_choices_admin/",
            "dataType" : "json",
            "cache"    : false,
            "success"  : function(json) {
                            alert("Teste")
                $('#id_energia >option').remove();
/* 				$.each(data, function(index,value) {
					$('#id_energia').append($("<option>").val(value).text));
				});  */
                for(var j = 0; j < json.length; j++){
                    $('#id_energia').append($('<option></option>').val(json[j][0]).text(json[j][1]));
                }
            }           
    })(django.jQuery);
};