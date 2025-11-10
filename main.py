"""
Main Program Entry
Provides interactive command-line interface
"""

import os
import sys
from typing import Optional
from react_agent import create_search_agent


def load_config():
    """Load configuration"""
    try:
        import config
        return config
    except ImportError:
        print("❌ config.py file not found")
        print("Please copy config.example.py to config.py and fill in your API keys")
        sys.exit(1)


def print_welcome():
    """Print welcome message"""
    print("=" * 60)
    print("🤖 Search-Augmented Agent")
    print("=" * 60)
    print("Features:")
    print("  ✓ ReAct framework for reasoning and acting")
    print("  ✓ Real-time web search capability")
    print("  ✓ Conversation memory")
    print("  ✓ Multiple search engine support")
    print()
    print("Commands:")
    print("  Enter question - Ask a question")
    print("  /clear       - Clear conversation history")
    print("  /memory      - View conversation history")
    print("  /help        - Show help")
    print("  /quit        - Exit program")
    print("=" * 60)
    print()


def print_help():
    """Print help information"""
    print("\n📖 Help:")
    print("  This is an AI assistant with search capabilities that can answer various questions.")
    print("  When the latest information is needed, it will automatically search the web.")
    print()
    print("  Example questions:")
    print("    - What's the weather today?")
    print("    - Where are the 2024 Olympics held?")
    print("    - What are the new features in Python 3.12?")
    print("    - What are the latest AI technology developments?")
    print()


def main():
    """Main function"""
    # Load configuration
    config = load_config()
    
    # Verify API key
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ Please set a valid OPENAI_API_KEY in config.py")
        sys.exit(1)
    
    # Print welcome message
    print_welcome()
    
    # Create agent
    print("🔧 Initializing agent...")
    try:
        agent = create_search_agent(
            openai_api_key=config.OPENAI_API_KEY,
            search_provider=config.SEARCH_PROVIDER,
            tavily_api_key=getattr(config, 'TAVILY_API_KEY', None),
            openai_base_url=getattr(config, 'OPENAI_BASE_URL', None),
            model_name=getattr(config, 'MODEL_NAME', 'gpt-3.5-turbo'),
            temperature=getattr(config, 'TEMPERATURE', 0.7),
            max_memory_length=getattr(config, 'MAX_MEMORY_LENGTH', 10),
            verbose=True
        )
        print("✅ Agent initialized successfully!")
        print()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = input("🧑 You: ").strip()
            
            if not user_input:
                continue
            
            # Process commands
            if user_input.startswith("/"):
                command = user_input.lower()
                
                if command == "/quit" or command == "/exit" or command == "/q":
                    print("\n👋 Goodbye!")
                    break
                
                elif command == "/clear":
                    agent.clear_memory()
                    print("✅ Conversation history cleared")
                    continue
                
                elif command == "/memory":
                    memory = agent.get_memory_summary()
                    print(f"\n📝 Conversation history:\n{memory}\n")
                    continue
                
                elif command == "/help" or command == "/h":
                    print_help()
                    continue
                
                else:
                    print(f"❌ Unknown command: {user_input}")
                    print("Enter /help to see available commands")
                    continue
            
            # Process query
            print("\n🤖 Assistant: ", end="", flush=True)
            response = agent.query(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()


if __name__ == "__main__":
    main()
