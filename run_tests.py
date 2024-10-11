import unittest
import sys
import os
import traceback

# Ajoutez le répertoire racine du projet au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def import_test_modules():
    test_modules = {}
    try:
        from tests.test_database import TestDatabaseManager
        test_modules['TestDatabaseManager'] = TestDatabaseManager
    except ImportError as e:
        print(f"Erreur lors de l'importation de TestDatabaseManager: {e}")

    try:
        from tests.test_models import TestUser, TestWorkshop
        test_modules['TestUser'] = TestUser
        test_modules['TestWorkshop'] = TestWorkshop
    except ImportError as e:
        print(f"Erreur lors de l'importation de TestUser ou TestWorkshop: {e}")

    try:
        from tests.test_utils import TestDateUtils
        test_modules['TestDateUtils'] = TestDateUtils
    except ImportError as e:
        print(f"Erreur lors de l'importation de TestDateUtils: {e}")

    try:
        from tests.test_ui import TestUI
        test_modules['TestUI'] = TestUI
    except ImportError as e:
        print(f"Erreur lors de l'importation de TestUI: {e}")

    return test_modules

def run_tests():
    test_modules = import_test_modules()

    # Créez une suite de tests
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # Ajoutez les tests à la suite
    for test_class in test_modules.values():
        try:
            test_suite.addTest(test_loader.loadTestsFromTestCase(test_class))
        except Exception as e:
            print(f"Erreur lors de l'ajout des tests pour {test_class.__name__}: {e}")
            traceback.print_exc()

    # Créez un runner de test et exécutez la suite
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Affichez un résumé des résultats
    print("\nRésumé des tests:")
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Erreurs: {len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")

    # Retournez le résultat pour une utilisation potentielle dans un pipeline CI/CD
    return result.wasSuccessful()

if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Une erreur inattendue s'est produite lors de l'exécution des tests: {e}")
        traceback.print_exc()
        sys.exit(1)