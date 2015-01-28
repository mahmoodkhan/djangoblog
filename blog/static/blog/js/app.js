$(document).ready(function() { 
    /* add select2 js library to these dropdowns */
    $("#id_tags").select2();
    
    $("#id_category").select2({
        placeholder: "Select a Category",
        allowClear: true
    });


});

function submitForm(form, formName, successMessage){
    $(form).on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            type: $(form).attr('method'),
            url: $(form).attr('action'),
            data: $(form).serialize(),
            success: function(xhr, ajaxOptions, thrownError)  {
                if ($(xhr).find('.has-error').length > 0 ) {
                    $("#form_modal").find('#modal_content').html(xhr);
                    // called again to register the 'onsubmit' event of the reloaded html form
                    submitForm($(formName), formName, successMessage); 
                } else {
                    $("#form_modal").modal('toggle');
                    createAlert("success", successMessage);
                }
            },
        });
    });
}

function createAlert (type, message) {
    $("#messages").append(
        $(
            "<div class='alert alert-" + type + " dynamic-alert alert-dismissable'>" +
            "<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;</button>" +
            "<p>" + message + "</p>" +
            "</div>"
        )
    );
    // Remove the alert after 30 seconds if the user does not close it.
    $(".dynamic-alert").delay(30000).fadeOut("slow", function () { $(this).remove(); });
}

/*
 * Get a cookie by name.
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*
 * Set the csrf header before sending the actual ajax request
 * while protecting csrf token from being sent to other domains
 */
$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            //console.log("csrftoken: " + getCookie('csrftoken'));
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});