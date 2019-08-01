// item-tree
jQuery(function () {
    $('ul.bonsai').bonsai();
});


// item
$(document).ready(function () {
    $('div.collapsible_links div.admonition:first-child').each(function (i) {
        $(this).siblings('dl.simple').addCollapseButton($(this));
    });
});

jQuery.fn.extend({
    addCollapseButton: function (admonition) {
        var relations = $(this);

        if (relations.children().length > 0) {
            if (admonition.parent().hasClass('collapse')) {
                // collapse relations and attributes list for each item on page load
                relations.toggle();
                arrowDirection = 'down';
            } else {
                arrowDirection = 'up';
            }

            var linkColor = relations.children('dt').first().css('color');
            var arrow = $('<i>', {
                class: "fa fa-angle-" + arrowDirection,
                css: {
                    'font-size': '135%',
                    'color': linkColor,
                    'float': 'right',
                    'transform': 'translate(-0.5rem, -1.4rem)'
                },
                click: function () {
                    relations.toggle('fold');
                    $(this).toggleClass("fa-angle-up fa-angle-down");
                }
            });
            admonition.after(arrow);
        }
    }
});
