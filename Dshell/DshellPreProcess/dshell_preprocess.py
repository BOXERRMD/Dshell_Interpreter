from ..full_import import search, sub, Optional

class PreProcessorData:
    def __init__(self, instruction: str, symbol: str, value: str):
        self.instruction = instruction
        self.symbol = symbol
        self.value = value

def define(code, pre_processor_data: PreProcessorData) -> str:
    """
    Replace all symbol with the current value
    :param symbol:
    :param value:
    :return:
    """
    return sub(f"\b{pre_processor_data.symbol}\b", pre_processor_data.value, code)

def preProcessor(code: str) -> Optional[PreProcessorData]:
    """
    Execute preprocessor code
    :param code:
    :return:
    """
    pre_process_match = search(r"^\s*##([a-zA-Z]+)\s+([a-zA-Z]+)\s+(.*)$", code)
    if pre_process_match:
        return PreProcessorData(pre_process_match.group(1).lower(), pre_process_match.group(2), pre_process_match.group(3))
    return None

def applyPreProcessor(code: str, pre_processor_data: PreProcessorData):
    """
    Apply preprocessor data to code
    :param code:
    :param pre_processor_data:
    :return:
    """
    match pre_processor_data.instruction:
        case "define":
            return define(code, pre_processor_data)