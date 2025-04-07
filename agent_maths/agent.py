from google.adk.agents import Agent
from google.genai import types

MODEL = "gemini-2.0-flash-001"

def add(numbers: list[int]) -> int:
  """Calculates the sum of a list of integers.

    This function takes a list of integers as input and returns the sum of all
    the elements in the list.  It uses the built-in `sum()` function for
    efficiency.

    Args:
        numbers: A list of integers to be added.

    Returns:
        The sum of the integers in the input list.  Returns 0 if the input
        list is empty.

    Examples:
        add([1, 2, 3]) == 6
        add([-1, 0, 1]) == 0
        add([]) == 0
    """
  return sum(numbers)

def subtract(numbers: list[int]) -> int:
    """Subtracts numbers in a list sequentially from left to right.

    This function performs subtraction on a list of integers, applying the
    subtraction operation from left to right.  For example, given the list
    [10, 2, 5], the function will calculate 10 - 2 - 5.

    Args:
        numbers: A list of integers to be subtracted.

    Returns:
        The result of the sequential subtraction as an integer. Returns 0 if the input list is empty.

    Examples:
        subtract([10, 2, 5]) == 3  # (10 - 2) - 5 = 8 - 5 = 3
        subtract([10, 2]) == 8      # 10 - 2 = 8
        subtract([]) == 0
    """
    if not numbers:
        return 0  # Handle empty list
    result = numbers[0]
    for num in numbers[1:]:
        result -= num
    return result

def multiply(numbers: list[int]) -> int:
  """Calculates the product of a list of integers.

    This function takes a list of integers as input and returns the product of all
    the elements in the list. It iterates through the list, multiplying each
    number with the accumulated product.

    Args:
        numbers: A list of integers to be multiplied.

    Returns:
        The product of the integers in the input list. Returns 1 if the input
        list is empty.

    Examples:
        multiply([2, 3, 4]) == 24  # 2 * 3 * 4 = 24
        multiply([1, -2, 5]) == -10 # 1 * -2 * 5 = -10
        multiply([]) == 1
    """
  product = 1
  for num in numbers:
    product *= num
  return product

def divide(numbers: list[int]) -> float:  # Use float for division
    """Divides numbers in a list sequentially from left to right.

    This function performs division on a list of integers, applying the division
    operation from left to right.  For example, given the list [10, 2, 5], the
    function will calculate 10 / 2 / 5.

    Args:
        numbers: A list of integers to be divided.

    Returns:
        The result of the sequential division as a float.

    Raises:
        ZeroDivisionError: If any number in the list *after* the first element
                           is zero, a ZeroDivisionError is raised.  Division by
                           zero is not permitted.

    Returns:
        float: The result of the division. Returns 0.0 if the input list is empty.

    Examples:
        divide([10, 2, 5]) == 1.0  # (10 / 2) / 5 = 5 / 5 = 1.0
        divide([10, 2]) == 5.0      # 10 / 2 = 5.0
        divide([10, 0, 5])  # Raises ZeroDivisionError
        divide([]) == 0.0
    """
    if not numbers:
        return 0.0 # Handle empty list
    if 0 in numbers[1:]: # Check for division by zero
        raise ZeroDivisionError("Cannot divide by zero.")
    result = numbers[0]
    for num in numbers[1:]:
        result /= num
    return result

#print("Model:" + MODEL)
agent_math = Agent(
    model=MODEL,
    name="agent_math",
    description="This agent performs basic arithmetic operations (addition, subtraction, multiplication, and division) on user-provided numbers, including ranges.",
    instruction="""
      I can perform addition, subtraction, multiplication, and division operations on numbers you provide. 
      Tell me the numbers you want to operate on. 
      For example, you can say 'add 3 5', 'multiply 2, 4 and 3', 'Subtract 10 from 20', 'Divide 10 by 2'.
      You can also provide a range: 'Multiply the numbers between 1 and 10'.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0.2),
    tools=[add, subtract, multiply, divide],
)