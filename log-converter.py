#!/usr/bin/env python

import os
import sys
import json
import pandas as pd


class App:

    def __init__(self, log_src):
        self.log_src = log_src
        with open(self.log_src) as f:
            content = f.readlines()
        self.data = pd.DataFrame()
        table = []
        line = 0
        for element in content:
            line += 1
            elements = element.split(',', 2)
            row = {'id': elements[0], 'ip': elements[1]}
            if bool(elements[2] and elements[2].strip()):
                try:
                    row.update(json.loads(elements[2].translate(str.maketrans("'", "\n"))))
                except:
                    pass
            table.append(row)
        self.data = pd.DataFrame(table)
        print(self.data)

    def run(self):
        pass


def main():
    # noinspection PyBroadException
    try:
        log_src = os.path.join(os.path.dirname(os.path.realpath(__file__)), str(sys.argv[1]))
        App(log_src=log_src).run()
    except:
        pass

if __name__ == '__main__':
    main()