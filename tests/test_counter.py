import os
import unittest
import tempfile
import json
from counttokens import TokenCounter

class TestTokenCounter(unittest.TestCase):
    def setUp(self):
        self.counter = TokenCounter(model="gpt-3.5-turbo")
        
        # Create temporary test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a text file
        self.text_file = os.path.join(self.temp_dir.name, "test.txt")
        with open(self.text_file, "w") as f:
            f.write("This is a test file for counting tokens.")
            
        # Create a JSON file
        self.json_file = os.path.join(self.temp_dir.name, "test.json")
        with open(self.json_file, "w") as f:
            json.dump({"key": "value", "test": "data"}, f)
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_count_tokens_from_string(self):
        """Test counting tokens in a simple string."""
        text = "Hello, world! This is a test."
        tokens = self.counter.count_tokens(text)
        self.assertGreater(tokens, 0)
        
    def test_count_tokens_from_text_file(self):
        """Test counting tokens in a text file."""
        result = self.counter.count_file_tokens(self.text_file)
        self.assertIn('tokens', result)
        self.assertGreater(result['tokens'], 0)
        self.assertIn('characters', result)
        self.assertEqual(result['file'], self.text_file)
        
    def test_count_tokens_from_json_file(self):
        """Test counting tokens in a JSON file."""
        result = self.counter.count_file_tokens(self.json_file)
        self.assertIn('tokens', result)
        self.assertGreater(result['tokens'], 0)
        self.assertIn('entries', result)
        
    def test_count_directory_tokens(self):
        """Test counting tokens in a directory."""
        results = self.counter.count_directory_tokens(self.temp_dir.name)
        self.assertEqual(len(results), 2)  # Should find our two test files
        
        # Calculate total tokens
        total_tokens = sum(r.get('tokens', 0) for r in results if 'tokens' in r)
        self.assertGreater(total_tokens, 0)


if __name__ == "__main__":
    unittest.main()