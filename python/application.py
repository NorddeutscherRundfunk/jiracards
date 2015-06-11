#!/usr/bin/env python

from flask import Flask, send_from_directory, abort, render_template, current_app, g
from jiracards import jiracards
from jiracards.print import print_pdf
import logging
import logging.config
import configparser
from pathlib import Path


def create_app():
    application = Flask(__name__)

    logging.config.fileConfig('conf/logging.conf')

    config = configparser.ConfigParser()
    with open('conf/live.conf') as f:
        config.read_file(f)

    application.config['file'] = config

    return application


app = create_app()


def after_this_request(func):
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func


@app.after_request
def per_request_callbacks(response):
    for func in getattr(g, 'call_after_request', ()):
        response = func(response)
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<issue_key>/<issue_type>')
@app.route('/<issue_key>/<issue_type>/<mode>')
def create_card(issue_key, issue_type, mode='preview'):
    @after_this_request
    def delete_generated_card(response):
        jiracards.delete_card(issue_key)
        return response

    logger = logging.getLogger(__name__)
    try:
        pdf = jiracards.create_card(issue_key, issue_type, current_app.config['file']['jira'])

        if mode == 'print':
            printer_name = current_app.config['file']['printer']['name']
            printer_tray = current_app.config['file']['printer']['tray']
            logger.info('Printing card for %s(%s) on %s: "%s"',
                        issue_key,
                        issue_type,
                        printer_name,
                        pdf)
            print_message = print_pdf(pdf, printer_name, printer_tray)

            return render_template('printed.html',
                                   print_message=print_message,
                                   issue_key=issue_key)
        else:
            return send_from_directory(str(Path(pdf).parent), str(Path(pdf).name))
    except KeyError as e:
        abort(400, e)

if __name__ == '__main__':
    app.debug = False
    app.run(port=5001)
