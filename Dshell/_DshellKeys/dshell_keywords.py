from .._DshellParser.ast_nodes import (
ASTNode,
IfNode,
ElifNode,
ElseNode,
LoopNode,
EndNode,
VarNode,
SleepNode,
ParamNode,
CodeNode,
EvalNode,
ReturnNode,
EmbedNode,
FieldEmbedNode,
PermissionNode,
UiButtonNode,
UiSelectNode,
OptionUiSelectNode
)




dshell_keyword: dict[str, ASTNode] = {
    'if': IfNode,
    'else': ElseNode,
    'elif': ElifNode,
    'loop': LoopNode,
    'var': VarNode,
    'sleep': SleepNode,
    'param': ParamNode,
    'code': CodeNode,
    'eval': EvalNode,
    'return': ReturnNode,
    '#end': EndNode,
    '#code': CodeNode,
    '#param': ParamNode,
    '#if': IfNode,
    '#loop': LoopNode,
}

dshell_discord_keyword: dict[str, ASTNode] = {
    'embed': EmbedNode,
    'field': FieldEmbedNode,
    'perm': PermissionNode,
    'permission': PermissionNode,
    'ui': UiButtonNode,
    'button': UiButtonNode,
    'select': UiSelectNode,
    'option': OptionUiSelectNode,
    '#select': UiSelectNode,
    '#button': UiButtonNode,
    '#ui': UiButtonNode,
    '#perm': PermissionNode,
    '#permission': PermissionNode,
    '#embed': EmbedNode,
}