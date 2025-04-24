"""
version 1.0.0
"""
from typing import Type

import rich
import rich.text
import os

from die_engine.command_handler import command, collect_commands
from die_engine.interaction_graph import IGraph
from die_engine.test_node import TestNode
from langs.parse_handler import command_parse

from view.abstract.abs_console import AbsConsole

from die_engine.exceptions import (UninitializedNodeException,
                                                  NodeAlreadyInitializedException,
                                                  NodeAlreadyHasContentException,
                                                  SaveContentException,
                                                  ArgsCountDifferenceException,
                                                  KwArgsDifferenceException,
                                                  InitializeNodeException,
                                                  GenerateContentException
                                                  )

import data_engine.checks as checks


class TestNodeExecute:
    # This dictionary stores the instances of TestNodeExecute.
    # If the hierarchy is not in the record, create a new instance and
    # save it; otherwise, return the existing instance.
    __instances: dict = {}

    _root_file_name: str = ".rt"

    # use class constructor to make a scope pattern
    def __new__(cls,
                hierarchy: list[Type[TestNode]],
                stg_path: str,
                console: AbsConsole,
                *args,
                **kwargs):

        # create a string than identify hierarchy
        hierarchy_string = ".".join([str(name) for name in hierarchy])

        if not (hierarchy_string in cls.__instances):  # if hierarchy id is not in instances keys
            # add new instance to instance map
            cls.__instances[hierarchy_string] = super(TestNodeExecute, cls).__new__(cls)

        # return instance
        return cls.__instances.get(hierarchy_string)

    def __init__(self, *,
                 hierarchy: list[Type[TestNode]],
                 stg_path: str,
                 console: AbsConsole):

        # Only initialize if is the first time that it does
        if not hasattr(self, "_is_init"):

            # concat this class to beginning of the list
            self._hierarchy = [self.__class__] + hierarchy
            self._current_hierarchy_level = 1

            # commands
            self.__commands: dict[str, dict] = collect_commands(self._hierarchy)

            # rich values
            self._console: AbsConsole = console

            # label
            # tree values
            root_label = ""
            if stg_path.count("\\") > 0:
                root_label = stg_path.split("\\")[-1]

            elif stg_path.count("/") > 0:
                root_label = stg_path.split("/")[-1]

            self._i_graph: IGraph = IGraph(
                root_label,
                hierarchy,
                stg_path,
                observers=self._console
            )

            # control values
            self._in_loop = False

            self._stg_path: str = stg_path
            self._is_init = True

    @command("help")
    def help(self, cname=None):
        """
            <help>
            Imprime todos los comandos
            </help>

            <optional>
                <help>
                    Nombre de un comando. Si se recibe el nombre
                    de un comando, se imprimira informacion del comando.
                </help>
                :<name: cname>:
            </optional>

            """

        # get console commands
        global_commands = self.get_console_commands()
        # get node commands
        local_commands = self.get_dummy_commands()

        # union commands
        all_commands = {**global_commands, **local_commands}

        # get Rich Text object
        info = rich.text.Text()
        info.append("\n")

        if not cname:  # if command is None

            aux_global_commands = {}
            for key, val in global_commands.items():
                dcs = val.get("docs")
                dcs = dcs if dcs else {"help": "Parse Error"}
                command_help = dcs.get("help", "NA")
                aux_global_commands.setdefault(key, command_help)

            aux_local_commands = {}
            for key, val in local_commands.items():
                dcs = val.get("docs")
                dcs = dcs if dcs else {"help": "Parse Error"}
                command_help = dcs.get("help", "NA")
                aux_local_commands.setdefault(key, command_help)

            dict_print_config = {
                "key_styles": ["green", "white"],
                "jumps_count_after_key": 0,
                "title_style": "yellow bold",
                "jumps_after_title": 2
            }

            self._console.render_dictionary(
                aux_global_commands,
                **{**dict_print_config, "title": "Global commands"}
            )

            self._console.render_dictionary(
                aux_local_commands,
                **{**dict_print_config, "title": "Node commands"}
            )

            return  # break function

        # recovery command info
        command_dict = all_commands.get(cname, {})
        # alphabetic sorted
        command_dict = dict(sorted(command_dict.items()))

        if not command_dict:
            self._console.logger.error(f"The command '{cname}' is not exists")
            return  # break function

        # recovery command docs
        command_docs = all_commands.get(cname).get("docs")
        # recovery command name
        command_name = all_commands.get(cname).get("callable").command_name

        # format dictionary
        self._console.render_dictionary(
            command_docs,
            key_styles=["bold green", "yellow"],
            title=f"'{command_name}' help",
            title_style="yellow bold",
            jumps_after_title=2
        )

    @command("rhelp")
    def raw_help(self):
        """
        <help>
            Imprime los parametros y opciones de cada comando
            establecidos a nivel de codigo. Aun no se programa...
        </help>
        """

    @command("leave")
    def leave(self):
        """
        <help>
            Termina el ciclo de ejecución de TestConsole
        </help>
        """
        self._in_loop = False

    @command("cls")
    def clear(self):
        """
        <help>
            Limpia la consola
        </help>
        """
        os.system("cls")

    @command("st")
    def show_tree(self, cb=False):
        """
        <help> Imprime el arbol de pruebas </help>
        <optional>
            :<name: cb>:
            :<type: boolean>:
            <help>
                Si se escribe esta bandera de opcion, se impime solamente
                la rama del arbol en la que se encuentre
            </help>
        </optional>
        """

        self._console.render_graph(cb=cb)

    @command("si")
    def show_info(self):

        dm = self._i_graph.dummy
        generals = {
            "Label": dm.label,
            "Prefix": dm.prefix,
            "Suffix": dm.suffix,
            "System path": dm.sys_path,
        }

        self._console.render_dictionary(
            generals,
            key_styles=["bold green"],
            title=f"General info",
            title_style="magenta bold",
            jumps_after_title=2,
            jumps_count_after_key=0
        )

        self._console.render_dictionary(
            dm.status_values,
            key_styles=["bold green"],
            title=f"Status values",
            title_style="magenta bold",
            jumps_after_title=2,
            jumps_count_after_key=0
        )

        if dm.build_params:
            self._console.render_dictionary(
                dm.build_params,
                key_styles=["bold green"],
                title=f"Build params",
                title_style="magenta bold",
                jumps_after_title=2,
                jumps_count_after_key=1
            )

        if dm.parent_build_params:
            self._console.render_dictionary(
                dm.parent_build_params,
                key_styles=["bold green"],
                title=f"Parent build params",
                title_style="magenta bold",
                jumps_after_title=2,
                jumps_count_after_key=1
            )

    @command("sh")
    def show_hierarchy(self):
        """
        <help>
            Show the nodes hierarchy and the current position
            within it
        </help>
        """
        hierarchy_text = rich.text.Text()
        hierarchy_text.append("\n\nHierarchy \n", style="yellow bold")

        current_node_type = self._i_graph.dummy.__class__

        for clss in self._hierarchy:

            if current_node_type is clss:
                hierarchy_text.append(f"{clss.__name__}", style="cyan bold")
                hierarchy_text.append(" <----- You are here :)\n")
                continue
            hierarchy_text.append(f"{clss.__name__}\n", style="default")

        hierarchy_text.append("\n\n")
        self._console.render(hierarchy_text)


    @command("cn")
    def create_child(self, child_name: str, goto: bool = False):
        """
        <help>
            Crea un nodo hijo basandose en la lista de jerarquias y lo
            adjunta al nodo actual.
        </help>

        <param>
            :<name: child_name>:
            <help>
                Etiqueta del nodo hijo.
            </help>
        </param>

        <optional>
            :<name: goto>:
            :<type: boolean>:
            <help>
                Te desplaza al nodo creado.
            </help>
        </optional>

        """

        # check out 1
        if child_name in self._i_graph.dummy.children_labels:
            self._console.logger.error(f"Ya existe un nodo hijo con el nombre '{child_name}'")
            return

        # ---------- Test child
        try:
            child = self._i_graph.add_child_to_dummy(child_name)
        except IndexError:
            self._console.logger.error("Maximum hierarchy level reached")
            return
        except UninitializedNodeException as e:
            self._console.logger.error(e)
            return

        # ---------- Dir
        self._console.logger.info("Creando directorio...")
        os.mkdir(child.sys_path)

        self._console.logger.info("Directorio creado exitosamente.")

        if goto:
            path = child.label
            self.move_to_child(path)

    @command("mvt")
    def move_to_child(self, path: str):
        """
        <help>
            Te desplaza por el grafo usando la ruta especificada.
        </help>
        <param>
            :<name: path>:
            :<type: string>:
            <help>
                Ruta de nodo al que desea moverse.
            </help>
        </param>
        """

        index_list = self._i_graph.move_to_node(path)

        if not index_list:
            self._console.logger.error("Invalid path")
            return

    def get_dummy_commands(self):
        """
        :return: The commands storage in the current dummy
        """
        # Retrieve the class name of the dummy
        dummy_class_name = str(self._i_graph.dummy.__class__.__name__)

        # Retrieve dummy commands
        return self.__commands.get(dummy_class_name, {})

    def get_console_commands(self):
        """
        :return: The global commands storage in the console
        """
        return self.__commands.get(self.__class__.__name__)

    def _execute_function(
            self,
            function: callable,
            command_name: str,
            global_commands: dict,
            args: list,
            kwargs: dict
    ):
        """
        Execute function using correct instance
        :param function: function to execute
        :param command_name: command to execute
        :param global_commands: console commands and dummy commands
        :param args: recovery args
        :param kwargs: recovery kwargs
        """
        instance = self if command_name in global_commands else self._i_graph.dummy
        # Execute callable

        function(
            instance,
            *args,
            **kwargs)

    # ----------------------------------
    # -------- Auxiliar Methods --------
    # ----------------------------------

    def __check_dir(self):
        """
        Load the root node of the tests
        """

        if not checks.dir_exists(self._stg_path):
            ans = self._console.catch_loop(["y", "n"],
                                           f"El directorio {self._stg_path} no existe ¿Desea crearlo?")

            if ans == "n":
                return False

            self._console.logger.info("Creando directorio de pruebas...")
            os.mkdir(self._stg_path)
            file = open(f"{self._stg_path}\\{self._root_file_name}", "w")
            file.write("")
            file.close()

            self._console.logger.info("Directorio de pruebas creado exitosamente.")
            return True

        file_path = f"{self._stg_path}\\{self._root_file_name}"
        if not checks.file_exists(f"{file_path}"):
            ans = self._console.catch_loop(["y", "n"],
                                           f"El directorio {self._stg_path} no es un directorio de pruebas"
                                           f" ¿Desea configurarlo?")

            if ans == "n":
                return False

            with open(file_path, "w") as file:
                file.write("")

        return True

    def __load_nodes(self):
        def load_children(d_node: TestNode, level=2):

            d_node.on_enter_node(load_content=False)

            if level >= len(self._hierarchy):
                return None

            # for each directory in node path
            for dr in os.scandir(d_node.sys_path):

                if dr.name == "__pycache__":
                    continue

                # if not exists directory path
                if not os.path.isdir(dr):
                    continue  # jump to next iteration

                hierarchy_level = self._hierarchy[level]
                prefix = str(hierarchy_level.prefix)
                suffix = str(hierarchy_level.suffix)
                ns = str(hierarchy_level.sys_node_splitter)

                label = dr.name.replace(prefix + ns, "")
                label = label.replace(ns + suffix, "")

                # get child node type
                d_child = self._hierarchy[level].create(label)

                # set as child of current node
                d_node.add_child(d_child)

                load_children(d_child, level + 1)
            d_node.on_leave_node()

        load_children(self._i_graph.root)
        self._i_graph.root.on_enter_node()
        self._console.build_visual_graph_struct(self._i_graph)

    def __command_loop(self):

        self._in_loop = True

        # Retrieve commands in TestNodeExecute class
        global_commands = self.__commands.get(str(self.__class__.__name__), {})

        while self._in_loop:

            try:

                inp = self._console.catch()  # get input from user

                if inp == "":
                    continue

                process_input: dict = command_parse(inp)

                # recovery class commands
                class_commands = self.get_dummy_commands()

                # Merge dummy commands with TestNodeExecute commands
                all_commands = {**global_commands, **class_commands}

                # get command name
                command_name = process_input.get("command")

                # Get callable of the command
                function = all_commands.get(command_name, {}).get("callable")

                if not function:
                    # TODO: replace with log
                    self._console.logger.error("Command was not found")
                    continue

                args = process_input.get("args")
                kwargs = process_input.get("kwargs")

                self._execute_function(
                    function,
                    command_name,
                    global_commands,
                    args,
                    kwargs
                )

            except Exception as e:
                e_str = str(e)

                if e_str.count("()") > 0:
                    e_str = e_str[e_str.index("()") + 2:]
                    e_str = e_str.capitalize()

                tb = e.__traceback__

                while tb:
                    tb_text = f"'{tb.tb_frame.f_code.co_filename}' line {tb.tb_lineno} - {tb.tb_frame.f_code.co_name}"
                    self._console.logger.error(tb_text)
                    tb = tb.tb_next
                self._console.logger.error(e_str)

    def loop(self):

        self._console.logger.info("Iniciando consola...")
        if not self.__check_dir():
            self._console.logger.info("Cerrando consola.")
            return

        self._console.logger.info(f"Cargando datos desde {self._stg_path} ...")

        self.__load_nodes()

        self._console.logger.info("Nodos cargados.")

        self._console.logger.info("Datos cargados exitosamente")

        self.__command_loop()

