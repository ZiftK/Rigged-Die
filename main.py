from die_engine.test_node import TestNode
from die_engine.test_node_execute import TestNodeExecute
from die_engine.command_handler import command
from view.rich.rich_console import RichConsole

view_console = RichConsole()

class Root(TestNode):
    _prefix = ""
    _suffix = ""
    _sys_ns = ""

    @command("test")
    def test(self, param1: str, param2: int):
        """
        """
        print("Test command executed")
        return 
    

if __name__ == "__main__":

    path = __file__.split("\\")
    path = path[:-2]
    path = path.append("test")
    path = "\\".join(path)
    test_console = TestNodeExecute(hierarchy=[Root], stg_path=path, console=view_console)