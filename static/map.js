


 $(function() {

     var hexaPicks = [];
     var event = {hexaPicks: hexaPicks};


    $(".hexa").click(function () {

        var ev = $( this );
        var hexaNumber = parseInt(ev.attr('id').match(/^hexa(\d+)$/)[1], 10);

        if (hexaPicks.includes(hexaNumber)) {
            hexaPicks.splice(hexaPicks.indexOf(hexaNumber), 1);
            ev.css('border-width', '0px');
        } else {
            hexaPicks.push(hexaNumber);
            ev.css('border-width', '1px');
        }
        event = {hexaPicks: hexaPicks};
    });

     $("#travel").click(function () {
             jQuery.ajax({
            type: "POST",
            async: true,
            url: '/map/travel/',
            data: $.toJSON(event),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: function (JsonResponse)
                    {
                    $('#hexa'+JsonResponse['start']) .css('border-width', '0px');
                    $('#hexa'+JsonResponse['end']) .css('border-width', '3px');
                    },
            error: function (err)
            { alert(err.responseText)}
        });


     });





});