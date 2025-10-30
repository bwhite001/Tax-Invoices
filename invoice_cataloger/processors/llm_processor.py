"""
LLM Processor for Invoice Data Extraction using LM Studio
"""
import json
import time
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException, Timeout


class LLMProcessor:
    """Process invoice text using LM Studio LLM"""
    
    def __init__(self, endpoint: str, model: str, temperature: float = 0.1,
                 max_tokens: int = 3000, timeout: int = 120, retry_attempts: int = 3,
                 retry_delay: int = 2):
        self.endpoint = endpoint
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
    
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
        prompt = f"""You are an invoice data extraction specialist. Extract invoice information from the text below and return ONLY valid JSON with no additional text or markdown.

TEXT TO EXTRACT FROM:
{invoice_text}

RETURN THIS JSON STRUCTURE (use empty string "" for missing fields, 0.00 for amounts):
{{
  "vendor_name": "",
  "vendor_abn": "",
  "invoice_number": "",
  "invoice_date": "",
  "due_date": "",
  "subtotal": 0.00,
  "tax": 0.00,
  "total": 0.00,
  "currency": "AUD",
  "description": "",
  "line_items": [{{"description": "", "quantity": 1, "unit_price": 0.00, "amount": 0.00}}]
}}

INSTRUCTIONS:
1. Extract vendor ABN if visible
2. Extract invoice number/ID
3. Extract invoice date and due date in YYYY-MM-DD format
4. Extract all monetary amounts
5. Extract line item descriptions and amounts
6. Return ONLY the JSON object, no explanation"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call LM Studio API"""
        # Combine system message with user prompt
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
    def test_connection(endpoint: str, models_endpoint: str) -> tuple[bool, str]:
        """
        Test connection to LM Studio
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            response = requests.get(models_endpoint, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                model_name = data['data'][0].get('id', 'unknown')
                return True, f"Connected. Loaded model: {model_name}"
            else:
                return False, "No model loaded in LM Studio"
                
        except RequestException as e:
            return False, f"Cannot connect to LM Studio: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
