"""Blueprint «Работа с отчётами» (будет реализован в следующих лабораторных работах)."""
from flask import Blueprint, render_template

from access import group_required

blueprint_report = Blueprint('bp_report', __name__, template_folder='templates')


@blueprint_report.route('/')
@group_required
def report_menu():
    return render_template('report_menu.html')
