




class AssertMethod:


    @staticmethod
    def assert_value(key, type_ex):
        assert isinstance(key, (type_ex, type(None))), \
            f"{key} должен быть ('{type_ex}') или None"

    @staticmethod
    def assert_enum_value(key, enum):
        assert key in enum, \
            f"{key} должен быть одним из: {', '.join(map(str, enum))}"

    @staticmethod
    def assert_float_in_str_value(key):
        assert isinstance(key, str), \
            f"{key} должен быть строкой"
        try:
            float(key)
        except ValueError:
            assert False, f"{key} должен быть числовым значением в строке"