import argparse
import xlrd
import math
from abc import ABC, abstractmethod, abstractproperty
import codecs
from enum import Enum

# ------------------------------------------------------------------------

global LANGUAGE

LANGUAGE = 'test'

DATA_SHEET_START_INDEX = 3
TEST_NO = 'test_no'
CASE_SHEET = 'case_正常系'
EXCEPTION_SHEET = 'case_異常系'
GLOBAL_SHEET = 'header'

DATA_NAME = 'data_sheet'

CASE = 'CASE'
CASE_NAME = 'CASE名'
HEADER_NAME = 'HEADER'
HEADER_TITLES = ['COMMENT', 'DATA_ID(001,002...)', 'BT_YMD( len(BY_YMD) == len(DATA_ID) )']

INPUT_NAME = 'INPUT'
INPUT_TITLES = ['DF名', 'TO', 'FROM']

FUNCTION_NAME = 'FUNCTION'
FUNCTION_TITLES = ['FUNCTIONS']

OUTPUT_NAME = 'OUTPUT'
OUTPUT_TITLES = ['DF名', 'FROM', 'CONDITION']

EXPECTED_NAME = 'EXPECTED'
EXPECTED_TITLES = ['DF名', 'FROM']

ASSERT_NAME = 'ASSERT'
ASSERT_TITLES = ['ASSERT方法', 'LEFT', 'RIGHT']

GLOBAL_NAME = 'GLOBAL'

TITLE_NAME = 'TITLE'
TEST = '処理名'
AUTHOR = '作成者'
DATE = '作成日'
CASE_TABLE = 'ケース表'

IMPORT_NAME = 'IMPORT'
MODULES = ['MODULES']

CONF_NAME = 'conftest.py'

PARAM_NAME = 'パラメータ'

PARAM_TITLES = ['パラメータ']

NUMBER = ['int64', 'float64']

FILE_PREFIX = 'gs://'
TABLE_PREFIX = ['dev-ai-pdca-prj', 'prod-ai-prj-01']

class Analyer:
    def __init__(self, path, env):
        self.excel = xlrd.open_workbook(path)
        self.env = env

    def get_data_name(self):
        return self.excel.sheet_names()

    def get_datas(self):
        for data in self.excel.sheets()[DATA_SHEET_START_INDEX:]:
            dataset = Row(['data_sheet', '\001', data.name, '\002'])
            yield dataset
            for r in range(0, data.nrows):
                yield Row(data.row_values(r))

    def get_head(self):
        sheet = self.excel.sheet_by_name(GLOBAL_SHEET)
        yield Row([GLOBAL_NAME, '\001'])
        for r in range(0, sheet.nrows):
            yield Row(sheet.row_values(r))
        yield Row(['', '', ''])

    def get_case(self):
        sheet = self.excel.sheet_by_name(CASE_SHEET)
        for r in range(0, sheet.nrows):
            yield Row(sheet.row_values(r))
        yield Row(['', '', ''])
        sheet = self.excel.sheet_by_name(EXCEPTION_SHEET)
        for r in range(0, sheet.nrows):
            yield Row(sheet.row_values(r))
        yield Row(['', '', ''])


class Row:
    def __init__(self, row):
        self.row = row
        self.trim_data = [c for c in self.row if c.strip() != '']

    def __len__(self):
        return len(self.row)

    def __getitem__(self, item):
        return self.row[item].strip() if isinstance(item, int) else self.row[item]

    def __str__(self):
        return str(self.row)

    def trim_size(self):
        return len(self.trim_data)

    def is_blank(self):
        return len(self.trim_data) == 0

    def is_case(self):
        return self.row[2].strip() == CASE

    def is_head(self):
        return self.row[2].strip() == HEADER_NAME

    def is_data(self):
        return self.row[0] == DATA_NAME and self.row[1] == '\001' and self.row[3] == '\002'

    def is_global(self):
        return self.row[0] == GLOBAL_NAME and self.row[1] == '\001'

    def has_prefix(self, num):
        return self.row[0: num] == [''] * num


# ---------------------------------------------------
#               Segment
# ---------------------------------------------------

class Segment(ABC):
    def __init__(self, name, env):
        self.name = name
        self.env = env

    @abstractmethod
    def segment_verificator(self):
        pass


class CaseSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return CaseVerificator(self)


class HeaderSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return HeaderVerificator(self)


class InputSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return InputVerificator(self)


class FunctionSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return FunctionVerificator(self)


class OutputSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return OutputVerificator(self)


class ExpectedSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return ExpectedVerificator(self)


class AssertSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return AssertVerificator(self)


class DataSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return DataVerificator(self)


class ModuleSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return ModuleVerificator(self)


class GlobalSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return GlobalVerificator(self)


class TitleSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return TitleVerificator(self)


class ImportSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return ImportVerificator(self)


class ConftestSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return ConftestVerificator(self)


class ParamsSegment(Segment):
    def __init__(self, name, env):
        Segment.__init__(self, name, env)

    def segment_verificator(self):
        return ParamsVerificator(self)


