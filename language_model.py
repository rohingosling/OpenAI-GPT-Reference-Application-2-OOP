#---------------------------------------------------------------------------------------------------------------------------------------------------------
# Application   Conversation Agent Reference Application
# Version:      2.0
# Release Date: 2024-04-06
# Author:       Rohin Gosling
#
# Description:
#
# - General-purpose conversation agent reference application, that can be used as the starting point for an OpenAI API-style chatbot.
#
# - main_loop:
#
#   - 1. Get user input prompt. 
#   - 2.     Get application command from user input prompt. 
#   - 3.     Append user input prompt to conversation history.
#   - 4. Query language model using user input prompt.
#   - 5.     Render language model response.
#   - 6.     Append language model response to conversation history.
#   - 7. Execute application command. 
#

# Features:
#
# - Turn-based conversation agent, with conversation history.
# - Autosave conversation history to a text file.
# 
# Dependencies:
# 
# - OpenAI Library:
#
#   pip install --upgrade openai 
#
# Usage Notes:
#
# - The variable `model_client` is initialized to an instance of `OpenAI`.
#   - OpenAI.api_key is set using the environment variable `OPENAI_API_KEY`.
#   - You will need to set `OPENAI_API_KEY` to hold your OpenAI API key. 
#   - Or replace `api_key = os.environ [ 'OPENAI_API_KEY' ]` with `api_key = <Your OpenAI API key>`.
#
# - On first use run the following batch files in order.
#   1. `venv_create.bat` to create the Python virtual environment.
#   2. 'venv_install_requirements.bat` to install dependent packages. 
#
# - For general use, run the following batch files before use. 
#   1. `venv_activate.bat` to activate the Python virtual environment.
#
# - To-Do:
#   5. Restructure system prompt initialization, so that initialization of the system prompt takes place in the initialization function.
#   6. Add feedback in both the console and chat log files, to show the system prompt file name. Or whether the default system prompt was used.  
#   7. Add a test command to show the system prompt.
#   8. Decide where is the most logical place to put the conversation log file. In the application class, or the LLM model class.
#
#---------------------------------------------------------------------------------------------------------------------------------------------------------

import os
from openai  import OpenAI

from utility import load_text_to_string

