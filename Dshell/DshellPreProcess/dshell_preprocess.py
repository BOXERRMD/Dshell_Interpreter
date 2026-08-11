from ..full_import import findall, sub, MULTILINE, StrEnum

class PreProcessorInstructions(StrEnum):
    DEFINE = "define"

class PreProcessorData:
    def __init__(self, instruction: str, symbol: str, value: str):
        self.instruction = instruction
        self.symbol = symbol
        self.value = value

def define(code: str, pre_processor_data: PreProcessorData) -> str:
    """
    Replace all symbol with the current value
    :param code: the code before tokenization
    :param pre_processor_data: all data for the ##define pre-processor
    :return:
    """
    return sub(f"(?<![a-zA-Z]){pre_processor_data.symbol}(?![a-zA-Z])", pre_processor_data.value, code)


def preProcessor(code: str) -> str:
    """
    Execute preprocessor line
    :param code: the code before tokenization
    :return:
    """
    pre_processor_matchs = findall(r"^\s*##([a-z]+) +([a-zA-Z]+)(?: +)?(.*?)?$", code, flags=MULTILINE)

    if pre_processor_matchs:
        pre_processor_data: list[PreProcessorData] = list()

        for match in pre_processor_matchs:
            if match[0] in PreProcessorInstructions:
                pre_processor_data.append(PreProcessorData(*match))

        # remove all pre-processor instructions in the code
        code = sub(r"^\s*##.*$", "", code, flags=MULTILINE)

        # apply pre-processor instructions
        code = applyPreProcessor(code, pre_processor_data)

        code = removeCommentPreProcessor(code)

    return code

def applyPreProcessor(code: str, pre_processor_data: list[PreProcessorData]) -> str:
    """
    Apply preprocessor data to code
    :param line: the current line before tokenization
    :param pre_processor_data:
    :return:
    """
    for pre_processor in pre_processor_data:
        match pre_processor.instruction:
            case "define":
                code = define(code, pre_processor)

    return code

def removeCommentPreProcessor(code: str) -> str:
    """
    Remove all comment in the code
    :param code:
    :return:
    """
    # add \ before or in :: like \:: or :\: disable comment. Usable in string to add :: characters sequence.
    return sub(r"(?<!\\):(?<!\\)?:.*", "", code, flags=MULTILINE)
