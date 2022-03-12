import ast
import inspect
from typing import TYPE_CHECKING, Callable


class TypeCheckingRemoveVisitor(ast.NodeTransformer):
    def visit_If(self, node: ast.If):
        if isinstance(node.test, ast.Name):
            if node.test.id == "TYPE_CHECKING":
                return None

    def visit_Call(self, node: ast.Call):
        if node.func.__dict__["id"] == "cast":
            return node.args[1]
        return node


def remove_type_checking(func: Callable):
    if TYPE_CHECKING:
        return func

    ast_tree: ast.AST = ast.parse(inspect.getsource(func))
    modified = TypeCheckingRemoveVisitor().visit(ast_tree)
    upper = inspect.stack()[1]
    exec(compile(ast.unparse(modified), func.__module__, "exec"), upper.frame.f_globals, upper.frame.f_locals)
    modified_func = upper.frame.f_locals[func.__name__]
    return modified_func
