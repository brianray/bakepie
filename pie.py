from IPython.display import SVG

def display_pie_factory():
    return SVG(open("static/pie.svg").read())