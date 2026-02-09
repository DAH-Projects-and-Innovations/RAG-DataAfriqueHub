import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Mock openai module before importing anything that uses it
sys.modules['openai'] = MagicMock()
# Mock llama_cpp module/class if needed, but we patch it in tests

# Add the backend directory to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.models import Document
from src.llm.openai_llm import OpenAILLM
from src.llm.ollama_llm import LocalLLM

class TestLLMImplementations(unittest.TestCase):
    
    def test_openai_llm_init(self):
        llm = OpenAILLM(api_key="fake-key")
        self.assertIsNotNone(llm.client)
        self.assertEqual(llm.model_name, "gpt-4o-mini")

    @patch('src.llm.openai_llm.openai.OpenAI')
    def test_openai_generate(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response

        llm = OpenAILLM(api_key="fake-key")
        response = llm.generate("Hello")
        
        self.assertEqual(response, "Test response")
        mock_client.chat.completions.create.assert_called_once()

    @patch('src.llm.openai_llm.openai.OpenAI')
    def test_openai_custom_prompt(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value = MagicMock()

        custom_sys = "Custom Sys Prompt"
        custom_user = "Custom User Template {query}"
        llm = OpenAILLM(api_key="fake-key", system_prompt=custom_sys, user_prompt_template=custom_user)
        
        llm.generate_with_context("MyQuery", [Document(content="doc")])
        
        # Check if custom prompts were passed
        call_args = mock_client.chat.completions.create.call_args[1]
        messages = call_args['messages']
        self.assertEqual(messages[0]['content'], custom_sys)
        self.assertIn("MyQuery", messages[1]['content'])

    @patch('src.llm.ollama_llm.LlamaCpp')
    @patch('os.path.exists')
    def test_local_llm_init(self, mock_exists, mock_llama_cpp):
        # Mock file existence
        mock_exists.return_value = True
        
        llm = LocalLLM(model_path="models/test.gguf")
        
        self.assertEqual(llm.model_path, "models/test.gguf")
        mock_llama_cpp.assert_called_once()
        self.assertIn("Je ne dispose pas", llm.default_system_prompt)

    @patch('src.llm.ollama_llm.LlamaCpp')
    @patch('os.path.exists')
    def test_local_generate(self, mock_exists, mock_llama_cpp):
        # Mock file existence
        mock_exists.return_value = True
        
        # Setup mock instance
        mock_instance = MagicMock()
        mock_llama_cpp.return_value = mock_instance
        mock_instance.invoke.return_value = "Local response"

        llm = LocalLLM(model_path="models/test.gguf")
        response = llm.generate("Hello")
        
        self.assertEqual(response, "Local response")
        mock_instance.invoke.assert_called_once()

if __name__ == '__main__':
    unittest.main()