# ---------------------------------------------------
#               Verificator
# ---------------------------------------------------

class Verificator(ABC):
    def __init__(self, seg):
        self.seg = seg
        self.env = seg.env
        self.status = None

    @abstractmethod
    def hard_verify(self, data):
        pass

    @abstractmethod
    def soft_verify(self, data):
        pass

    @abstractmethod
    def flush(self):
        pass


class GlobalVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.blanks = 0
        self.status = Status(self)
        self.status.regist_blank(module_blank)
        self.status.regist(0, global_00)
        self.status.regist(1, global_01)
        self.status.regist(2, global_02)
        self.status.regist(3, global_03)

    def hard_verify(self, data):
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.segment.pop()


class TitleVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)
        self.status.regist(0, title_00)
        self.status.regist(1, title_01)
        self.status.regist(2, title_02)
        self.status.regist(3, title_03)
        self.status.regist(4, header_02)

    def hard_verify(self, data):
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_title(Title(self.env.pop(self.seg)))


class ImportVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)
        self.status.regist(0, import_00)
        self.status.regist(1, import_01_02)
        self.status.regist(2, import_01_02)
        self.status.regist(3, header_02)

    def hard_verify(self, data):
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_imports(Imports(self.env.pop(self.seg)))


class ConftestVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)
        self.status.regist_default(conf_param_default)
        self.status.regist(0, conf_param_00)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(PARAM_TITLES))] != PARAM_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_conftest(Conftest(self.env.pop(self.seg)))


class ParamsVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)
        self.status.regist_default(conf_param_default)
        self.status.regist(0, conf_param_00)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(PARAM_TITLES))] != PARAM_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_params(Params(self.env.pop(self.seg)))


class ModuleVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)
        self.blanks = 0
        self.status.regist_blank(module_blank)
        self.status.regist_case(module_case)
        self.status.regist_data(module_data)
        self.status.regist_global(module_global)

    def hard_verify(self, data):
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.pop(self.seg)
        print('构造完成')
        self.env.module.init(self.env.module, self.env.module)


class DataVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.columns_size = None
        self.dtype = None
        self.status = Status(self, 0)
        self.status.regist_data(data_data)
        self.status.regist(0, data_00)
        self.status.regist(1, data_01)
        self.status.regist_default(data_default)

    def hard_verify(self, data):
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_data(DataFunction(self.env.pop(self.seg), self.seg.name))


class CaseVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.blanks = 0
        self.status = Status(self)
        self.status.regist_blank(module_blank)
        self.status.regist(0, case_00, 0.5)
        self.status.regist(0.5, case_005, 0.5)
        self.status.regist(1, case_01)
        self.status.regist(2, case_02)
        self.status.regist(3, case_03)
        self.status.regist(4, case_04)
        self.status.regist(5, case_05)
        self.status.regist(6, case_06)

    def hard_verify(self, data):
        if self.blanks > 1:
            raise RuntimeError('CASE: ' + self.seg.name + '中有多余的空格')
        self.soft_verify(data)

    def soft_verify(self, data):
        if self.status.no != 7:
            self.status.trigge(data)
        elif data.is_blank():
            self.flush()
        else:
            raise RuntimeError(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.segment.pop()


class HeaderVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)
        self.status.regist(0, header_00)
        self.status.regist(1, header_01)
        self.status.regist(2, header_02)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(HEADER_TITLES))] != HEADER_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_header(Header(self.env.pop(self.seg)[0]))


class InputVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)

        self.status.regist_default(input_default)
        self.status.regist(0, input_00)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(INPUT_TITLES))] != INPUT_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_input(Inputs(self.env.pop(self.seg)))


class FunctionVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)
        self.status.regist(0, function_00)
        self.status.regist(1, function_01)
        self.status.regist(2, function_02)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(FUNCTION_TITLES))] != FUNCTION_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_function(Function(self.env.pop(self.seg)[0]))


class OutputVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)

        self.status.regist_default(output_default)
        self.status.regist(0, output_00)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(OUTPUT_TITLES))] != OUTPUT_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_output(Output(self.env.pop(self.seg)))


class ExpectedVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)

        self.status.regist_default(expected_default)
        self.status.regist(0, expected_00)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(EXPECTED_TITLES))] != EXPECTED_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_expected(Expected(self.env.pop(self.seg)))


class AssertVerificator(Verificator):
    def __init__(self, seg):
        Verificator.__init__(self, seg)
        self.status = Status(self)

        self.status.regist_default(assert_default)
        self.status.regist(0, assert_00)

    def hard_verify(self, data):
        if self.status.no == 0 and data[2:(2 + len(ASSERT_TITLES))] != ASSERT_TITLES:
            raise RuntimeError(data)
        self.soft_verify(data)

    def soft_verify(self, data):
        self.status.trigge(data)

    def flush(self):
        self.env.verficators.pop()
        self.env.module.add_assert(Assert(self.env.pop(self.seg)))


# ---------------------------------------------------
#               event
# ---------------------------------------------------

def module_blank(env, verficator, data):
    verficator.blanks += 1


