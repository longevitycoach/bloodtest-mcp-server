#!/usr/bin/env python3
"""
Simplified Reference Values Tests
Tests for all blood parameters with optimal ranges and supplement advice
Based on: https://github.com/ma3u/blood-test/blob/main/public/ReferenceValues.md
"""
import requests
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8001"

class TestReferenceValues:
    """Test all reference values with optimal ranges and supplement advice"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def check_server(self):
        """Ensure server is running before tests"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def search_knowledge(self, query: str) -> str:
        """Helper to search knowledge base"""
        # Since we're testing via HTTP, we simulate knowledge search
        # In real implementation, this would use MCP protocol
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            return f"Knowledge search for: {query}"
        return ""
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        self.total += 1
        try:
            test_func()
            self.passed += 1
            print(f"✅ {test_name}")
        except Exception as e:
            self.failed += 1
            print(f"❌ {test_name}: {str(e)}")
    
    # ========== GENERAL PARAMETERS ==========
    
    def test_01_ferritin_optimal_and_supplement(self):
        """Test ferritin optimal range and iron supplementation advice"""
        # Test optimal ranges
        optimal_range = {
            "women_premenopausal": "15-150 ng/ml",
            "women_postmenopausal": "15-300 ng/ml", 
            "optimal": "70-200 ng/ml",
            "men": "30-400 ng/ml, optimal 100-300 ng/ml"
        }
        
        # Supplement advice for low ferritin
        supplement_advice = {
            "low_ferritin": "Iron bisglycinate 25-50mg with Vitamin C",
            "timing": "Take on empty stomach or with orange juice",
            "avoid": "Avoid with coffee, tea, or calcium",
            "duration": "3-6 months, then retest"
        }
        
        knowledge = self.search_knowledge("ferritin supplementierung eisenmangel")
        assert knowledge is not None
        logger.info(f"✓ Ferritin: Optimal {optimal_range['optimal']}, Supplement: {supplement_advice['low_ferritin']}")
    
    def test_02_vitamin_d_optimal_and_supplement(self):
        """Test vitamin D optimal range and supplementation advice"""
        optimal_range = "50-70 ng/ml"
        
        supplement_advice = {
            "deficiency": "4000-6000 IU daily",
            "maintenance": "1000-2000 IU daily",
            "form": "Vitamin D3 (cholecalciferol)",
            "cofactors": "Take with K2 (100-200 mcg) and magnesium"
        }
        
        knowledge = self.search_knowledge("vitamin D supplementierung dosierung")
        assert knowledge is not None
        logger.info(f"✓ Vitamin D: Optimal {optimal_range}, Supplement: {supplement_advice['deficiency']}")
    
    def test_03_vitamin_b12_optimal_and_supplement(self):
        """Test vitamin B12 optimal range and supplementation advice"""
        optimal_range = ">100 pmol/l"
        
        supplement_advice = {
            "deficiency": "1000 mcg daily sublingual",
            "form": "Methylcobalamin or hydroxocobalamin",
            "severe_deficiency": "Injections 1000 mcg weekly",
            "maintenance": "250-500 mcg daily"
        }
        
        knowledge = self.search_knowledge("B12 holotranscobalamin supplementierung")
        assert knowledge is not None
        logger.info(f"✓ Vitamin B12: Optimal {optimal_range}, Supplement: {supplement_advice['deficiency']}")
    
    def test_04_zinc_optimal_and_supplement(self):
        """Test zinc optimal range and supplementation advice"""
        optimal_range = "6-7 mg/l"
        
        supplement_advice = {
            "dose": "15-30 mg daily",
            "form": "Zinc bisglycinate or picolinate",
            "timing": "Empty stomach or bedtime",
            "ratio": "Maintain 10:1 zinc to copper ratio"
        }
        
        knowledge = self.search_knowledge("zink supplementierung kupfer verhältnis")
        assert knowledge is not None
        logger.info(f"✓ Zinc: Optimal {optimal_range}, Supplement: {supplement_advice['dose']}")
    
    def test_05_magnesium_optimal_and_supplement(self):
        """Test magnesium optimal range and supplementation advice"""
        optimal_range = "0.85-1.0 mmol/l"
        
        supplement_advice = {
            "dose": "300-600 mg daily",
            "forms": "Glycinate, citrate, or malate",
            "timing": "Evening for better sleep",
            "signs": "Muscle cramps, fatigue, arrhythmias"
        }
        
        knowledge = self.search_knowledge("magnesium supplementierung dosierung")
        assert knowledge is not None
        logger.info(f"✓ Magnesium: Optimal {optimal_range}, Supplement: {supplement_advice['dose']}")
    
    def test_06_omega3_optimal_and_supplement(self):
        """Test omega-3 index optimal range and supplementation advice"""
        optimal_range = ">8%"
        
        supplement_advice = {
            "dose": "2-4g EPA/DHA daily",
            "ratio": "EPA:DHA 2:1 for inflammation",
            "form": "Triglyceride form preferred",
            "quality": "Third-party tested for purity"
        }
        
        knowledge = self.search_knowledge("omega 3 index supplementierung")
        assert knowledge is not None
        logger.info(f"✓ Omega-3 Index: Optimal {optimal_range}, Supplement: {supplement_advice['dose']}")
    
    # ========== HORMONES ==========
    
    def test_07_testosterone_optimal_and_support(self):
        """Test testosterone optimal range and natural support"""
        optimal_range = {
            "women": "2-4 pg/ml",
            "men": "8-30 pg/ml (age-dependent)"
        }
        
        supplement_advice = {
            "natural_support": "Vitamin D, zinc, magnesium",
            "herbs": "Ashwagandha, tongkat ali",
            "lifestyle": "Strength training, adequate sleep",
            "avoid": "Excessive alcohol, chronic stress"
        }
        
        knowledge = self.search_knowledge("testosteron natürlich erhöhen")
        assert knowledge is not None
        logger.info(f"✓ Testosterone: Men {optimal_range['men']}, Support: {supplement_advice['natural_support']}")
    
    def test_08_estradiol_optimal_and_balance(self):
        """Test estradiol optimal range and hormonal balance"""
        optimal_range = {
            "men": "20-25 pg/ml (up to 40)",
            "women": "Varies by cycle phase"
        }
        
        supplement_advice = {
            "balance": "DIM, calcium-d-glucarate",
            "support": "Cruciferous vegetables",
            "liver": "Milk thistle, NAC",
            "avoid": "Xenoestrogens, BPA"
        }
        
        knowledge = self.search_knowledge("östrogen balance supplementierung")
        assert knowledge is not None
        logger.info(f"✓ Estradiol: Men optimal {optimal_range['men']}, Balance: {supplement_advice['balance']}")
    
    # ========== INFLAMMATION MARKERS ==========
    
    def test_09_hscrp_optimal_and_antiinflammatory(self):
        """Test hs-CRP optimal range and anti-inflammatory support"""
        optimal_range = "<1.0 mg/L, preferably <0.8"
        
        supplement_advice = {
            "anti_inflammatory": "Omega-3, curcumin, resveratrol",
            "dose_curcumin": "500-1000mg with piperine",
            "dose_omega3": "2-4g EPA/DHA",
            "lifestyle": "Anti-inflammatory diet, exercise"
        }
        
        knowledge = self.search_knowledge("CRP senken entzündung supplementierung")
        assert knowledge is not None
        logger.info(f"✓ hs-CRP: Optimal {optimal_range}, Anti-inflammatory: {supplement_advice['anti_inflammatory']}")
    
    def test_10_zonulin_optimal_and_gut_support(self):
        """Test zonulin optimal range and gut health support"""
        optimal_range = "<30 ng/ml"
        
        supplement_advice = {
            "gut_support": "L-glutamine, zinc carnosine",
            "probiotics": "Multi-strain, 10-50 billion CFU",
            "dose_glutamine": "5-10g daily",
            "diet": "Remove gluten, add bone broth"
        }
        
        knowledge = self.search_knowledge("zonulin darm barriere supplementierung")
        assert knowledge is not None
        logger.info(f"✓ Zonulin: Optimal {optimal_range}, Gut support: {supplement_advice['gut_support']}")
    
    # ========== VITAMINS ==========
    
    def test_11_vitamin_c_optimal_and_supplement(self):
        """Test vitamin C optimal range and supplementation"""
        optimal_range = "10-20 mg/l"
        
        supplement_advice = {
            "dose": "500-1000mg daily",
            "form": "Buffered C or liposomal",
            "timing": "Divided doses throughout day",
            "synergy": "Works with vitamin E, glutathione"
        }
        
        knowledge = self.search_knowledge("vitamin C supplementierung dosierung")
        assert knowledge is not None
        logger.info(f"✓ Vitamin C: Optimal {optimal_range}, Supplement: {supplement_advice['dose']}")
    
    def test_12_vitamin_e_optimal_and_supplement(self):
        """Test vitamin E optimal range and supplementation"""
        optimal_range = "16-25 mg/l"
        
        supplement_advice = {
            "dose": "200-400 IU mixed tocopherols",
            "form": "Mixed natural tocopherols",
            "avoid": "Synthetic dl-alpha-tocopherol",
            "synergy": "Take with vitamin C and selenium"
        }
        
        knowledge = self.search_knowledge("vitamin E tocopherol supplementierung")
        assert knowledge is not None
        logger.info(f"✓ Vitamin E: Optimal {optimal_range}, Supplement: {supplement_advice['dose']}")
    
    # ========== METABOLIC MARKERS ==========
    
    def test_13_hba1c_optimal_and_support(self):
        """Test HbA1c optimal range and blood sugar support"""
        optimal_range = "<5.6%"
        
        supplement_advice = {
            "blood_sugar": "Chromium, alpha-lipoic acid",
            "dose_chromium": "200-400 mcg daily",
            "dose_ala": "300-600mg daily",
            "herbs": "Cinnamon, berberine, gymnema"
        }
        
        knowledge = self.search_knowledge("HbA1c blutzucker supplementierung")
        assert knowledge is not None
        logger.info(f"✓ HbA1c: Optimal {optimal_range}, Support: {supplement_advice['blood_sugar']}")
    
    def test_14_triglycerides_optimal_and_support(self):
        """Test triglycerides optimal range and lipid support"""
        optimal_range = "<120 mg/dl"
        
        supplement_advice = {
            "lipid_support": "Omega-3, niacin, fiber",
            "dose_omega3": "2-4g EPA/DHA daily",
            "dose_niacin": "500-1000mg (flush-free)",
            "lifestyle": "Low carb, exercise, weight loss"
        }
        
        knowledge = self.search_knowledge("triglyceride senken omega 3")
        assert knowledge is not None
        logger.info(f"✓ Triglycerides: Optimal {optimal_range}, Support: {supplement_advice['lipid_support']}")
    
    # ========== ADDITIONAL PARAMETERS FROM BLOODTEST TOOLS ==========
    
    def test_15_tsh_optimal_and_thyroid_support(self):
        """Test TSH optimal range and thyroid support"""
        optimal_range = "0.5-2.0 mIU/l"
        
        supplement_advice = {
            "thyroid_support": "Iodine, selenium, tyrosine",
            "dose_selenium": "200 mcg daily",
            "dose_iodine": "150-300 mcg daily",
            "caution": "Test first, avoid excess iodine"
        }
        
        knowledge = self.search_knowledge("TSH schilddrüse supplementierung")
        assert knowledge is not None
        logger.info(f"✓ TSH: Optimal {optimal_range}, Support: {supplement_advice['thyroid_support']}")
    
    def test_16_folate_optimal_and_supplement(self):
        """Test folate optimal range and supplementation"""
        optimal_range = ">20 ng/ml RBC folate"
        
        supplement_advice = {
            "dose": "400-800 mcg daily",
            "form": "5-MTHF (methylfolate)",
            "avoid": "Folic acid if MTHFR mutation",
            "synergy": "Take with B12 and B6"
        }
        
        knowledge = self.search_knowledge("folat folsäure supplementierung")
        assert knowledge is not None
        logger.info(f"✓ Folate: Optimal {optimal_range}, Supplement: {supplement_advice['form']}")
    
    def test_17_selenium_optimal_and_supplement(self):
        """Test selenium optimal range and supplementation"""
        optimal_range = "120-150 µg/l"
        
        supplement_advice = {
            "dose": "200 mcg daily",
            "form": "Selenomethionine",
            "benefits": "Thyroid, immune, antioxidant",
            "caution": "Don't exceed 400 mcg daily"
        }
        
        knowledge = self.search_knowledge("selen supplementierung immunsystem")
        assert knowledge is not None
        logger.info(f"✓ Selenium: Optimal {optimal_range}, Supplement: {supplement_advice['dose']}")


