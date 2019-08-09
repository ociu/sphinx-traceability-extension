// item-tree
jQuery(function () {
    $('ul.bonsai').bonsai();
});

$(document).ready(function () {
    $('div.collapsible_links div.admonition:first-child').each(function (i) {
        $(this).siblings('dl').first().addCollapseButton($(this));
    });

    // show an item's hidden caption on hover
    $('em.has_hidden_caption').each(function (i) {
        var caption = $(this).children('.popup_caption').first();
        var tableCell = caption.parents('td').first();
        var backgroundColor = caption.parents('td').first().css('background-color');
        if ((typeof backgroundColor == 'undefined') || (backgroundColor == 'rgba(0, 0, 0, 0)')) {
            backgroundColor = $('body').css('background-color');
            if (typeof backgroundColor == 'undefined') {
                backgroundColor = 'white';
            }
        }
        $(this).css('position', 'relative');
        caption.hide();  // hide on page load
        caption.css({
            'position': 'absolute',
            'color': 'black',
            'background-color': backgroundColor,
            'padding': '5px',
            'font-weight': 'normal',
            'z-index': '99',
            'white-space': 'pre'
        });
        $(this).hover(
            function(event) {
                caption.css('transform', 'translate(0.3rem, -5px)').show();
            }, function() {
                caption.hide();
            }
        );
    });
});

// item
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

            var linkColor = admonition.children('p').first().css('color');
            var translateX = '0rem'
            var translateY = '-2.5rem'
            if (relations.hasClass('simple')) {
                translateX = '-0.5rem'
                translateY = '-3.9rem'
            }
            var arrow = $('<i>', {
                class: "fa fa-angle-" + arrowDirection,
                css: {
                    'font-size': '135%',
                    'color': linkColor,
                    'float': 'right',
                    'transform': 'translate(' + translateX + ', ' + translateY + ')'
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
