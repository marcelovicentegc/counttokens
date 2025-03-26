import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock, call
import sys
import io
from counttokens import Ingest, Repository

class TestIngest(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for tests
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Setup paths for testing
        self.test_repo_path = os.path.join(self.temp_dir.name, "shoreline")
        os.makedirs(self.test_repo_path, exist_ok=True)
        
        # Create some mock files in the test repo
        os.makedirs(os.path.join(self.test_repo_path, "docs"), exist_ok=True)
        os.makedirs(os.path.join(self.test_repo_path, "docs", "examples"), exist_ok=True)
        
        # Create a test best practices file
        os.makedirs(os.path.join(self.test_repo_path, "content"), exist_ok=True)
        with open(os.path.join(self.test_repo_path, "content", "best-practices.mdx"), "w") as f:
            f.write("# Best Practices\n\nThis is a test best practices document.")
        
        # Create a test examples file
        with open(os.path.join(self.test_repo_path, "docs", "examples", "test.tsx"), "w") as f:
            f.write("// This is a test example file")

        # Change the paths in the ingest instance to use our test directories
        self.test_data_dir = os.path.join(self.temp_dir.name, "data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        
    def tearDown(self):
        self.temp_dir.cleanup()
    
    @patch("counttokens.ingest.ingest")
    def test_ingest_shoreline_best_practices(self, mock_ingest):
        """Test ingesting best practices from a repository using legacy method."""
        # Setup mock return values
        mock_ingest.return_value = ("Test Summary", "Test Tree", "Test Content")
        
        # Create ingest instance with test paths
        ingest_tool = Ingest()
        ingest_tool.clone_dir = self.temp_dir.name
        ingest_tool.data_dir = self.test_data_dir
        
        # Run the ingest method
        ingest_tool.ingest_shoreline_best_practices(self.test_repo_path)
        
        # Assert that ingest was called with correct parameters
        expected_output_path = os.path.join(self.test_data_dir, 'shoreline-best-practices', 'shoreline-best-practices.txt')
        mock_ingest.assert_called_once()

    @patch("counttokens.ingest.ingest")
    def test_ingest_shoreline_examples(self, mock_ingest):
        """Test ingesting examples from a repository using legacy method."""
        # Setup mock return values
        mock_ingest.return_value = ("Test Summary", "Test Tree", "Test Content")
        
        # Create ingest instance with test paths
        ingest_tool = Ingest()
        ingest_tool.clone_dir = self.temp_dir.name
        ingest_tool.data_dir = self.test_data_dir
        
        # Run the ingest method
        ingest_tool.ingest_shoreline_examples(self.test_repo_path)
        
        # Assert that ingest was called with correct parameters
        expected_output_path = os.path.join(self.test_data_dir, 'shoreline-examples', 'shoreline-examples.txt')
        mock_ingest.assert_called_once()
    
    @patch("counttokens.Ingest._select_repository")
    @patch("counttokens.Ingest._check_repository")
    @patch("counttokens.Ingest._display_ingest_options")
    @patch("counttokens.Ingest._ensure_output_dirs")
    @patch("counttokens.Ingest._ingest_data")
    @patch("builtins.input")
    def test_run_with_repository_selection(self, mock_input, mock_ingest_data, 
                                          mock_ensure_dirs, mock_display_options, 
                                          mock_check_repo, mock_select_repo):
        """Test running the ingest tool with the repository selection flow."""
        # Setup mocks
        mock_select_repo.return_value = True  # Repository selected successfully
        mock_check_repo.return_value = self.test_repo_path
        mock_input.return_value = "1"  # Select first option
        
        # Create ingest instance
        ingest_tool = Ingest()
        
        # Set selected repository after mocking selection
        ingest_tool.selected_repo = ingest_tool.repositories[1]  # Shoreline
        
        # Run the ingest tool
        ingest_tool.run()
        
        # Verify the method calls in the expected sequence
        mock_select_repo.assert_called_once()
        mock_check_repo.assert_called_once()
        mock_display_options.assert_called_once()
        mock_ensure_dirs.assert_called_once()
        mock_ingest_data.assert_called_once_with(self.test_repo_path, 1)
    
    @patch("builtins.input")
    def test_select_repository_success(self, mock_input):
        """Test successful repository selection."""
        mock_input.return_value = "1"  # Select Shoreline
        
        ingest_tool = Ingest()
        
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            result = ingest_tool._select_repository()
        
        self.assertTrue(result)
        self.assertEqual(ingest_tool.selected_repo, ingest_tool.repositories[1])
    
    @patch("builtins.input")
    def test_select_repository_exit(self, mock_input):
        """Test exiting from repository selection."""
        # Set input to exit option (3 for two repositories + exit)
        mock_input.return_value = "3" 
        
        ingest_tool = Ingest()
        
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            result = ingest_tool._select_repository()
        
        self.assertFalse(result)
        self.assertIsNone(ingest_tool.selected_repo)
    
    @patch("builtins.input")
    def test_display_ingest_options(self, mock_input):
        """Test displaying ingest options for a selected repository."""
        ingest_tool = Ingest()
        ingest_tool.selected_repo = ingest_tool.repositories[1]  # Shoreline
        
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            ingest_tool._display_ingest_options()
            output = fake_stdout.getvalue()
        
        self.assertIn("Best Practices", output)
        self.assertIn("Examples", output)
    
    @patch("counttokens.ingest.ingest")
    def test_ingest_data(self, mock_ingest):
        """Test ingesting data from a repository with specific option."""
        # Setup mock return values
        mock_ingest.return_value = ("Test Summary", "Test Tree", "Test Content")
        
        ingest_tool = Ingest()
        ingest_tool.data_dir = self.test_data_dir
        ingest_tool.selected_repo = ingest_tool.repositories[1]  # Shoreline
        
        # Run the ingest_data method
        with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
            ingest_tool._ingest_data(self.test_repo_path, 1)  # Best Practices
        
        # Assert that ingest was called with correct parameters
        mock_ingest.assert_called_once()
    
    def test_multiple_repositories_defined(self):
        """Test that multiple repositories are defined and available."""
        ingest_tool = Ingest()
        
        # Should have at least 2 repositories
        self.assertGreaterEqual(len(ingest_tool.repositories), 2)
        
        # Check that both Shoreline and FastStore repositories are defined
        self.assertIn(1, ingest_tool.repositories)
        self.assertIn(2, ingest_tool.repositories)
        
        # Check repository names
        self.assertEqual(ingest_tool.repositories[1].name, "shoreline")
        self.assertEqual(ingest_tool.repositories[2].name, "faststore")

if __name__ == "__main__":
    unittest.main()