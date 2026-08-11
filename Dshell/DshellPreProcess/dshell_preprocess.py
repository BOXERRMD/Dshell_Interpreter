from ..full_import import sub, MULTILINE, StrEnum, search, compile, DOTALL

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

pre_processor_pattern = compile(r"^\s*##([a-z]+) +([a-zA-Z]+)(?: +(.*))?$", flags=MULTILINE|DOTALL)
def preProcessor(code: list[str]) -> list[str]:
    """
    Execute preprocessor line
    :param code: a list of code line before tokenization
    :return: a new list of string after pre-processor and since pre-processor instructions
    """
    pre_processor_data: list[PreProcessorData] = list()
    new_code: list[str] = []

    for line in code:

        line = removeCommentPreProcessor(line)

        if pre_processor_match := search(pre_processor_pattern, line):

            if pre_processor_match.group(1) in PreProcessorInstructions:
                pre_processor_data.append(PreProcessorData(*pre_processor_match.groups()))

        else:
            # apply pre-processor instructions
            line = applyPreProcessor(line, pre_processor_data)
            new_code.append(line)

    return new_code



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
