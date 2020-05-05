
function allowDrop(ev) {
    var entNumber = parseInt(ev.target.id.match(/^div(\d+)$/)[1], 10);

    if (!ev.target.hasChildNodes() && entNumber <= 26 ) {
        ev.preventDefault();
    }
}

function dragStart(ev) {
    ev.dataTransfer.setData("ItemID", ev.target.id);
}

function drop(ev) {
    this.classList.remove('over');
    ev.preventDefault();
    var data = ev.dataTransfer.getData("ItemID");
    ev.target.appendChild(document.getElementById(data));

    var dragNumber = parseInt(data.match(/^drag(\d+)/)[1], 10);
    var initNumber = parseInt(data.match(/initial(\d+)$/)[1], 10);
    var entNumber = parseInt(ev.target.id.match(/^div(\d+)$/)[1], 10);
    var toCraft = $('input[name=craft]:checked').val();

    $('#'+data).prop('id', 'drag'+dragNumber+'initial'+entNumber);

    if (!toCraft) {toCraft = ''}

    var event = {entNumber: entNumber, dragNumber: dragNumber, initNumber: initNumber, toCraft: toCraft};

    var path = window.location.pathname;

    jQuery.ajax({
        type: "POST",
        async: true,
        url: path+'drag_and_drop/',
        data: $.toJSON(event),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function (JsonResponse)
                {
                    if (path == '/inventory/') {inventoryRender(JsonResponse);}
                    if (path == '/recon/') {reconRender(JsonResponse);}
                },
        error: function (err)
        { alert(err.responseText)}
    });
}


function inventoryRender(response) {
    if (response['build']) {
        $("#item_to_craft").html(response["name"] + ' level: ' + response["level"] + ' coal: ' + response["coal"]);
    } else  {
        $("#item_to_craft").html('');
    }
}


function handleDragEnter(ev) {
    if (!ev.target.hasChildNodes()) {
        this.classList.add('over');
    }
}

function handleDragLeave() {
  this.classList.remove('over');
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ************* Here goes LOAD event listener *************************************
window.addEventListener('load',function(){

  var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });


    var divs = document.querySelectorAll('.grid .ent');
    [].forEach.call(divs, function(div) {
      div.addEventListener('dragenter', handleDragEnter, false);
      div.addEventListener('dragover', allowDrop, false);
      div.addEventListener('dragleave', handleDragLeave, false);
      div.addEventListener('drop', drop, false);
    });

    var drags = document.querySelectorAll('.grid .drag');
    [].forEach.call(drags, function(drag) {
      drag.addEventListener('dragstart', dragStart, false);
      drag.setAttribute('draggable', 'true');
      //col.addEventListener('dragend', handleDragEnd, false);
    });


}, true);