def module_case(env, verificator, data):
    if verificator.blanks != 2:
        raise RuntimeError("case之间的空行不正确: " + str(verificator.blanks))
    verificator.blanks = 1
    case = CaseSegment('', env)
    env.segment.append(case)
    env.verficators.append(case.segment_verificator())


def module_data(env, verificator, data):
    dataset = DataSegment(data[2], env)
    env.verficators.append(dataset.segment_verificator())
    env.segment.append(dataset)


def module_global(env, verificator, data):
    gs = GlobalSegment('', env)
    env.verficators.append(gs.segment_verificator())
    env.segment.append(gs)


def data_data(env, verificator, data):
    verificator.flush()
    data = DataSegment(data[2], env)
    env.verficators.append(data.segment_verificator())
    env.segment.append(data)


def data_00(env, verificator, data):
    if data.is_blank() or data[0] == '' or data.trim_data[-1] != TEST_NO:
        raise RuntimeError(data)
    verificator.columns_size = data.trim_size() - 1
    env.segment.append(data)


def data_01(env, verificator, data):
    verificator.dtype = data
    env.segment.append(data)


def data_default(env, verificator, data):
    if verificator.columns_size != data.trim_size() - 1:
        raise RuntimeError(data)
    env.segment.append(data)


def case_00(env, verificator, data):
    if data[2] != CASE_NAME:
        raise RuntimeError(data)


def case_005(env, verificator, data):
    if data.trim_size() == 1 and data[2] != '':
        verificator.seg.name = data[2].strip()
        env.module.add_case(Case(verificator.seg.name))
    else:
        raise RuntimeError(data)


def init_segment(env, verificator, name, segment, data):
    if data[2] == name:
        env.segment.append(segment)
        env.verficators.append(segment.segment_verificator())
        verificator.blanks = 1
    else:
        raise RuntimeError(data)


def case_01(env, verificator, data):
    header = HeaderSegment('', env)
    init_segment(env, verificator, HEADER_NAME, header, data)


def case_02(env, verificator, data):
    inputs = InputSegment('', env)
    init_segment(env, verificator, INPUT_NAME, inputs, data)


def case_03(env, verificator, data):
    func = FunctionSegment("", env)
    init_segment(env, verificator, FUNCTION_NAME, func, data)


def case_04(env, verificator, data):
    output = OutputSegment("", env)
    init_segment(env, verificator, OUTPUT_NAME, output, data)


def case_05(env, verificator, data):
    expected = ExpectedSegment("", env)
    init_segment(env, verificator, EXPECTED_NAME, expected, data)


def case_06(env, verificator, data):
    asserts = AssertSegment("", env)
    init_segment(env, verificator, ASSERT_NAME, asserts, data)


def header_00(env, verificator, data):
    if data.trim_size() != len(HEADER_TITLES):
        raise RuntimeError(data)


def header_01(env, verificator, data):
    if data.trim_size() == len(HEADER_TITLES):
        env.segment.append(data)


def header_02(env, verificator, data):
    if not data.is_blank():
        raise RuntimeError(data)
    verificator.flush()


def input_00(env, verificator, data):
    if data.trim_size() != len(INPUT_TITLES):
        raise RuntimeError(data)


def input_default(env, verificator, data):
    if data.is_blank():
        verificator.flush()
    else:
        env.segment.append(data)  # TODO check 格式


def function_00(env, verificator, data):
    if data.trim_size() != len(FUNCTION_TITLES):
        raise RuntimeError(data)


def function_01(env, verificator, data):
    if data.trim_data[0] != '':
        env.segment.append(data)


def function_02(env, verificator, data):
    if data.is_blank():
        verificator.flush()
    else:
        raise RuntimeError(data)


def output_00(env, verificator, data):
    if data.trim_size() != len(OUTPUT_TITLES):
        raise RuntimeError(data)


def output_default(env, verificator, data):
    if data.is_blank():
        verificator.flush()
    else:
        env.segment.append(data)  # TODO check 格式


def expected_00(env, verificator, data):
    if data.trim_size() != len(EXPECTED_TITLES):
        raise RuntimeError(data)


def expected_default(env, verificator, data):
    if data.is_blank():
        verificator.flush()
    else:
        env.segment.append(data)  # TODO check 格式


def assert_00(env, verificator, data):
    if data.trim_size() != len(ASSERT_TITLES):
        raise RuntimeError(data)


def assert_default(env, verificator, data):
    if data.is_blank():
        verificator.flush()
    else:
        env.segment.append(data)  # TODO check 格式


def global_00(env, verificator, data):
    title = TitleSegment('', env)
    init_segment(env, verificator, TITLE_NAME, title, data)


def global_01(env, verificator, data):
    imports = ImportSegment('', env)
    init_segment(env, verificator, IMPORT_NAME, imports, data)


def global_02(env, verificator, data):
    conf = ConftestSegment('', env)
    init_segment(env, verificator, CONF_NAME, conf, data)


def global_03(env, verificator, data):
    params = ParamsSegment('', env)
    init_segment(env, verificator, PARAM_NAME, params, data)


