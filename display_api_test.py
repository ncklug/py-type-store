
import ast
import textwrap

import ast_type_annotator
import db_test
import display_api
import record


class AnnotatorTest(db_test.DbTest):

    def _record_annotate_and_output(self, code):
        ast_ = ast.parse(code)
        with record.record():
            exec(compile(ast_, filename=__file__, mode='exec'))
        ast_type_annotator.annotate_ast(ast_, __file__)
        return display_api.get_types(ast_)

    def test_str_node(self):
        actual_output = self._record_annotate_and_output("'foobar'")
        self.assertEqual([], actual_output)

    def test_call(self):
        actual_output = self._record_annotate_and_output(textwrap.dedent("""\
            def foo(a):
                a
            foo('a')
        """))
        expected_output = [
            (__file__, 'a', {'{}.str'.format(record.BUILTINS_NAME): 1}),
            (__file__, 'a', {'{}.str'.format(record.BUILTINS_NAME): 1}),
            (__file__, 'foo', {None: 1}),
        ]
        self.assertEqual(expected_output, actual_output)

