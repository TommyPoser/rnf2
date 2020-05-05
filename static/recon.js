
function reconRender(response) {
    var animals = response[0];

    if (animals) {
        var status = response[1];

        if (status == 'dead' || status == 'items') {window.location.replace("/recon/");}

        $("#hunt").html(status+'<br>');
        $.each(animals, function (k, v) {
            var behaviour = '';
            if (v[3] == 1) {
                behaviour = 'attacking';
            }
            if (v[3] == 2) {
                behaviour = 'running';
            }
            if (v[3] == 3) {
                $("#hunt").append('<span class="animal animal' + v[4] + '" >' + v[1] + ' | dead</span><br>')
            } else {
                $("#hunt").append('<a id="animal' + v[0] + '" class="animal animal' + v[4] + '" href="#" >' + v[1] + ' -  hit chance: ' + v[2] + ' | ' + behaviour + '</a><br>')
            }
        });
    }
}


function removeLoot() {
    $(".drag").each(function() {
        var initNumber = parseInt($(this).attr('id').match(/initial(\d+)$/)[1], 10);
        if (initNumber > 26) {$(this).hide();}
    });
}

 $(function() {

     $('#hunt').on('click', '.animal', function() {

        var data = $(this).attr('id');

        var animalNumber = parseInt(data.match(/^animal(\d+)$/)[1], 10);

             jQuery.ajax({
            type: "POST",
            async: true,
            url: '/recon/shot/',
            data: $.toJSON(animalNumber),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: function (JsonResponse)
                    {
                        reconRender(JsonResponse);
                    },
            error: function (err)
            { alert(err.responseText)}
        });


     });

     $("#go").click(function () {
             jQuery.ajax({
            type: "POST",
            async: true,
            url: '/recon/recon/',
            data: '',
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: function (JsonResponse)
                    {
                        reconRender(JsonResponse);
                        removeLoot();
                    },
            error: function (err)
            { alert(err.responseText)}
        });


     });


     $("#leave").click(function () {
             jQuery.ajax({
            type: "POST",
            async: true,
            url: '/recon/leave/',
            data: '',
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            success: function (JsonResponse)
                    {
                        reconRender(JsonResponse);
                        removeLoot();
                    },
            error: function (err)
            { alert(err.responseText)}
        });


     });


});