def title_00(env, verificator, data):
    if data.is_blank() or data[2] != TEST:
        raise RuntimeError(data)
    env.segment.append(data)


def title_01(env, verificator, data):
    if data.is_blank() or data[2] != AUTHOR:
        raise RuntimeError(data)
    env.segment.append(data)


def title_02(env, verificator, data):
    if data.is_blank() or data[2] != DATE:
        raise RuntimeError(data)
    env.segment.append(data)


def title_03(env, verificator, data):
    if data.is_blank() or data[2] != CASE_TABLE:
        raise RuntimeError(data)
    env.segment.append(data)


def import_00(env, verificator, data):
    if data.trim_size() != len(MODULES):
        raise RuntimeError(data)


def import_01_02(env, verificator, data):
    if data.is_blank():
        raise RuntimeError(data)
    else:
        env.segment.append(data)  # TODO check 格式


def conf_param_00(env, verificator, data):
    if data.trim_size() != len(PARAM_TITLES):
        raise RuntimeError(data)


def conf_param_default(env, verificator, data):
    if data.is_blank():
        verificator.flush()
    else:
        env.segment.append(data)  # TODO check 格式


# ---------------------------------------------------
#               Context
# ---------------------------------------------------

class Status:
    blank = "blank"
    case = "case"
    header = "header"
    inputs = "inputs"
    function = "function"
    output = "output"
    expected = "expected"
    asserts = "asserts"
    data = "data"
    default = "default"
    globls_stat = 'global'

    def __init__(self, verficator, prefix=2):
        self.no = 0
        self.verficator = verficator
        self.env = self.verficator.env
        self.prefix = prefix
        self.table = {Status.blank: None, Status.case: None, Status.header: None,
                      Status.inputs: None, Status.function: None, Status.output: None,
                      Status.expected: None, Status.asserts: None, Status.data: None, Status.default: None,
                      Status.globls_stat: None}

    def trigge(self, data):
        if self.table[Status.data] is not None and data.is_data():
            self.table[Status.data](self.env, self.verficator, data)
        elif self.table[Status.blank] is not None and data.is_blank():
            self.table[Status.blank](self.env, self.verficator, data)
        elif self.table[Status.case] is not None and data.has_prefix(self.prefix) and data.is_case():
            self.table[Status.case](self.env, self.verficator, data)
        elif self.table[Status.header] is not None and data.has_prefix(self.prefix) and data.is_head():
            self.table[Status.header](self.env, self.verficator, data)
        elif self.table[Status.globls_stat] is not None and data.is_global():
            self.table[Status.globls_stat](self.env, self.verficator, data)
        elif self.no in self.table:
            trigger, step = self.table[self.no]
            if not data.has_prefix(self.prefix):
                raise RuntimeError(data)
            trigger(self.env, self.verficator, data)
            self.no += step
        elif self.table[Status.default] is not None and data.has_prefix(self.prefix):
            self.table[Status.default](self.env, self.verficator, data)
        else:
            raise RuntimeError(data)

    def regist(self, signal, trigger, step=1):
        self.table[signal] = [trigger, step]

    def regist_blank(self, trigger):
        self.table[Status.blank] = trigger

    def regist_case(self, trigger):
        self.table[Status.case] = trigger

    def regist_header(self, trigger):
        self.table[Status.header] = trigger

    def regist_inputs(self, trigger):
        self.table[Status.inputs] = trigger

    def regist_function(self, trigger):
        self.table[Status.function] = trigger

    def regist_output(self, trigger):
        self.table[Status.output] = trigger

    def regist_expected(self, trigger):
        self.table[Status.expected] = trigger

    def regist_asserts(self, trigger):
        self.table[Status.asserts] = trigger

    def regist_data(self, trigger):
        self.table[Status.data] = trigger

    def regist_default(self, trigger):
        self.table[Status.default] = trigger

    def regist_global(self, trigger):
        self.table[Status.globls_stat] = trigger


class ContextEnv:
    def __init__(self):
        self.segment = []
        self.verficators = []
        self.module = Module()
        module = ModuleSegment('test', self)
        self.segment.append(module)
        self.verficators.append(module.segment_verificator())

    def add(self, obj):
        if global_verify:
            flag = self.verficators[-1].hard_verify(obj)
        else:
            flag = self.verficators[-1].soft_verify(obj)

    def pop(self, seg):
        array = []
        while self.segment[-1] is not seg:
            array.append(self.segment.pop())
        self.segment.pop()
        return array[::-1]


class Generator:
    def __init__(self, input):
        self.env = ContextEnv()
        self.analyer = Analyer(input, self.env)

    def generate(self):
        self.__gen_data()
        self.__flush()
        self.__gen_case()
        self.__flush()
        self.__gen_global()
        self.__flush()
        self.__flush()
        return self.env.module

    def __gen_data(self):
        for r in self.analyer.get_datas():
            self.env.add(r)

    def __gen_case(self):
        for r in self.analyer.get_case():
            self.env.add(r)

    def __gen_global(self):
        for r in self.analyer.get_head():
            self.env.add(r)

    def __flush(self):
        self.env.verficators[-1].flush()


