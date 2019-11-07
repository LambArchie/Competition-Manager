(function() {
    var canvas = document.getElementById('graph'),
        context = canvas.getContext('2d');
    window.addEventListener('resize', resizeCanvas, false);
    function resizeCanvas() {
      container = window.getComputedStyle(document.querySelector('.container'))
      canvas.width = parseInt(container.getPropertyValue('width'), 10) - 
                     parseInt(container.getPropertyValue('padding-left'), 10) -
                     parseInt(container.getPropertyValue('padding-right'), 10);
      canvas.height = window.innerHeight - $("#title").height() - 56 - 56;
    }
    resizeCanvas();
})();
  
jQuery(function(graphJSON){
fetch(window.location.pathname + '/json')
    .then(response => response.json())
    .then(json => {
        var graph = new Springy.Graph();
        graph.loadJSON(json);
        var springy = jQuery('#graph').springy({
            graph: graph
        });
    });
});