
import ast
import textwrap

import ast_type_annotator
import db_test
import record


class AnnotatorTest(db_test.DbTest):

    def _record_and_annotate(self, code, ret_first=True):
        ast_ = ast.parse(code)
        with record.record():
            exec(compile(ast_, filename=__file__, mode='exec'))
        ast_type_annotator.annotate_ast(ast_, __file__)
        if ret_first:
            return ast_.body[0]
        else:
            return ast_

    def test_str_node(self):
        ast_ = self._record_and_annotate("'foobar'").value
        self.assertEqual({str: 1}, ast_._types)

    def test_call(self):
        try:
            ast_ = self._record_and_annotate(textwrap.dedent("""\
                def foo(a):
                    a
                foo('a')
            """), ret_first=False)
        except Exception:
            import pdb; pdb.set_trace()
        self.assertEqual({'__builtin__.str': 1}, ast_.body[0].args.args[0]._types)
        self.assertEqual({'__builtin__.str': 1}, ast_.body[0].body[0].value._types)
        self.assertEqual({None: 1}, ast_.body[1].value.func._types)