# ---------------------------------------------------
#               Node
# ---------------------------------------------------

class Node(ABC):
    @abstractmethod
    def execute(self, action):
        pass

    @abstractmethod
    def init(self, pre_node, module_node):
        pass

class Module(Node):
    def __init__(self):
        self.name = ''
        self.data_func = []
        self.case = []
        self.global_info = GlobalInfo()

    def execute(self, action):
        self.global_info.execute(action)

        for c in self.case:
            c.execute(action)

        for data in self.data_func:
            data.execute(action)

    def init(self, pre_node, module_node):
        self.global_info.init(self, module_node)

        for data in self.data_func:
            data.init(self, module_node)

        for case in self.case:
            case.init(self, module_node)

    def add_data(self, data_func):
        self.data_func.append(data_func)

    def add_case(self, case):
        self.case.append(case)

    def add_header(self, header):
        self.case[-1].header = header

    def add_input(self, inputs):
        self.case[-1].input = inputs

    def add_function(self, func):
        self.case[-1].function = func

    def add_output(self, output):
        self.case[-1].output = output

    def add_expected(self, expected):
        self.case[-1].expected = expected

    def add_assert(self, asserts):
        self.case[-1].asserts = asserts

    def add_title(self, title):
        self.global_info.title = title

    def add_imports(self, imports):
        self.global_info.imports = imports

    def add_conftest(self, conftest):
        self.global_info.conftest = conftest

    def add_params(self, params):
        self.global_info.params = params


class Case(Node):
    def __init__(self, name):
        self.name = name
        self.header = None
        self.input = None
        self.output = None
        self.expected = None
        self.function = None
        self.asserts = None
        

    def execute(self, action):
        self.header.execute(action)
        self.input.execute(action)
        self.function.execute(action)
        self.output.execute(action)
        self.expected.execute(action)
        self.asserts.execute(action)

    def init(self, pre_node, module_node):
        self.header.init(self, module_node)
        self.input.init(self, module_node)
        self.function.init(self, module_node)
        self.output.init(self, module_node)
        self.expected.init(self, module_node)
        self.asserts.init(self, module_node)


