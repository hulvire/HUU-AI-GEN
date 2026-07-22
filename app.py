from core.bootstrap import bootstrap


def main() -> None:
    context = bootstrap()
    context.run()


if __name__ == "__main__":
    main()