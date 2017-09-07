#!/usr/bin/env python
"""The main entry point. Invoke as 'cams' or `python cams'.
"""
import sys


def main():
    try:
        from cams.cli import main
        sys.exit(main())
    except KeyboardInterrupt:
        from cams import ExitStatus
        sys.exit(ExitStatus.ERROR_CTRL_C)


if __name__ == '__main__':
    main()

