window.addEventListener("load", function(){
    $('.col-md-4').removeClass('col-md-4').addClass('col-md-12');
    var simplemde = new SimpleMDE({ element: document.getElementById("body") });
    document.getElementById("body").required=false;
});