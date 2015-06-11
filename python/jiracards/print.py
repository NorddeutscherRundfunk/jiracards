import logging
import subprocess


def print_pdf(pdf, printer_name, printer_tray):
    logger = logging.getLogger(__name__)

    lp_output = subprocess.check_output(
        ['lp', '-d', printer_name, '-o', 'media={}'.format(printer_tray), pdf],
        universal_newlines=True
    )

    lp_message = lp_output.rstrip()

    logger.info('Printing pdf "%s": "%s"', pdf, lp_message)
    return lp_message
