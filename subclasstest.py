class A:

    @classmethod
    def a(cls):
        return list(cls.__subclasses__())
    # end
class AA(A):
    pass

print(list(A.__subclasses__()))

print(A.a())