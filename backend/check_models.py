"""Quick script to list available Gemini models."""
import google.generativeai as genai
from app.config import settings

# Configure API
genai.configure(api_key=settings.GEMINI_API_KEY)

print("Listing available Gemini models...\n")

try:
    models = genai.list_models()

    print("Available models that support generateContent:")
    print("-" * 80)

    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n[OK] {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Supported methods: {', '.join(model.supported_generation_methods)}")

    print("\n" + "=" * 80)
    print("\nAll available models:")
    print("-" * 80)
    for model in models:
        print(f"• {model.name} - {model.display_name}")

except Exception as e:
    print(f"[ERROR] Error listing models: {e}")
    print("\nTrying alternative approach...")

    # Try common model names
    test_models = [
        'gemini-1.5-pro',
        'gemini-1.5-flash',
        'gemini-1.5-pro-latest',
        'gemini-1.5-flash-latest',
        'gemini-pro',
        'gemini-pro-vision',
        'models/gemini-1.5-pro',
        'models/gemini-1.5-flash',
        'models/gemini-pro',
        'models/gemini-pro-vision',
    ]

    print("\nTesting common model names:")
    for model_name in test_models:
        try:
            model = genai.GenerativeModel(model_name)
            print(f"[OK] {model_name} - WORKS")
        except Exception as e:
            print(f"[FAIL] {model_name} - {str(e)[:100]}")
