let clipboard = new Clipboard('.btn');

document.addEventListener("DOMContentLoaded", function(){
    // copy schedule output table
    clipboard.on('success', function(e) {
        console.log(e);
    });

    clipboard.on('error', function(e) {
        console.log(e);
    });

});
