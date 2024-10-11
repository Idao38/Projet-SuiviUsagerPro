import unittest
import sys
import os

# Ajoutez le répertoire racine du projet au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importez tous les modules de test
from tests.test_database import TestDatabaseManager
from tests.test_models import TestUser, TestWorkshop
from tests.test_ui import TestUI
from tests.test_utils import TestDateUtils
from tests.test_integration import TestUserWorkshopIntegration
from tests.test_performance import TestPerformance

def run_tests():
    # Créez une suite de tests
    test_suite = unittest.TestSuite()

    # Ajoutez toutes les classes de test à la suite
    test_loader = unittest.TestLoader()
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestDatabaseManager))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestUser))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestWorkshop))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestUI))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestDateUtils))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestUserWorkshopIntegration))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestPerformance))

    # Créez un runner de test
    runner = unittest.TextTestRunner(verbosity=2)

    # Exécutez les tests
    result = runner.run(test_suite)

    # Retournez le résultat des tests
    return result

if __name__ == '__main__':
    result = run_tests()
    
    # Sortez avec un code d'erreur si des tests ont échoué
    sys.exit(not result.wasSuccessful())