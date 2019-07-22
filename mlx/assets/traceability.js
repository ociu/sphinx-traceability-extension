$(document).ready(function () {
    $('<a>', {
        text: 'Hide links',
        click: function () {
            //alert($(this).siblings()[0].innerHTML);
            var p = $(this).siblings()[0];
            //alert(p.innerHTML);
            var relations = $(this).siblings('dl.simple')
            if (relations.is(':visible')) {
                relations.hide();
                $(this).text('Show links');
            } else {
                relations.show();
                $(this).text('Hide links');
            }
        }
    }).insertAfter('div.toggle_links div.admonition:first-child');
});

jQuery(function() {
    $('ul.bonsai').bonsai();
});
