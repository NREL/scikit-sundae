import pytest
from sksundae._cy_ida import _check_signature as ida_signature
from sksundae._cy_cvode import _check_signature as cvode_signature


class IDATestClass:

    def resfn_1(self, t, y, yp, res):
        pass

    def resfn_2(self, t, y, yp, res, userdata):
        pass

    @classmethod
    def resfn_3(cls, t, y, yp, res):
        pass

    @classmethod
    def resfn_4(cls, t, y, yp, res, userdata):
        pass

    @staticmethod
    def resfn_5(t, y, yp, res):
        pass

    @staticmethod
    def resfn_6(t, y, yp, res, userdata):
        pass


def resfn_7(t, y, yp, res):
    pass


def resfn_8(t, y, yp, res, userdata):
    pass


def resfn_short(t, y, yp):
    pass 


def resfn_long(t, y, yp, res, userdata1, userdata2):
    pass


def test_ida_signature_checks():

    assert ida_signature('resfn', IDATestClass().resfn_1, (4, 5)) == 0
    assert ida_signature('resfn', IDATestClass().resfn_2, (4, 5)) == 1

    assert ida_signature('resfn', IDATestClass().resfn_3, (4, 5)) == 0
    assert ida_signature('resfn', IDATestClass().resfn_4, (4, 5)) == 1

    assert ida_signature('resfn', IDATestClass().resfn_5, (4, 5)) == 0
    assert ida_signature('resfn', IDATestClass().resfn_6, (4, 5)) == 1

    assert ida_signature('resfn', resfn_7, (4, 5)) == 0
    assert ida_signature('resfn', resfn_8, (4, 5)) == 1
    
    with pytest.raises(ValueError):
        _ = ida_signature('rhsfn', resfn_short, (4, 5))
        
    with pytest.raises(ValueError):
        _ = ida_signature('rhsfn', resfn_long, (4, 5))


class CVODETestClass:

    def rhsfn_1(self, t, y, yp):
        pass

    def rhsfn_2(self, t, y, yp, userdata):
        pass

    @classmethod
    def rhsfn_3(cls, t, y, yp):
        pass

    @classmethod
    def rhsfn_4(cls, t, y, yp, userdata):
        pass

    @staticmethod
    def rhsfn_5(t, y, yp):
        pass

    @staticmethod
    def rhsfn_6(t, y, yp, userdata):
        pass


def rhsfn_7(t, y, yp):
    pass


def rhsfn_8(t, y, yp, userdata):
    pass


def rhsfn_short(t, y):
    pass 


def rhsfn_long(t, y, yp, userdata1, userdata2):
    pass


def test_cvode_signature_checks():

    assert cvode_signature('rhsfn', CVODETestClass().rhsfn_1, (3, 4)) == 0
    assert cvode_signature('rhsfn', CVODETestClass().rhsfn_2, (3, 4)) == 1

    assert cvode_signature('rhsfn', CVODETestClass().rhsfn_3, (3, 4)) == 0
    assert cvode_signature('rhsfn', CVODETestClass().rhsfn_4, (3, 4)) == 1

    assert cvode_signature('rhsfn', CVODETestClass().rhsfn_5, (3, 4)) == 0
    assert cvode_signature('rhsfn', CVODETestClass().rhsfn_6, (3, 4)) == 1

    assert cvode_signature('rhsfn', rhsfn_7, (3, 4)) == 0
    assert cvode_signature('rhsfn', rhsfn_8, (3, 4)) == 1
    
    with pytest.raises(ValueError):
        _ = cvode_signature('rhsfn', rhsfn_short, (3, 4))
        
    with pytest.raises(ValueError):
        _ = cvode_signature('rhsfn', rhsfn_long, (3, 4))
