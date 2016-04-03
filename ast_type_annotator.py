
import ast

import models

FILENAME_ANNOTATION = '_file_name'
TYPE_ANNOTATION = '_types'


class Error(Exception):
    pass


class MissingAnnotationError(Error):

    def __init__(self, node, expected_annotation):
        super().__init__(
            'Expected annotation {} to be present on node {}'
            .format(expected_annotation, node))


def check_file_name(node):
    if not hasattr(node, FILENAME_ANNOTATION):
        raise MissingAnnotationError(FILENAME_ANNOTATION, node)


class _TypeAnnotator(ast.NodeTransformer):

    def __init__(self):
        self._var_types = {}
        self._funcs = {}

    def visit_Call(self, node):
        check_file_name(node)
        query = models.get_session().query(models.Return).join(models.Function)
        # TODO(nathan): Handle namespaced functions
        called_func = self._funcs[node.func.id]
        query = query.filter(models.Function.name==node.func.id)
        query = query.filter(models.Function.lineno==called_func.lineno)
        query = query.filter(models.Function.file_name==getattr(
            called_func, FILENAME_ANNOTATION))
        # TODO(nathan): Handle multi-return
        ret_dict = {}
        for ret in query:
            ret_dict.setdefault(ret.type_name, 0)
            ret_dict[ret.type_name] += 1
        setattr(node.func, TYPE_ANNOTATION, ret_dict)
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        # TODO(nathan): This is super janky and won't handle scoping.
        self._funcs = {node.name: node}
        check_file_name(node)
        query = models.get_session().query(models.Arg).join(models.Function)
        query.filter(models.Function.name==node.name)
        query.filter(models.Function.lineno==node.lineno)
        query.filter(models.Function.file_name==getattr(node, FILENAME_ANNOTATION))
        arg_dict = {}
        for arg in query:
            arg_dict.setdefault(arg.arg_name, {}).setdefault(arg.type_name, 0)
            arg_dict[arg.arg_name][arg.type_name] += 1
        # TODO(nathan): Make this use the self._var_types in a different visit
        for arg in node.args.args:
            setattr(arg, TYPE_ANNOTATION, arg_dict[arg.arg])
        old_var_types = dict(self._var_types)
        self._var_types.update(arg_dict)
        self.generic_visit(node)
        self._var_types = old_var_types
        return node

    def visit_Name(self, node):
        # Exclude the case where it's already been set, like by the visit_Call
        # method, because Name nodes are also used for function names
        if not hasattr(node, TYPE_ANNOTATION):
            setattr(node, TYPE_ANNOTATION, self._var_types[node.id])
        self.generic_visit(node)
        return node

    def visit_Str(self, node):
        setattr(node, TYPE_ANNOTATION, {str: 1})
        self.generic_visit(node)
        return node


class _FileNameAnnotator(ast.NodeTransformer):

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name

    def visit(self, node):
        setattr(node, FILENAME_ANNOTATION, self._file_name)
        return super().visit(node)


def annotate_ast(ast_, file_name):
    _FileNameAnnotator(file_name).visit(ast_)
    _TypeAnnotator().visit(ast_)
