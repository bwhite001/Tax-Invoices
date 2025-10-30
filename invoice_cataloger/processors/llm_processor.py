"""
LLM Processor for Invoice Data Extraction
Supports: LM Studio, OpenAI, and OpenRouter
"""
import json
import time
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException, Timeout
from openai import OpenAI


class LLMProcessor:
    """Process invoice text using various LLM providers"""
    
    def __init__(self, api_provider: str = "lmstudio",
                 # LM Studio params
                 endpoint: str = None, model: str = None,
                 # OpenAI params
                 openai_api_key: str = None, openai_model: str = None, openai_api_base: str = None,
                 # OpenRouter params
                 openrouter_api_key: str = None, openrouter_model: str = None,
                 openrouter_api_base: str = None, openrouter_app_name: str = None,
                 # Custom prompt
                 use_custom_prompt: bool = False, custom_extraction_prompt: str = None,
                 # Common params
                 temperature: float = 0.1, max_tokens: int = 3000,
                 timeout: int = 120, retry_attempts: int = 3, retry_delay: int = 2):
        
        self.api_provider = api_provider.lower()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Custom prompt configuration
        self.use_custom_prompt = use_custom_prompt
        self.custom_extraction_prompt = custom_extraction_prompt
        
        # LM Studio configuration
        self.endpoint = endpoint
        self.model = model
        
        # OpenAI configuration
        self.openai_client = None
        if self.api_provider == "openai" and openai_api_key:
            self.openai_client = OpenAI(
                api_key=openai_api_key,
                base_url=openai_api_base,
                timeout=timeout
            )
            self.openai_model = openai_model
        
        # OpenRouter configuration
        self.openrouter_client = None
        if self.api_provider == "openrouter" and openrouter_api_key:
            self.openrouter_client = OpenAI(
                api_key=openrouter_api_key,
                base_url=openrouter_api_base,
                timeout=timeout,
                default_headers={
                    "HTTP-Referer": "https://github.com/yourusername/invoice-cataloger",
                    "X-Title": openrouter_app_name or "Invoice-Cataloger"
                }
            )
            self.openrouter_model = openrouter_model
    
    def extract_invoice_data(self, invoice_text: str, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured invoice data from text using LLM
        
        Args:
            invoice_text: Raw text extracted from invoice
            file_name: Name of the file being processed
        
        Returns:
            Dictionary with extracted invoice data or None if extraction fails
        """
        if not invoice_text or len(invoice_text.strip()) < 10:
            return None
        
        # Truncate very long texts
        if len(invoice_text) > 10000:
            invoice_text = invoice_text[:10000]
        
        prompt = self._build_extraction_prompt(invoice_text)
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = self._call_llm(prompt)
                
                if response:
                    # Parse and validate response
                    extracted_data = self._parse_response(response)
                    if extracted_data:
                        return extracted_data
                
            except Exception as e:
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return None
        
        return None
    
    def _build_extraction_prompt(self, invoice_text: str) -> str:
        """Build the extraction prompt for the LLM"""
        
        # Use custom prompt if configured
        if self.use_custom_prompt and self.custom_extraction_prompt:
            return self.custom_extraction_prompt.replace("{invoice_text}", invoice_text)
        
        # Default optimized prompt for invoice extraction
        prompt = f"""You are a professional invoice data extraction AI assistant specializing in Australian tax invoices. Your task is to extract structured information from invoice documents with high accuracy.

INVOICE TEXT TO ANALYZE:
---
{invoice_text}
---

EXTRACTION REQUIREMENTS:

Extract the following information and return ONLY a valid JSON object (no markdown, no explanations):

{{
  "vendor_name": "Full legal business name",
  "vendor_abn": "Australian Business Number (11 digits, format: XX XXX XXX XXX)",
  "invoice_number": "Invoice/Tax Invoice number or reference",
  "invoice_date": "Invoice date in YYYY-MM-DD format",
  "due_date": "Payment due date in YYYY-MM-DD format",
  "subtotal": 0.00,
  "tax": 0.00,
  "total": 0.00,
  "currency": "AUD",
  "description": "Brief description of goods/services",
  "line_items": [
    {{
      "description": "Item description",
      "quantity": 1,
      "unit_price": 0.00,
      "amount": 0.00
    }}
  ]
}}

EXTRACTION RULES:
1. **Vendor Name**: Extract the full legal business name (usually at the top of the invoice)
2. **ABN**: Look for "ABN:" followed by 11 digits. Format as XX XXX XXX XXX
3. **Invoice Number**: Look for "Invoice #", "Invoice No", "Tax Invoice", or similar labels
4. **Dates**: Convert all dates to YYYY-MM-DD format (e.g., "15 Jan 2024" → "2024-01-15")
5. **Amounts**: Extract as decimal numbers (e.g., 150.00, not "$150" or "150")
6. **GST/Tax**: Look for GST, Tax, or VAT line items
7. **Line Items**: Extract each product/service with quantity, unit price, and total
8. **Currency**: Default to "AUD" unless explicitly stated otherwise
9. **Missing Data**: Use empty string "" for text fields, 0.00 for numeric fields if not found

IMPORTANT:
- Return ONLY the JSON object
- Do NOT include markdown code blocks (no ```json```)
- Do NOT add explanations or comments
- Ensure all numeric values are numbers, not strings
- Ensure dates are in YYYY-MM-DD format
- If a field cannot be found, use the default empty/zero value

JSON OUTPUT:"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call the configured LLM API provider"""
        if self.api_provider == "openai":
            return self._call_openai(prompt)
        elif self.api_provider == "openrouter":
            return self._call_openrouter(prompt)
        elif self.api_provider == "lmstudio":
            return self._call_lmstudio(prompt)
        else:
            raise ValueError(f"Unsupported API provider: {self.api_provider}")
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API using official SDK"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional invoice data extraction assistant. Always respond with ONLY valid JSON, no markdown formatting, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            
            return None
            
        except Exception as e:
            raise
    
    def _call_openrouter(self, prompt: str) -> Optional[str]:
        """Call OpenRouter API using OpenAI-compatible SDK"""
        try:
            response = self.openrouter_client.chat.completions.create(
                model=self.openrouter_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional invoice data extraction assistant. Always respond with ONLY valid JSON, no markdown formatting, no explanations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            
            return None
            
        except Exception as e:
            raise
    
    def _call_lmstudio(self, prompt: str) -> Optional[str]:
        """Call LM Studio API (OpenAI-compatible endpoint)"""
        # Combine system message with user prompt for LM Studio
        full_prompt = "You are a JSON extraction assistant. Always respond with ONLY valid JSON, no markdown, no explanations.\n\n" + prompt
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('choices') and len(data['choices']) > 0:
                message = data['choices'][0].get('message', {})
                content = message.get('content', '')
                return content
            
            return None
            
        except (RequestException, Timeout) as e:
            raise
    
    def _parse_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse and validate LLM response"""
        try:
            # Clean up response - remove markdown code blocks if present
            response = response.strip()
            response = response.replace('```json', '').replace('```', '')
            response = response.strip()
            
            # Parse JSON
            data = json.loads(response)
            
            # Validate required fields
            required_fields = ['vendor_name', 'invoice_date', 'total']
            for field in required_fields:
                if field not in data:
                    data[field] = "" if field != 'total' else 0.00
            
            # Ensure numeric fields are floats
            numeric_fields = ['subtotal', 'tax', 'total']
            for field in numeric_fields:
                if field in data:
                    try:
                        data[field] = float(data[field]) if data[field] else 0.00
                    except (ValueError, TypeError):
                        data[field] = 0.00
            
            # Ensure line_items is a list
            if 'line_items' not in data or not isinstance(data['line_items'], list):
                data['line_items'] = []
            
            return data
            
        except json.JSONDecodeError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def test_connection(api_provider: str, **kwargs) -> tuple[bool, str]:
        """
        Test connection to the configured API provider
        
        Args:
            api_provider: "lmstudio", "openai", or "openrouter"
            **kwargs: Provider-specific parameters
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        provider = api_provider.lower()
        
        if provider == "lmstudio":
            endpoint = kwargs.get('endpoint')
            models_endpoint = kwargs.get('models_endpoint')
            
            try:
                response = requests.get(models_endpoint, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('data') and len(data['data']) > 0:
                    model_name = data['data'][0].get('id', 'unknown')
                    return True, f"LM Studio connected. Loaded model: {model_name}"
                else:
                    return False, "No model loaded in LM Studio"
                    
            except RequestException as e:
                return False, f"Cannot connect to LM Studio: {str(e)}"
            except Exception as e:
                return False, f"LM Studio error: {str(e)}"
        
        elif provider == "openai":
            api_key = kwargs.get('api_key')
            model = kwargs.get('model')
            api_base = kwargs.get('api_base')
            
            if not api_key:
                return False, "OpenAI API key not configured"
            
            try:
                client = OpenAI(api_key=api_key, base_url=api_base, timeout=5)
                # Test with a minimal request
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                return True, f"OpenAI connected. Using model: {model}"
            except Exception as e:
                return False, f"OpenAI connection failed: {str(e)}"
        
        elif provider == "openrouter":
            api_key = kwargs.get('api_key')
            model = kwargs.get('model')
            api_base = kwargs.get('api_base')
            app_name = kwargs.get('app_name', 'Invoice-Cataloger')
            
            if not api_key:
                return False, "OpenRouter API key not configured"
            
            try:
                client = OpenAI(
                    api_key=api_key,
                    base_url=api_base,
                    timeout=5,
                    default_headers={
                        "HTTP-Referer": "https://github.com/yourusername/invoice-cataloger",
                        "X-Title": app_name
                    }
                )
                # Test with a minimal request
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                return True, f"OpenRouter connected. Using model: {model}"
            except Exception as e:
                return False, f"OpenRouter connection failed: {str(e)}"
        
        else:
            return False, f"Unknown API provider: {api_provider}"
