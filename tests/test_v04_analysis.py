import math
import unittest
from bal.fitting import availability, fit_alpha_beta
from bal.sensitivity import sobol_indices

class TestBALv04Analysis(unittest.TestCase):
    def test_availability(self):
        expected=math.log1p(2.0*.5*(1-.2))/math.log1p(1.5*.4)
        self.assertAlmostEqual(availability(.5,.2,.4,2.0,1.5),expected)
    def test_fit_synthetic_parameters(self):
        rows=[]
        for a,m,b in [(.2,.1,.3),(.4,.2,.5),(.6,.15,.8),(.8,.3,.4),(.3,.05,1.0),(.9,.25,.7),(.5,.4,.2),(.7,.1,1.2)]:
            rows.append({"a":a,"m":m,"b":b,"y":availability(a,m,b,2.4,1.3)})
        result=fit_alpha_beta(rows)
        self.assertAlmostEqual(result["alpha"],2.4,places=4)
        self.assertAlmostEqual(result["beta"],1.3,places=4)
        self.assertLess(result["rmse"],1e-7)
    def test_sobol_reproducible(self):
        ranges={"a":(.1,.9),"m":(0,.5),"b":(.2,1.5),"alpha":(.5,3),"beta":(.5,2)}
        one=sobol_indices(ranges,512,42); two=sobol_indices(ranges,512,42)
        self.assertEqual(one,two)
        self.assertEqual(set(one["indices"]),set(ranges))
        self.assertTrue(all(math.isfinite(v["ST"]) for v in one["indices"].values()))
    def test_domain_validation(self):
        with self.assertRaises(ValueError): availability(1.2,.2,.4,2,1)

if __name__=="__main__": unittest.main()
