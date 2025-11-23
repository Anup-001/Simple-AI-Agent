import os
from langchain_core.messages import HumanMessage 
from langchain_openai import ChatOpenAI
from langchain.tools import tool 
from langgraph.prebuilt import create_react_agent 
from dotenv import load_dotenv

load_dotenv()

@tool
def calculator(a:float, b:float, operation: str) -> str:
    """
    Perform basic arithmetic operations (addition, subtraction, multiplication, division).
    :param a: The first operand (number)
    :param b: The second operand (number)
    :param operation: The operation to perform ('add', 'subtract', 'multiply', 'divide')
    :return: A string with the result of the operation.
    """
    if operation == "add":
        return f"The sum of {a} and {b} is {a + b}."
    elif operation == "subtract":
        return f"The difference between {a} and {b} is {a - b}."
    elif operation == "multiply":
        return f"The product of {a} and {b} is {a * b}."
    elif operation == "divide":
        if b == 0:
            return "Error: Cannot divide by zero."
        return f"The quotient of {a} divided by {b} is {a / b}."
    else:
        return "Error: Unsupported operation. Please use 'add', 'subtract', 'multiply', or 'divide'."

@tool 
def greet(name:str)->str:
    """Greets a person with the provided name."""
    return f"Hello, {name}! How can I assist you today?"

@tool
def weather(location: str) -> str:
    """Returns the current weather for a given location."""
    # This would call a weather API like OpenWeather or WeatherAPI
    # Example return:
    return f"The current weather in {location} is sunny with a temperature of 25°C."

@tool
def currency_converter(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts currency from one type to another (requires an external API)."""
    # Example logic (you'd call an API here to get the actual conversion rate)
    conversion_rate = 1.2  # Example fixed rate for conversion
    converted_amount = amount * conversion_rate
    return f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}."

def main():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        print("Error: OpenAI API key not found. Please set it in your .env file.")
        return

    model = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
    tools = [calculator, greet,weather, currency_converter] 
    agent_executor = create_react_agent(model,tools)
    print("Agent loaded")
    print("Welcome to the interactive chat! Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ").strip()
        if user_input=="quit":
            break 
        if any(op in user_input.lower() for op in ['add', 'subtract', 'multiply', 'divide']):
            parts = user_input.split()
            if len(parts) >= 3:
                try:
                    num1 = float(parts[1])
                    num2 = float(parts[3])
                    operation = parts[0].lower()  # 'add', 'subtract', 'multiply', 'divide'
                    print("\nAssistant: ", end="")
                    response = calculator(num1, num2, operation)
                    print(response)
                except ValueError:
                    print("\nAssistant: Could not process the numbers. Please enter valid numbers.")
            else:
                print("\nAssistant: Please provide a valid operation, e.g., 'add 5 and 3'.")
        else:
            print("\nAssistant: ", end="")
            for chunk in agent_executor.stream({ "messages": [HumanMessage(content=user_input)] }):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    for message in chunk["agent"]["messages"]:
                        print(message.content,end="") 
            print()


if __name__ == "__main__":
    main()
