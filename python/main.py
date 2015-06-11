#!/usr/bin/env python

import logging
import logging.config
import argparse
import sys
import configparser
from jiracards.jiracards import create_card
from jiracards.print import print_pdf


def main():
    logging.config.fileConfig('conf/logging.conf')
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('key', help='key of JIRA issue')
    parser.add_argument('--type', choices=['task', 'bug'],
                        default='task', help='type to print')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--mode', choices=['preview', 'print'],
                        default='preview', help='just save or print directly')

    args = parser.parse_args()

    config = configparser.ConfigParser()
    with open('conf/live.conf') as f:
        config.read_file(f)

    try:
        pdf = create_card(args.key, args.type, config['jira'], args.debug)

        if args.mode == 'print':
            printer_name = config['printer']['name']
            printer_tray = config['printer']['tray']
            logger.info('Printing card for %s(%s) on %s: "%s"',
                        args.key,
                        args.type,
                        printer_name,
                        pdf)
            print_pdf(pdf, printer_name, printer_tray)

    except Exception as e:
        logger.exception(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
