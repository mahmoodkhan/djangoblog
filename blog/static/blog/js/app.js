$(document).ready(function() { 
    $("#id_tags").select2();
    
    $("#id_category").select2({
        placeholder: "Select a Category",
        allowClear: true
    });

    $("#id_blogpost").select2();
});