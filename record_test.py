
import db_test
import models
import record


class ReturnRecordTest(db_test.DbTest):

    def _sample_function(self):
        return 'foobar'

    def test_return_empty_list(self):
        with record.record():
            def foo():
                return []
            foo()

        returns = record.get_all_returns()
        self.assertEqual(1, len(returns.all()))
        self.assertEqual(
            '{}.list'.format(record.BUILTINS_NAME), returns[0].type_name)

    def test_return_obj_instance(self):
        with record.record():
            class Foobar(object):
                pass

            def foo():
                return Foobar()
            foo()

        returns = record.get_all_returns()
        self.assertEqual(2, len(returns.all()))
        self.assertEqual(None, returns[0].type_name)
        self.assertEqual('record_test.Foobar', returns[1].type_name)

    def test_return_obj_class(self):
        with record.record():
            class Foobar(object):
                pass

            def foo():
                return Foobar
            foo()

        returns = record.get_all_returns()
        self.assertEqual(2, len(returns.all()))
        self.assertEqual(None, returns[0].type_name)
        self.assertEqual(
            '{}.type'.format(record.BUILTINS_NAME), returns[1].type_name)

    # TODO(nathan): Do better with this
    def test_return_typed_list(self):
        with record.record():
            def foo():
                return ['a']
            foo()

        returns = record.get_all_returns()
        self.assertEqual(1, len(returns.all()))
        self.assertEqual(
            '{}.list'.format(record.BUILTINS_NAME), returns[0].type_name)
        self.assertEqual(
            'foo', returns[0].function.name)

    def test_sample_function_has_proper_function(self):
        with record.record():
            self._sample_function()

        returns = record.get_all_returns()
        self.assertEqual(1, len(returns.all()))
        self.assertEqual(
            '{}.str'.format(record.BUILTINS_NAME), returns[0].type_name)
        self.assertEqual(
            '_sample_function', 
            returns[0].function.name)


class ArgsRecordTest(db_test.DbTest):

    def _sample_function(self, a):
        return a

    def test_empty_args(self):
        with record.record():
            def foo():
                pass
            foo()

        args = record.get_all_args()
        self.assertEqual(0, len(args.all()))

    def test_single_arg(self):
        with record.record():
            def foo(bar):
                pass
            foo('a')

        args = record.get_all_args()
        self.assertEqual(1, len(args.all()))
        self.assertEqual('foo', args[0].function.name)
        self.assertEqual('bar', args[0].arg_name)
        self.assertEqual(
            '{}.str'.format(record.BUILTINS_NAME), args[0].type_name)

    def test_multiple_args(self):
        with record.record():
            def foo(bar, baz):
                pass
            foo('a', 2)

        args = record.get_all_args()
        self.assertEqual(2, len(args.all()))
        self.assertEqual('foo', args[0].function.name)
        self.assertEqual('bar', args[0].arg_name)
        self.assertEqual(
            '{}.str'.format(record.BUILTINS_NAME), args[0].type_name)
        self.assertEqual('foo', args[1].function.name)
        self.assertEqual('baz', args[1].arg_name)
        self.assertEqual(
            '{}.int'.format(record.BUILTINS_NAME), args[1].type_name)

    def test_sample_function_has_proper_function(self):
        with record.record():
            self._sample_function('foobar')

        args = record.get_all_args().all()
        self.assertEqual(2, len(args))
        expected_types = {
            '{}.str'.format(record.BUILTINS_NAME),
            'record_test.ArgsRecordTest'}
        self.assertEqual(
            expected_types, {arg.type_name for arg in args})
        for arg in args:
            self.assertEqual(
                '_sample_function', 
                arg.function.name)