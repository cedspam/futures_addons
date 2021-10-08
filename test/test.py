import futures_addons
def test_validation():
    r,w,liste=futures_addons.test()
    assert [l.ident for l in liste[:-1]]==[0, 1]