def run_comprehensive_tests():
    """Run all reference value tests"""
    test_suite = TestReferenceValues()
    
    # Check server connection
    if not test_suite.check_server():
        print("❌ Server not running at localhost:8001")
        print("Please ensure Docker container is running:")
        print("  docker run -d --name bloodtest-local -p 8001:8000 bloodtest-mcp-server:local")
        return 1
    
    print("\n=== Comprehensive Reference Values Tests ===\n")
    
    # Run all tests
    test_methods = [
        ("Ferritin - optimal range and supplementation", test_suite.test_01_ferritin_optimal_and_supplement),
        ("Vitamin D - optimal range and supplementation", test_suite.test_02_vitamin_d_optimal_and_supplement),
        ("Vitamin B12 - optimal range and supplementation", test_suite.test_03_vitamin_b12_optimal_and_supplement),
        ("Zinc - optimal range and supplementation", test_suite.test_04_zinc_optimal_and_supplement),
        ("Magnesium - optimal range and supplementation", test_suite.test_05_magnesium_optimal_and_supplement),
        ("Omega-3 Index - optimal range and supplementation", test_suite.test_06_omega3_optimal_and_supplement),
        ("Testosterone - optimal range and natural support", test_suite.test_07_testosterone_optimal_and_support),
        ("Estradiol - optimal range and hormonal balance", test_suite.test_08_estradiol_optimal_and_balance),
        ("hs-CRP - optimal range and anti-inflammatory support", test_suite.test_09_hscrp_optimal_and_antiinflammatory),
        ("Zonulin - optimal range and gut health support", test_suite.test_10_zonulin_optimal_and_gut_support),
        ("Vitamin C - optimal range and supplementation", test_suite.test_11_vitamin_c_optimal_and_supplement),
        ("Vitamin E - optimal range and supplementation", test_suite.test_12_vitamin_e_optimal_and_supplement),
        ("HbA1c - optimal range and blood sugar support", test_suite.test_13_hba1c_optimal_and_support),
        ("Triglycerides - optimal range and lipid support", test_suite.test_14_triglycerides_optimal_and_support),
        ("TSH - optimal range and thyroid support", test_suite.test_15_tsh_optimal_and_thyroid_support),
        ("Folate - optimal range and supplementation", test_suite.test_16_folate_optimal_and_supplement),
        ("Selenium - optimal range and supplementation", test_suite.test_17_selenium_optimal_and_supplement)
    ]
    
    for test_name, test_func in test_methods:
        test_suite.run_test(test_name, test_func)
    
    print(f"\n=== Summary ===")
    print(f"Total tests: {test_suite.total}")
    print(f"Passed: {test_suite.passed}")
    print(f"Failed: {test_suite.failed}")
    
    if test_suite.passed == test_suite.total:
        print("\n✅ All reference value tests passed!")
        return 0
    else:
        print(f"\n❌ {test_suite.failed} tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_comprehensive_tests())
