import unittest
import sys
import os
import logging
from datetime import datetime
import tempfile

# Ajoutez le répertoire racine du projet au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_manager import DatabaseManager
from tests.test_data_generator import generate_test_data

# Importez tous les modules de test
from tests.test_database import TestDatabaseManager
from tests.test_models import TestUser, TestWorkshop
from tests.test_ui import TestUI
from tests.test_utils import TestDateUtils, TestCSVExport
from tests.test_config import TestConfig
from tests.test_rgpd_manager import TestRGPDManager
from tests.test_workshop_history import TestWorkshopHistory
from tests.test_data_management import TestDataManagement
from tests.test_settings import TestSettings

def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f'test_results_{timestamp}.log')
    
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return log_file

def setup_test_database():
    # Créer une base de données temporaire pour les tests
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    
    # Initialiser la base de données
    db_manager = DatabaseManager(db_path)
    db_manager.initialize()
    
    # Générer les données de test
    generate_test_data(db_manager)
    
    return db_path, db_manager


def run_tests():
    log_file = setup_logging()
    
    # Configurer la base de données de test
    db_path, db_manager = setup_test_database()
    
    # Créez une suite de tests
    test_suite = unittest.TestSuite()
    test_loader = unittest.TestLoader()

    # Ajoutez toutes les classes de test à la suite
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestDatabaseManager))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestUser))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestWorkshop))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestUI))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestDateUtils))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestCSVExport))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestConfig))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestRGPDManager))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestWorkshopHistory))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestDataManagement))
    test_suite.addTest(test_loader.loadTestsFromTestCase(TestSettings))

    # Créez un runner de test
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)

    # Définir la variable d'environnement pour le chemin de la base de données
    os.environ['TEST_DB_PATH'] = db_path

    # Exécutez les tests
    result = runner.run(test_suite)

    # Enregistrez le résumé des tests dans le log
    logging.warning(f"Tests run: {result.testsRun}")
    logging.warning(f"Errors: {len(result.errors)}")
    logging.warning(f"Failures: {len(result.failures)}")
    
    if result.errors:
        logging.error("Errors:")
        for test, error in result.errors:
            logging.error(f"{test}: {error}")
    
    if result.failures:
        logging.error("Failures:")
        for test, failure in result.failures:
            logging.error(f"{test}: {failure}")

    # Nettoyage : supprimez la base de données temporaire
    os.unlink(db_path)

    # Retournez le résultat des tests
    print(f"Les résultats des tests ont été enregistrés dans : {log_file}")
    return result

if __name__ == '__main__':
    result = run_tests()
    
    # Sortez avec un code d'erreur si des tests ont échoué
    sys.exit(not result.wasSuccessful())
