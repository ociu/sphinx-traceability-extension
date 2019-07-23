jQuery(function () {
    $('ul.bonsai').bonsai();
});

jQuery.fn.extend({
    prependHideLinks: function () {
        var relations = $(this)
        var hideLinks = $('<a>', {
            text: 'Hide links',
            click: function () {
                if (relations.is(':visible')) {
                    relations.hide();
                    $(this).text('Show links');
                } else {
                    relations.show();
                    $(this).text('Hide links');
                }
            }
        });
        if (relations.children().length > 0) {
            console.log(relations.children().length);
            $(this).before(hideLinks);
        }
    }
});

$(document).ready(function () {
    $('div.toggle_links div.admonition:first-child').each(function (i) {
        $(this).siblings('dl.simple').prependHideLinks();
    });
});
