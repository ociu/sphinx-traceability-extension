# -*- coding: utf-8 -*-

from sphinx_testing import with_app


@with_app(buildername='html', srcdir='tests/docs/basic/')
def test_build_html(app, status, warning):
    app.builder.build_all()


@with_app(buildername='singlehtml', srcdir='tests/docs/basic/')
def test_build_singlehtml(app, status, warning):
    app.builder.build_all()


@with_app(buildername='latex', srcdir='tests/docs/basic/')
def test_build_latex(app, status, warning):
    app.builder.build_all()


@with_app(buildername='epub', srcdir='tests/docs/basic/')
def test_build_epub(app, status, warning):
    app.builder.build_all()


@with_app(buildername='json', srcdir='tests/docs/basic/')
def test_build_json(app, status, warning):
    app.builder.build_all()
