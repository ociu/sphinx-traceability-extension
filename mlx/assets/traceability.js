// item-tree
jQuery(function () {
    $('ul.bonsai').bonsai();
});

// item (traceability_collapsible_links == True)
jQuery.fn.extend({
    prependHideLinks: function (admonition) {
        var relations = $(this);

        if (relations.children().length > 0) {
            var arrow = $('<i>', {
                class: "fa fa-angle-up",
                click: function () {
                    relations.toggle();
                    $(this).toggleClass("fa-angle-up fa-angle-down");
                }
            });

            var linkColor = relations.children('dt').first().css('color');
            console.log(linkColor);
            var arrowDiv = $('<div>', {
                css: {
                    'display': 'inline-block',
                    'float': 'right',
                    'font-size': '150%',
                    'color': linkColor,
                    'padding-right': '1rem'
                },
                append: arrow
            });
            admonition.after(arrowDiv);
        }
    }
});

$(document).ready(function () {
    $('div.collapsible_links div.admonition:first-child').each(function (i) {
        $(this).siblings('dl.simple').prependHideLinks($(this));
    });
});