class Header(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.header(self)

    def init(self, pre_node, module_node):
        self.comment = self.data[2].split('\n')
        self.data_id = self.data[3].strip()
        self.bt_ymd = self.data[4].strip()
        self.case_name = pre_node.name

        if self.data_id not in pre_node.name:
            err = f"data_id: {self.data_id}, 与CASE名: {pre_node.name}中的id号不一致."
            raise RuntimeError(err)


class Inputs(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.inputs(self)

    def init(self, pre_node, module_node):
        self.inputs = []
        data_names = [c for c in [data.name for data in module_node.data_func]]
        for item in self.data:
            if item[4] in data_names and item[3].startswith(FILE_PREFIX):
                self.inputs.append(InputData(name=item[2], src=item[4], file=item[3], dtype=Dtype.file))
            elif item[4] in data_names and item[3].split('.')[0] in TABLE_PREFIX:
                table_info = item[3].split('.')
                if len(table_info) != 3:
                    raise RuntimeError(item[3])
                self.inputs.append(InputData(name=item[2], src=item[4], dataset=table_info[1], table=table_info[2],
                                             dtype=Dtype.table))
            elif item[4] in data_names and item[3] == "" and item[2] != "":
                self.inputs.append(InputData(name=item[2], src=item[4], dtype=Dtype.dataframe))
            elif item[4] not in data_names and item[3] == "" and item[2] != "":
                self.inputs.append(InputData(name=item[2], src=item[4], dtype=Dtype.variable))
            else:
                raise RuntimeError(item)


class Function(Node):
    def __init__(self, data):
        self.data = data
        self.returns = []

    def execute(self, action):
        action.function(self)

    def init(self, pre_node, module_node):
        self.error = False if len(pre_node.asserts.data) == 0 else True
        self.function = self.data[2]


class Output(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.outputs(self)

    def init(self, pre_node, module_node):
        self.outputs = []
        data_names = [c for c in [data.name for data in module_node.data_func]]

        for item in self.data:
            if item[2] != '' and item[3].startswith(FILE_PREFIX):
                if item[4] == "":
                    raise RuntimeError("出力数据为文件时,必须指定在param参数文件中的字典常量: "+item[2])
                self.outputs.append(OutputData(item[2], Dtype.file, file=item[3], cond=item[4]))
            elif item[2] != '' and item[3].split('.')[0] in TABLE_PREFIX:
                table_info = item[3].split('.')
                if len(table_info) != 3:
                    raise RuntimeError("biquery表格式不正确: "+item[3])
                cond = None if item[4] == '' else item[4]
                self.outputs.append(OutputData(item[2], Dtype.table, dataset=table_info[1], table=table_info[2], cond=cond))
            elif item[2] != '' and item[3] == pre_node.function.function:
                pre_node.function.returns.append(item[2])
            else:
                raise RuntimeError(item)

class Expected(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.expecteds(self)

    def init(self, pre_node, module_node):
        self.expecteds = []
        data_names = [c for c in [data.name for data in module_node.data_func]]
        for item in self.data:
            if item[3] not in data_names:
                raise RuntimeError("数据sheet页: "+item[3]+", 不存在")
            self.expecteds.append((item[2], item[3]))

class Assert(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.asserts(self)

    def init(self, pre_node, module_node):
        self.asserts = []
        for item in self.data:
            self.asserts.append((item[2], item[3], item[4]))


class DataFunction(Node):
    def __init__(self, array, name):
        self.name = name
        self.array = array

    def execute(self, action):
        action.datas(self)

    def init(self, pre_node, module_node):
        self.function_name = 'def get_data_from_'+self.name+'():'
        self.columns = self.array[0][0:-1]
        self.dtype = self.array[1]
        self.values = self.array[2:]


class GlobalInfo(Node):
    def __init__(self):
        self.title = None
        self.imports = None
        self.conftest = None
        self.params = None

    def execute(self, action):
        self.title.execute(action)
        self.imports.execute(action)
        self.conftest.execute(action)
        self.params.execute(action)

    def init(self, pre_node, module_node):
        self.title.init(self, module_node)
        self.imports.init(self, module_node)
        self.conftest.init(self, module_node)
        self.params.init(self, module_node)

class Title(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.title(self)

    def init(self, pre_node, module_node):
        self.test = self.data[0][3]
        self.author = self.data[1][3]
        self.date = self.data[2][3]
        self.case_table = self.data[3][3]


class Imports(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.import_module(self)

    def init(self, pre_node, module_node):
        self.py = self.data[0][2]
        self.pr = self.data[1][2]


class Conftest(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.depend(self)

    def init(self, pre_node, module_node):
        self.depend = [d[2] for d in self.data]


class Params(Node):
    def __init__(self, data):
        self.data = data

    def execute(self, action):
        action.params(self)

    def init(self, pre_node, module_node):
        self.param_list = [d[2] for d in self.data]


# ---------------------------------------------------
#               Action
# ---------------------------------------------------

class Action(ABC):

    def __init__(self, spaces=4):
        self.indent = 0
        self.spaces = spaces

    def space(self, n):
        return ' '*n*self.spaces

    @abstractmethod
    def title(self, node):
        pass

    @abstractmethod
    def import_module(self, node):
        pass

    @abstractmethod
    def depend(self, node):
        pass

    @abstractmethod
    def params(self, node):
        pass

    @abstractmethod
    def case(self, node):
        pass

    @abstractmethod
    def header(self, node):
        pass

    @abstractmethod
    def inputs(self, node):
        pass

    @abstractmethod
    def function(self, node):
        pass

    @abstractmethod
    def outputs(self, node):
        pass

    @abstractmethod
    def expecteds(self, node):
        pass

    @abstractmethod
    def asserts(self, node):
        pass

    @abstractmethod
    def datas(self, node):
        pass

class PytestAction(Action):

    def __init__(self):
        Action.__init__(self)
        #self.buffer = codecs.open("", 'r', 'utf-8')

    def title(self, node):
        code = raw(f"""
        '''coding:utf-8'''
        # ---------------------------------------------------------------------------
        # 処理名 ： {node.test}
        # 作成者 ： {node.author}
        # 作成日 ： {node.date}
        # ケース表： {node.case_table}
        # ---------------------------------------------------------------------------
        
        """)
        print(code)

    def import_module(self, node):
        code = raw(f"""
        # =========================== START-HEADER-BLOCKS ===========================
        from util import file_util
        from util import date_util
        from util import processing_util
        import {node.py}
        import {node.pr}
        import os
        from logging import getLogger
        from google.cloud import bigquery as bq
        import pandas as pd
        import numpy as np
        import datetime as dt
        import json
        from pandas.testing import assert_frame_equal
        import pytest
        """)
        print(code)

    def depend(self, node):
        array = '\n'.join(node.depend)

        code = raw(f"""
        def read_json_list(data_set, table):
        {{s1}}schema_file_path = "/ryu1/common/rls/param/" + data_set + "_" + table + ".json"
        {{s1}}if not os.path.exists(schema_file_path):
        {{s2}}raise "jsonファイル存在していない"
        {{s1}}with open(schema_file_path, "r", encoding="utf-8") as f:
        {{s2}}try:
        {{s3}}schema = json.load(f)
        {{s2}}except:
        {{s3}}raise "jsonファイルのロードミス"
        {{s1}}return schema
        
        def truncate_table(data_set, table, df):
        {{s1}}client = bq.Client("dev-ai-pdca-prj")
        {{s1}}job_config = bq.LoadJobConfig(
        {{s2}}schema=read_json_list(data_set, table),
        {{s2}}write_disposition="WRITE_TRUNCATE",
        {{s1}})
        {{s1}}load_job = client.load_table_from_dataframe(
        {{s2}}df, data_set + "." + table, job_config=job_config
        {{s1}})
        {{s1}}load_job.result()
        
        def get_data_from_sheet(case_no, data_id, datasheet_name):
        {{s1}}datasheet_name = datasheet_name.replace('[case-no]', case_no)
        {{s1}}datasheet_name = datasheet_name.replace('[data-id]', data_id)
        {{s1}}func_name = 'get_data_from_' + datasheet_name
        {{s1}}func = globals()[func_name]
        {{s1}}return func()
        
        def write_to_file(
        {{s2}}case_no,
        {{s2}}data_id,
        {{s2}}df,
        {{s2}}file_path,
        {{s2}}cols=None,
        {{s2}}dtype=None,
        {{s2}}encode='utf-8'):
        {{s1}}file_path = file_path.replace('[case-no]', case_no)
        {{s1}}file_path = file_path.replace('[data-id]', data_id)
        {{s1}}file_data = {{{{'file_dir': '', 'file_name': file_path, 'outcols': cols}}}}
        
        {{s1}}if file_path[-3:] == 'csv':
        {{s2}}if dtype is not None:
        {{s3}}df = df.astype(dtype)
        {{s2}}file_util.write_csv(g_logger, df, file_data, encode)
        
        {{s1}}elif file_path[-3:] == 'pkl':
        {{s2}}if dtype is not None:
        {{s3}}file_data['dtype'] = dtype
        {{s2}}else:
        {{s3}}file_data['dtype'] = df.dtypes.to_dict()
        {{s2}}file_util.write_pickle(g_logger, df, file_data)
        
        {{s1}}elif file_path[-7:] == 'parquet':
        {{s2}}if dtype is not None:
        {{s3}}file_data['dtype'] = dtype
        {{s2}}else:
        {{s3}}file_data['dtype'] = df.dtypes.to_dict()
        {{s2}}file_util.write_parquet(g_logger, df, file_data)
        
        def load_from_file(
        {{s2}}case_no,
        {{s2}}data_id,
        {{s2}}file_path,
        {{s2}}cols=None,
        {{s2}}dtype=None,
        {{s2}}encode='utf-8'):
        {{s1}}file_path = file_path.replace('[case-no]', case_no)
        {{s1}}file_path = file_path.replace('[data-id]', data_id)
        {{s1}}file_data = {{{{'file_dir': '', 'file_name': file_path, 'usecols': cols}}}}
        
        {{s1}}df = pd.DataFrame()
        {{s1}}if file_path[-3:] == 'csv':
        {{s2}}file_data['dtype'] = dtype
        {{s2}}df = file_util.load_csv(g_logger, file_data, encode)
        
        {{s1}}elif file_path[-3:] == 'pkl':
        {{s2}}df = file_util.load_pickle(g_logger, file_data)
        {{s2}}if dtype is not None:
        {{s3}}df = df.astype(dtype)
        
        {{s1}}elif file_path[-7:] == 'parquet':
        {{s2}}df = file_util.load_parquet(g_logger, file_data)
        {{s2}}if dtype is not None:
        {{s3}}df = df.astype(dtype)
        {{s1}}return df
        
        g_logger = getLogger()
        
        # conftest.pyに依頼されたパラメータを設定する
        pytestmark = pytest.mark.usefixtures('test_util')
        {array}
        """)

        code = code.format(s1=self.space(1), s2=self.space(2), s3=self.space(3))

        print(code)

    def params(self, node):
        array = '\n'.join(node.param_list)
        code = raw(f"""
        # ほかのパラメータを設定する
        {array}
        # =========================== END-HEADER-BLOCKS ===========================
        """)
        print(code)

    def case(self, node):
        pass

    def header(self, node):
        comments = '\n'.join(["{s1}print('"+line+"')" for line in node.comment])
        code = raw(f"""
                @pytest.mark.parametrize(
                {{s1}}'test_util',
                {{s1}}[{{{{'data_id': '{node.data_id}', 'bt_ymd': str('{node.bt_ymd}'), }}}}, ],
                {{s1}}ids=['data_id:{node.data_id}', ],
                {{s1}}indirect=True)
                def {node.case_name}(test_util):
                {{s1}}case_no = '{node.data_id}'
                {{s1}}data_id = test_util[0].data_id

                {{s1}}print('=======================テスト内容=======================')
                {comments}
            """)
        code = code.format(s1=self.space(1))
        print(code)

    def inputs(self, node):
        code = None
        for data in node.inputs:
            name = data.name if data.name != "" else 'tmp'
            if data.dtype == Dtype.file:
                code = raw(f"""{{s1}}if os.path.exists('{data.file}'):
                                {{s2}}os.remove('{data.file}')
                                
                                {{s1}}{name} = get_data_from_sheet(
                                {{s2}}case_no,
                                {{s2}}data_id,
                                {{s2}}'{data.src}')
                                
                                {{s1}}write_to_file(
                                {{s2}}case_no,
                                {{s2}}data_id,
                                {{s2}}{name},
                                {{s2}}'{data.file}')
                        """)
                code = code.format(s1=self.space(1), s2=self.space(2))
            elif data.dtype == Dtype.dataframe:
                code = raw(f"""{{s1}}{name} = get_data_from_sheet(
                                {{s2}}case_no,
                                {{s2}}data_id,
                                {{s2}}'{data.src}')
                        """)
                code = code.format(s1=self.space(1), s2=self.space(2))
            elif data.dtype == Dtype.variable:
                code = raw(f"""{{s1}}{name}={data.src}""")
                code = code.format(s1=self.space(1))
            else:
                code = raw(f"""
                    {{s1}}{name} = get_data_from_sheet(
                    {{s2}}case_no,
                    {{s2}}data_id,
                    {{s2}}'{data.src}')
                    
                    {{s1}}truncate_table('{data.dataset}', '{data.table}', {name})
                """)
                code = code.format(s1=self.space(1), s2=self.space(2))
            print(code)

    def function(self, node):
        if node.error:
            code = raw(f"""
                {{s1}}df_result = {node.function}
            """)
            code = code.format(s1=self.space(1))
        else:
            code = raw(f"""
                {{s1}}with pytest.raises(Exception):
                {{s2}}{node.function}
            """)
            code = code.format(s1=self.space(1),s2=self.space(2))
        
        print(code)

    def outputs(self, node):
        for data in node.outputs:
            if data.dtype == Dtype.file:
                code = raw(f"""
                        {{s1}}{data.name} = load_from_file(
                        {{s2}}case_no,
                        {{s2}}data_id,
                        {{s2}}{data.file},
                        {{s2}}dtype={data.cond}['dtype'])
                        """)
                code = code.format(s1=self.space(1), s2=self.space(2))
            else:
                where = ' where '+data.cond if data.cond != None else '' 
                code = raw(f"""
                            {{s1}}{data.name} = bigquery_util.load_from_table(g_logger, 'select * from {data.dataset}.{data.table} {where}')
                        """)
                code = code.format(s1=self.space(1))
            print(code)

    def expecteds(self, node):
        for data in node.expecteds:
            code = raw(f"""
                        {{s1}}{data[0]} = get_data_from_sheet(
                        {{s2}}case_no,
                        {{s2}}data_id,
                        {{s2}}'{data[1]}')
                    """)
            code = code.format(s1=self.space(1), s2=self.space(2))
            print(code)
    
    def asserts(self, node):
        for item in node.asserts:
            if item[0] == 'assert_frame_equal':
                code = raw(f"""
                            {{s1}}assert_frame_equal(
                            {{s2}}{item[1]},
                            {{s2}}{item[2]},
                            {{s2}}check_dtype=False,
                            {{s2}}check_index_type=False,
                            {{s2}}check_categorical=False)
                        """)
                code = code.format(s1=self.space(1), s2=self.space(2))
                print(code)
            else:
                code = raw(f"""{{s1}}assert {item[1]} == {item[2]}""")
                code = code.format(s1=self.space(1))
                print(code)

    def datas(self, node):
        datas = []
        for idx in range(len(node.columns)):
            col = [r[idx] for r in node.values]
            tmp = transform(col, node.dtype[idx])
            datas.append(f"'{node.columns[idx]}': [{tmp}]")

        values_data = '{s2}'+(',\n{s2}'.join(datas))
        code = raw(f"""
        {node.function_name}
        {{s1}}return pd.DataFrame({{{{
        {values_data}
        {{s1}}}}}}""")
        code = code.format(s1=self.space(1), s2=self.space(2))
        print(code)

# ---------------------------------------------------
#               utils
# ---------------------------------------------------

def transform(column, column_type):
    if column_type in NUMBER:
        return ', '.join([cell if cell != '' else 'np.NaN' for cell in column])
    else:
        return ', '.join(["'"+cell+"'" if cell != '' else 'np.NaN' for cell in column])

def raw(code):
    return code.replace('  ', '')

class Dtype(Enum):
    file = 1
    table = 2
    dataframe = 3
    variable = 4
    function = 5


class InputData:
    def __init__(self, name, src, file=None, dataset=None, table=None, dtype=None):
        self.name = name
        self.src = src
        self.file = file
        self.dataset = dataset
        self.table = table
        self.dtype = dtype

class OutputData:
    def __init__(self, name, dtype, file=None, dataset=None, table=None, cond=None):
        self.name = name
        self.file = file
        self.dataset = dataset
        self.table = table
        self.cond = cond
        self.dtype = dtype

# ---------------------------------------------------
#               MAIN
# ---------------------------------------------------

if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-i')
    # parser.add_argument('-o')
    # parser.add_argument('-check', action='store_const', const=True, required=False)

    # args = parser.parse_args()

    # input_file = args.i
    # output_path = args.o

    # global global_verify
    # global_verify = args.check

    input_file = r"/Users/likai/test.xlsx"

    global global_verify
    global_verify = False

    gen = Generator(input_file)
    module = gen.generate()

    pytest = PytestAction()

    module.execute(pytest)

# --------------------------------------------------------
"""
python gen.py -i /Users/likai/test.xlsx -o /Users/likai/ -check
"""
