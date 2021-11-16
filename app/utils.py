from flask import render_template


def render_template_with_nav(file, **kwargs):
    sidebar = render_template("sidebar.html", **kwargs)
    nav = render_template("nav.html", **kwargs)
    
    html = render_template(file, **kwargs)
    html = html.replace('<div id="nav-sidebar"></div>', sidebar)
    html = html.replace('<div id="nav"></div>', nav)

    return html