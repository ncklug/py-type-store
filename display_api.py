
import ast

import ast_type_annotator


class _TypeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.type_list = []

    def visit_Name(self, node):
        ast_type_annotator.check_file_name(node)
        self.type_list.append((
            getattr(node, ast_type_annotator.FILENAME_ANNOTATION),
            node.id,
            getattr(node, ast_type_annotator.TYPE_ANNOTATION),
        ))

    def visit_arg(self, node):
        ast_type_annotator.check_file_name(node)
        self.type_list.append((
            getattr(node, ast_type_annotator.FILENAME_ANNOTATION),
            node.arg,
            getattr(node, ast_type_annotator.TYPE_ANNOTATION),
        ))


def get_types(type_annotated_ast):
    visitor = _TypeVisitor()
    visitor.visit(type_annotated_ast)
    return visitor.type_list

