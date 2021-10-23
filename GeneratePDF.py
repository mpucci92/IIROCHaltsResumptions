import pandas as pd
from pandas import DataFrame
import pdfkit as pdf
from jinja2 import Environment, FileSystemLoader
from datetime import date, timedelta, datetime


def generatePDF(path_wkhtmltopdf,path_html_directory,html_file,pdf_file,var1,var2,var3):
    config = pdf.configuration(wkhtmltopdf=path_wkhtmltopdf)

    env = Environment(loader=FileSystemLoader(path_html_directory))
    template = env.get_template('ReportTemplate.html')

    template_vars = {"haltdf": var1, "resumptiondf": var2,"dfUSA": var3}
    html_out = template.render(template_vars)

    # open the html file and put the newly rendered html in it
    with open(html_file, "w") as file:
        file.write(html_out)

    # convert html to pdf

    pdf.from_file(html_file, pdf_file, configuration=config)

def finalGeneratePDF(path_wkhtmltopdf,html_file,pdf_file):
    config = pdf.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf.from_file(html_file, pdf_file, configuration=config)