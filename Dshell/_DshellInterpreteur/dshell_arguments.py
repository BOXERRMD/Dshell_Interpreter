from Dshell.full_import import Any, Union
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT

class DshellArgumentsData:
    """
    Data structure for a Dshell argument containing value, type, and whether it's obligatory.
    """

    def __init__(self, value: Any, obligatory: bool, type_: DTT):
        """
        Initialize argument data.
        :param value: The argument value
        :param obligatory: Whether this argument is required
        :param type_: The token type of this argument
        """
        self.value: Any = value
        self.type: DTT = type_
        self.obligatory: bool = obligatory

    def __repr__(self) -> str:
        return f"DshellArgumentsData(value={self.value}, obligatory={self.obligatory})"

    def __str__(self) -> str:
        return str(self.value)

class DshellArguments:
    """
    Manage Dshell parameters and arguments passed to a command call.
    Example: !ban @user reason for ban
    """

    def __init__(self):
        """Initialize with empty parameters except for non-specified parameters list."""
        self.parameters: dict[str, DshellArgumentsData] = {
            '*': DshellArgumentsData([], False, DTT.LIST)  # Non-specified parameters
        }

    def set_parameter(self, name: str, value: Any, type_: DTT, obligatory: bool = False) -> None:
        """
        Set a parameter with its type and value.
        :param name: Name of the parameter
        :param value: Value of the parameter
        :param type_: Token type of the parameter
        :param obligatory: Whether this parameter is required
        """
        self.parameters[name] = DshellArgumentsData(value, obligatory, type_)

    def get_parameter(self, name: str) -> DshellArgumentsData:
        """
        Get a parameter by its name.
        :param name: Parameter name
        :return: Parameter data or None data if not found
        """
        return self.parameters.get(name, DshellArgumentsData(None, False, DTT.NONE))

    def update_parameter(self, name: str, value: DshellArgumentsData) -> None:
        """
        Update a parameter value if it exists and types match.
        :param name: Name of the parameter
        :param value: New parameter data
        """
        if name in self.parameters and self.get_parameter(name).type == value.type:
            self.parameters[name] = value

    def get_dict_parameters(self) -> dict[str, Union[Any, None]]:
        """
        Get all parameters as a dictionary.
        :return: Dictionary mapping parameter names to their values
        """
        return {name: data.value for name, data in self.parameters.items()}

    def get_non_specified_parameters(self) -> list[Any]:
        """
        Get all non-specified parameters (those stored under the '*' key).
        :return: List of non-specified parameter values
        """
        return self.parameters['*'].value

    def add_non_specified_parameters(self, value: Any) -> None:
        """
        Add a non-specified parameter.
        :param value: The parameter value to add
        """
        self.parameters['*'].value.append(value)

    def __repr__(self) -> str:
        return str(self.parameters)