from .ui import TerminalUI


def main():
    ui = TerminalUI()
    # 获取用户输入到程序
    ui.get_request()
    # 按照用户输入执行
    ui.run_request()


if __name__ == "__main__":
    main()
