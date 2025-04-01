# model_handler.py
import ollama
from typing import Generator
from dotenv import load_dotenv
import os
import re

load_dotenv()

class CancellationError(Exception):
    """Custom exception for generation cancellation"""

def validate_code_syntax(code: str, language: str) -> bool:
    """Enhanced syntax validation with improved pattern matching"""
    language = language.lower()
    language_patterns = {
        "python": r"(^def\s|^class\s|^async\s|^from\s|^import\s|^\@|->\s\w+:)",
        "javascript": r"(function\s|=>|import\s|export\s|const\s|let\s|class\s|console\.)",
        "java": r"(class\s+\w+|public\s+static|System\.out\.|interface\s+)",
        "c++": r"(#include\s|using\s+namespace|template\s*<|std::)",
        "rust": r"(fn\s+main|impl\s+|struct\s+|trait\s+|println!)",
        "go": r"(package\s+main|func\s+main|import\s+\()"
    }
    
    # Extract code block if present
    code_block = re.search(r"```(?:.*?)\n(.*?)```", code, re.DOTALL)
    if code_block:
        code = code_block.group(1)
    
    return bool(re.search(language_patterns.get(language, ""), code, re.MULTILINE))

def generate_code(
    prompt: str, 
    language: str, 
    temperature: float,
    cancellation_flag: list  # Added cancellation flag parameter
) -> Generator[str, None, None]:
    """Enhanced code generation with cancellation support"""
    system_prompt = f"""You are a {language} coding expert. Follow these rules:
1. Generate {os.getenv('CODE_STYLE', 'production')}-quality code
2. Include {', '.join(os.getenv('DOC_STYLE', 'comments').split(','))}
3. Use modern language features
4. Format output as markdown code blocks with language specification"""
    
    try:
        model_name = os.getenv('DEFAULT_MODEL')
        response = ollama.generate(
            model=model_name,
            system=system_prompt,
            prompt=f"{language} code for: {prompt}",
            stream=True,
            options={
                'temperature': max(0.1, min(temperature, 1.0)),
                'num_ctx': 4096,
                'stop': ['</end>', '<!-- END -->', '### END']
            }
        )
        
        code_buffer = ""
        in_code_block = False
        validated = False

        for chunk in response:
            # Check cancellation flag
            if cancellation_flag[0]:
                yield "\n## Generation stopped by user"
                raise CancellationError()
            
            chunk_text = chunk.get('response', '')
            
            # Handle code block boundaries
            if '```' in chunk_text:
                parts = chunk_text.split('```')
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        if part:
                            yield part
                    else:
                        if not in_code_block:
                            # Start code block
                            in_code_block = True
                            code_buffer = ""
                            yield f"\n```{language.lower()}\n"
                        else:
                            # End code block
                            in_code_block = False
                            code_buffer += part
                            if validate_code_syntax(code_buffer, language):
                                yield f"{code_buffer}\n```\n"
                            else:
                                yield "\n```⚠️ Potential syntax issues detected\n"
                            code_buffer = ""
                            validated = True
                continue
                
            if in_code_block:
                code_buffer += chunk_text
                if not validated:
                    yield chunk_text
            else:
                yield chunk_text

    except CancellationError:
        yield "\n## Operation cancelled by user"
    except Exception as e:
        yield f"\n## Generation error: {str(e)}"