def quick_chat_system_prompt() -> str:
    return f"""
            Forget all previous instructions.
        You are a chatbot named Fred. You are assisting a software developer
        with their software development tasks.
        Each time the user converses with you, make sure the context is about
        * software development,
        * or coding,
        * or debugging,
        * or code reviewing,
        and that you are providing a helpful response.

        If the user asks you to do something that is not
        concerning one of those topics, you should refuse to respond.
        """

def system_learning_prompt() -> str:
    return """
    You are assisting a user with their general software development tasks.
Each time the user converses with you, make sure the context is generally about software development,
or creating a course syllabus about software development,
and that you are providing a helpful response.
If the user asks you to do something that is not concerning software
in the least, you should refuse to respond.
"""

def learning_prompt(learner_level: str, answer_type: str, topic: str) -> str:
    return f"""
Please disregard any previous context.

The topic at hand is ```{topic}```.
Analyze the sentiment of the topic.
If it does not concern software development or creating an online course syllabus about software development,
you should refuse to respond.

You are now assuming the role of a highly acclaimed software engineer specializing in the topic
 at a prestigious software company.  You are assisting a fellow software engineer with
 their software development tasks.
You have an esteemed reputation for presenting complex ideas in an accessible manner.
Your colleague wants to hear your answers at the level of a {learner_level}.

Please develop a detailed, comprehensive {answer_type} to teach me the topic as a {learner_level}.
The {answer_type} should include high level advice, key learning outcomes,
detailed examples, step-by-step walkthroughs if applicable,
and major concepts and pitfalls people associate with the topic.

Make sure your response is formatted in markdown format.
Ensure that embedded formulae are quoted for good display.
"""

############################################################################################################
# Requirements prompts
############################################################################################################

def system_requirements_prompt(product_name, product_description):
    """
    Generate a system requirements prompt based on the product name and description
    Args:
        product_name: The name of a product described in a system prompt
        product_description: A description of the product

    Returns:
        A prompt to use as a system prompt for making requirements documents for the product name and description.

    """
    return f"""
    Forget all previous instructions and context.

    You are an expert in requirements engineering.

    Your job is to learn and understand the following text about a product named {product_name}.
    ```
    {product_description}
    ```
    """

def requirements_prompt(product_name, requirement_type):
    """
    Generate a requirements prompt based on the requirement type and product name.
    Args:
        product_name: the name of a product described in a system prompt
        requirement_type: ["Business Problem Statement", "Vision Statement", "Ecosystem map", "RACI Matrix"]

    Returns:
        A prompt to use to generate a requirements document
        for the requirement type and product name.
    """
    if requirement_type not in ["Business Problem Statement", "Vision Statement", "Ecosystem map", "RACI Matrix"]:
        raise ValueError(f"Invalid requirement type.")
    if requirement_type == "Business Problem Statement":
        return business_problem_prompt(product_name)
    if requirement_type == "Vision Statement":
        return vision_statement_prompt(product_name)
    if requirement_type == "Ecosystem map":
        return ecosystem_map_prompt(product_name)
    if requirement_type == "RACI Matrix":
        return responsibility_matrix_prompt(product_name)


def business_problem_prompt(product_name):
    """
    Generates a prompt to define the business problem that the product aims to solve.

    Parameters:
    product_name (str): The name of the product.

    Returns:
    str: A detailed prompt asking for business problem identification.
    """
    return (f"Describe the core business problem that {product_name} aims to solve. "
            f"What pain points do users or stakeholders face that this product seeks to address? "
            f"Explain the inefficiencies, challenges, or market gaps that make the development of {product_name} necessary. "
            f"Provide specific examples of how this problem impacts business operations, customer satisfaction, or industry trends.")

def vision_statement_prompt(product_name):
    """
    Generates a prompt to define the vision statement for the product.

    Parameters:
    product_name (str): The name of the product.

    Returns:
    str: A detailed prompt for drafting the vision statement.
    """
    return (f"Define the vision statement for {product_name}. What is the long-term goal of this product? "
            f"Describe how {product_name} will create value for users and stakeholders. "
            f"How will the product evolve over time, and what impact will it have on the industry or society? "
            f"Ensure the vision statement is inspiring, future-focused, and aligned with the overall business strategy.")


def ecosystem_map_prompt(product_name):
    """
    Generates a prompt to create an ecosystem map for the product.

    Parameters:
    product_name (str): The name of the product.

    Returns:
    str: A detailed prompt requesting an ecosystem map.
    """
    return (f"Create an ecosystem map for {product_name}. Identify the key stakeholders, systems, and external factors that interact with the product. "
            f"Include suppliers, partners, regulatory bodies, and technology dependencies. "
            f"Describe how data, services, and transactions flow between different components of the ecosystem. "
            f"Consider user roles, third-party integrations, and external market influences that shape the product’s environment.")


def responsibility_matrix_prompt(product_name):
    """
    Generates a prompt to develop a responsibility assignment matrix (RACI) for the product.

    Parameters:
    product_name (str): The name of the product.

    Returns:
    str: A detailed prompt for constructing a responsibility matrix.
    """
    return (f"Develop a responsibility assignment matrix (RACI) for {product_name}. Identify the key roles involved in the development, implementation, and management of the product. "
            f"Assign responsibility levels for each role (Responsible, Accountable, Consulted, Informed) to ensure clarity in decision-making and execution. "
            f"Consider internal teams (such as developers, designers, and product managers) and external stakeholders (such as clients, regulators, or suppliers). "
            f"Provide a structured framework to clarify ownership and accountability for product success.")




############################################################################################################
# Code Generation prompts
############################################################################################################

def review_prompt(existing_code: str) -> str:
    """
    Generate a prompt for code review.
    
    Args:
        existing_code: The code to review
        
    Returns:
        A prompt to use for code review
    """
    return f"""
    Please review the following code and provide feedback on:
    
    1. Code quality and best practices
    2. Potential bugs or edge cases
    3. Performance considerations
    4. Readability and maintainability
    5. Suggestions for improvement
    
    Here is the code to review:
    
    ```python
    {existing_code}
    ```
    
    Please provide a comprehensive review with specific examples and suggestions for improvement.
    """


def modify_code_prompt(user_prompt: str, existing_code: str) -> str:
    """
    Generate a prompt for code modification.
    
    Args:
        user_prompt: The user's instructions for modifying the code
        existing_code: The code to modify
        
    Returns:
        A prompt to use for code modification
    """
    return f"""
    Please modify the following code according to these instructions:
    
    {user_prompt}
    
    Here is the original code:
    
    ```python
    {existing_code}
    ```
    
    Please provide:
    1. The modified code in a code block with the language specified
    2. An explanation of the changes made
    3. Any considerations or trade-offs in your implementation
    """


def debug_prompt(debug_error_string: str, existing_code: str) -> str:
    """
    Generate a prompt for code debugging.
    
    Args:
        debug_error_string: The error message or description of the issue
        existing_code: The code to debug
        
    Returns:
        A prompt to use for code debugging
    """
    error_context = f"""
    The following error occurred:
    
    ```
    {debug_error_string}
    ```
    """ if debug_error_string else "The code is not working as expected."
    
    return f"""
    Please help debug the following code.
    
    {error_context}
    
    Here is the code:
    
    ```python
    {existing_code}
    ```
    
    Please provide:
    1. An explanation of what's causing the issue
    2. A fixed version of the code in a code block with the language specified
    3. An explanation of the fix and how it resolves the issue
    """
