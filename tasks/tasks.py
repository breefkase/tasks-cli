import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from supporters import tasks_gui
        tasks_gui.main()
    else:
        from supporters import tasks_cli
        tasks_cli.main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("")
        print("Tasks CLI interrupted by keyboard.")