class LanguageModel:

    # Constants: Language Model Meta Parameters.

    MODEL_NAME_GPT_3_5_TURBO      = 'gpt-3.5-turbo'
    MODEL_NAME_GPT_4              = 'gpt-4'
    MODEL_NAME_GPT_4O             = 'gpt-4o'
    MODEL_MESSAGE_ROLE_SYSTEM     = 'system'
    MODEL_MESSAGE_ROLE_USER       = 'user'
    MODEL_MESSAGE_ROLE_AI         = 'assistant'
    MODEL_SYSTEM_PROMPT_FILE_NAME = 'data/system_prompt.txt'
    MODEL_SYSTEM_PROMPT_DEFAULT   = 'You are a general purpose AI assistant. You always provide well-reasoned answers that are both correct and helpful.'

    # Constants: Terminal Management.
    # - Terminal formatting and rendering.
    
    TERMINAL_ERROR  = '[Error]'
    TERMINAL_SYSTEM = '[SYSTEM]'
    TERMINAL_BULLET = '- '

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Constructor.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__ ( self ):

        # Initialise language model.

        self.client               = OpenAI ( api_key = os.environ [ 'OPENAI_API_KEY' ] )
        self.name                 = self.MODEL_NAME_GPT_4O
        self.max_tokens           = 1024
        self.temperature          = 0.7
        self.streaming_enabled    = True
        self.conversation_history = []

        # Initialise chat-log file. 

        self.chat_log_folder         = 'chat_log'
        self.chat_log_file_name      = 'chat_log_'
        self.chat_log_file_extension = '.txt'

        # Add system prompt to conversation history.
        # - If a system prompt can not be loaded from the file, then just use the default system prompt. 

        model_system_prompt = load_text_to_string ( self.MODEL_SYSTEM_PROMPT_FILE_NAME )

        if model_system_prompt == '':
            model_system_prompt = self.MODEL_SYSTEM_PROMPT_DEFAULT

        self.add_message_to_conversation_history ( model_system_prompt, self.MODEL_MESSAGE_ROLE_SYSTEM )

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Add a message to the conversation history.
    #
    # Function name:
    # - add_message_to_conversation_history
    #
    # Description:
    # - This function appends a message to the model's conversation history.
    #
    # Parameters:    
    # - message      : str : The message to be added to the conversation history.
    # - message_role : str : The role of the message sender (e.g., user, assistant, system).
    #
    # Return Values:
    # - None.
    #
    # Preconditions:    
    # - The message must be a string.
    # - The message_role must be a valid role string.
    #
    # Postconditions:
    # - The message is appended to the conversation history.
    #
    # To-Do:
    # 1. Validate message and message_role before appending.
    # 2. Add error handling for invalid inputs.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def add_message_to_conversation_history ( self, message, message_role ):
        
        self.conversation_history.append ( { 'role': message_role, 'content': message } )

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Query the language model with the conversation history.
    #
    # Function name:
    # - query_language_model
    #
    # Description:
    # - This function queries the language model using the provided conversation history.
    # - It handles both streaming and non-streaming responses.
    #
    # Parameters:
    # - None
    #
    # Return Values:
    # - response : object : The response object from the language model.
    #
    # Preconditions:
    # - The model class must be initialized.
    # - The conversation history must be set.
    #
    # Postconditions:
    # - The language model is queried and the response object is returned.
    #
    # To-Do:
    # 1. Add more detailed error handling for the API call.
    # 2. Log the query and response for debugging.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def query_language_model ( self ):
        
        try:

            # Query the language model. 

            response = self.client.chat.completions.create (
                model       = self.name,
                messages    = self.conversation_history,
                max_tokens  = self.max_tokens,
                temperature = self.temperature,
                stream      = self.streaming_enabled
            )

            # Return the response object. 
            # - We return the response object rather than the response text, so that the renderer can render streaming responses if `stream` is True.        
            # - If `stream` is False, the renderer will retrieve the response text with `response.choices [ 0 ].message.content`.

            return response
        
        except Exception as e:

            error_message = f'\n{[self.TERMINAL_ERROR]} {str(e)}\n'

            print ( error_message )

            return error_message

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Save the chat log to a file.
    #
    # Function name:
    # - save_chat_log_to_file
    #
    # Description:
    # - This function saves the conversation history to a log file.
    # - It ensures the log folder exists, determines the next available file name, and writes the conversation history to the file.
    #
    # Parameters:
    # - application                   : dict : Dictionary containing the application's state.
    # - model                         : dict : Dictionary containing the model configuration settings.
    # - include_system_prompt_enabled : bool : Boolean flag to control whether we will include the system prompt or not.
    #                                   Default value is False, i.e. Do not include system prompt. 
    #
    # Return Values:
    # - None.
    #
    # Preconditions:
    # - The application and model dictionaries must be initialized.
    # - The conversation history must be set.
    #
    # Postconditions:
    # - The conversation history is saved to a log file.
    #
    # To-Do:
    # 1. Add error handling for file operations.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def save_chat_log_to_file ( self, include_system_prompt_enabled = False ):
        
        # Ensure the folder exists; if not, create it.

        if not os.path.exists ( self.chat_log_folder ):
            os.makedirs ( self.chat_log_folder )
        
        # Determine the next file number to use.

        file_index = 0

        while os.path.exists ( os.path.join ( self.chat_log_folder, f'{self.chat_log_file_name}{file_index}{self.chat_log_file_extension}' ) ):
            file_index += 1

        # Create the filename with the next index.

        file_name = os.path.join ( self.chat_log_folder, f'{self.chat_log_file_name}{file_index}{self.chat_log_file_extension}' )

        # Write the conversation history to the file.

        with open ( file_name, 'w', encoding = 'utf-8' ) as file:

            # Write chat log header information.

            file.write ( f'\nModel:\n' )
            file.write ( f'{self.TERMINAL_BULLET}Name:              {self.name}\n' )
            file.write ( f'{self.TERMINAL_BULLET}Max Tokens:        {self.max_tokens}\n' )
            file.write ( f'{self.TERMINAL_BULLET}Temperature:       {self.temperature}\n' )
            file.write ( f'{self.TERMINAL_BULLET}Streaming Enabled: {self.streaming_enabled}\n' )
            file.write ( '\n' )

            # Write chat log history to file. 
            
            row_index = 0

            for row in self.conversation_history:
                if row_index > 0:
                    file.write ( f'[{row [ "role" ]}]\n{row [ "content" ]}\n\n' )
                elif row_index == 0 and include_system_prompt_enabled:
                    file.write ( f'[{row [ "role" ]}]\n{row [ "content" ]}\n\n' )
                
                row_index += 1

        print ( f'\n{self.TERMINAL_SYSTEM}\nConversation history saved to "{file_name}."' ) 

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Function tagline. Short one-sentence or phrase description of function. e .g. Execute this or that. 
    #
    # Function name:
    # - function_name
    #
    # Description:
    # - bla bla bla.
    # - bla bla bla.
    #
    # Parameters:
    # - parameter_x : Description of value_x.
    # - parameter_y : Description of value_y.
    # - parameter_z : Description of value_z.
    #
    # Return Values:
    # - Description of return value. Or `none` if there is no return value. 
    #
    # Preconditions:
    # - Description of precondition 1
    # - Description of precondition 2
    # - Description of precondition 3
    #
    # Postconditions:
    # - Description of postcondition 1.
    # - Description of postcondition 2.
    # - Description of postcondition 3.
    #
    # To-Do:
    # 1. Improvement or enhancement 1.
    # 2. Improvement or enhancement 2.
    # 3. Improvement or enhancement 3.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

