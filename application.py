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
import platform
from language_model import LanguageModel

class Application:

    # Global Constants.

    # Constants: Application States.
    # - Application states are used to control application flow. 

    APPLICATION_STATE_IDLE    = 0   # Default application state. Usually used to initialise application state variables before giving them a value later. 
    APPLICATION_STATE_RUNNING = 1   # The application main loop is running.
    APPLICATION_STATE_STOPPED = 2   # The application main loop is stopped.

    # Constants: Application commands.
    # - Application commands control application state, or trigger actions.
    # - Note:
    #   - In a more sophisticated application we would define "events" that drive application state, in the form of a state machine. Where anything could 
    #     raise an event.
    #   - For the sake of simplicity, this reference application will just make use of simple user triggered commands to drive application state and actions. 

    APPLICATION_COMMAND_NONE           = 0
    APPLICATION_COMMAND_EXIT           = 1
    APPLICATION_COMMAND_CLEAR_TERMINAL = 2

    # Constants: User Prompt Commands. 
    # - When the user types any of the commands defined below, the text will be translated to application command constants (see below) to be executed by the
    #   command manager.

    PROMPT_COMMAND_NONE  = ''       # No command issued by the user. 
    PROMPT_COMMAND_EXIT  = 'exit'   # The user wants to exit the application.
    PROMPT_COMMAND_CLEAR = 'clear'  # The user wants to clear the application terminal. 

    # Constants: Terminal Commands. 
    # - Terminal commands that can be issued to the OS terminal.
    # - When I user enters a prompt command, the command interpreter will convert the prompt command to an application command.
    # - The command manager will execute the latest command. If the latest command is to issue a command to the terminal, then these constants will be used
    #   to execute actual command on the appropriate OS terminal. 

    TERMINAL_COMMAND_CLEAR_TERMINAL_WINDOWS = 'cls'
    TERMINAL_COMMAND_CLEAR_TERMINAL_LINUX   = 'clear'

    # Constants: Terminal Management.
    # - Terminal formatting and rendering.

    TERMINAL_PROMPT_AGENT_NAMETAG = '<agent_name>'                              # Markdown tag to be replaced with actual agent name.
    TERMINAL_PROMPT_FORMAT        = '[' + TERMINAL_PROMPT_AGENT_NAMETAG + ']'   # Terminal prompt format, e.g. "[USer]".
    TERMINAL_ERROR                = '[Error]'
    TERMINAL_SYSTEM               = '[SYSTEM]'
    TERMINAL_BULLET               = '- '

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Constructor.
    #---------------------------------------------------------------------------------------------------------------------------------------------------------

    def __init__ ( self ):

        # Initialise application.

        self.name            = 'Conversation Agent Reference Application'
        self.version         = 2.0
        self.agent_name_user = 'User'
        self.agent_name_ai   = 'AI'        
        self.command         = self.APPLICATION_COMMAND_NONE
        self.state           = self.APPLICATION_STATE_IDLE

        # Initialise model.

        self.model = LanguageModel ()

    #---------------------------------------------------------------------------------------------------------------------------------------------------------
    # Starts an instance of the application class.    
    #
    # Function name:
    # - run
    #
    # Description:
    # - This is the main public function that consumers of the class call to execute the application.
    #
    # Parameters:
    # - None
    #
    # Return Values:
    # - None.
    #
    # Preconditions:
    # - Application classes must be initialized.
    #
    # Postconditions:
    # - Main application has been executed, and has exited.
    #
    # To-Do:
    # 1. Improve error handling within the loop.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def run ( self ):

        self.print_application_info ()
        self.main_loop ()

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Main loop of the application handling user input and querying the language model.
    #
    # Function name:
    # - main_loop
    #
    # Description:
    # - This function runs the main loop of the application.
    # - It handles user input, queries the language model, and executes application commands.
    #
    # Parameters:
    # - None
    #
    # Return Values:
    # - None.
    #
    # Preconditions:
    # - Application and model classes must be initialized.
    #
    # Postconditions:
    # - User input is processed and language model responses are generated and rendered.
    #
    # To-Do:
    # 1. Improve error handling within the loop.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def main_loop ( self ):
        
        # Initialise main loop.  

        self.command = self.APPLICATION_COMMAND_NONE
        self.state   = self.APPLICATION_STATE_RUNNING    

        # Execute the main loop.

        while self.state == self.APPLICATION_STATE_RUNNING:
    
            # Get user input prompt.
            # 1. Get the user's input prompt from the terminal.
            # 2. Identify and initialize any application commands the user may have issued.
            # 3. Save the user's prompt to the conversation history.

            user_input   = self.get_user_prompt ()
            self.command = self.get_application_command ( user_input )                
            
            # Query language model and update conversation history.
            # 1. Append user input to conversation history. We add the user input to teh conversation history here, so that it doesn't get added in the case of a 
            #    command like `exit` for example, where we would not want the conversation history added when it is being written to the chat log later. 
            # 2. Query language model. We will return the response object, not the text. The renderer will decide whether to extract response text or use the 
            #    object based on whether `model_streaming_enabled` is True or not.
            # 3. Render model response. `model_streaming_enabled` is True then we will render streaming output from the model, otherwise we will just render
            #    the complete response text from the model. 
            # 4. Append language model response to conversation history.

            if self.command == self.APPLICATION_COMMAND_NONE:

                self.model.add_message_to_conversation_history ( user_input, self.model.MODEL_MESSAGE_ROLE_USER )
                model_response      = self.model.query_language_model ()
                model_response_text = self.render_language_model_response ( model_response )
                self.model.add_message_to_conversation_history ( model_response_text, self.model.MODEL_MESSAGE_ROLE_AI )                

            # Execute application command.            

            self.execute_application_command ()

        # Shut down program.

        self.model.save_chat_log_to_file ( include_system_prompt_enabled = False )

    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Retrieve the user prompt from the terminal.
    #
    # Function name:
    # - get_user_prompt
    #
    # Description:
    # - This function retrieves the user's input prompt from the terminal.
    # - It compiles the terminal prompt using the user's agent name and returns the prompt.
    #
    # Parameters:
    # - None
    #
    # Return Values:
    # - user_prompt : str : The user's input prompt.
    #
    # Preconditions:
    # - The application class must be initialized.
    #
    # Postconditions:
    # - The user's input prompt is retrieved and returned.
    #
    # To-Do:
    # 1. Add input validation for user prompt.
    # 2. Handle edge cases for empty or invalid inputs.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_user_prompt ( self ):

        # Compile terminal prompt, get prompt text from the user, and return the prompt to the caller.

        terminal_prompt_user = f'[{self.agent_name_user}]'
        user_prompt          = input ( f'\n{terminal_prompt_user}\n' )

        return user_prompt
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Convert the user prompt to an application command.
    #
    # Function name:
    # - get_application_command
    #
    # Description:
    # - This function converts the user's input prompt to an application command.
    # - It normalizes the user prompt to lowercase and identifies any application commands to execute.
    #
    # Parameters:
    # - user_prompt : str : The user's input prompt.
    #
    # Return Values:
    # - application_command : int : The application command constant.
    #
    # Preconditions:
    # - The user prompt must be a string.
    #
    # Postconditions:
    # - The appropriate application command is identified and returned.
    #
    # To-Do:
    # 1. Add more user prompt commands.
    # 2. Improve error handling for unrecognized commands.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def get_application_command ( self, user_prompt ):

        # Initialize local variables. 

        application_command = self.APPLICATION_COMMAND_NONE
        user_prompt         = user_prompt.lower()       # Normalize user prompt to lower case. 

        # Identify any application commands the user intends to execute.    

        if user_prompt == self.PROMPT_COMMAND_EXIT:
            application_command = self.APPLICATION_COMMAND_EXIT

        elif user_prompt == self.PROMPT_COMMAND_CLEAR:
            application_command = self.APPLICATION_COMMAND_CLEAR_TERMINAL

        else:
            application_command = self.APPLICATION_COMMAND_NONE

        # Return selected command to the caller. 

        return application_command
    
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Execute the application command.
    #
    # Function name:
    # - execute_application_command
    #
    # Description:
    # - This function executes the identified application command.
    # - It handles commands like exiting the application or clearing the terminal.
    #
    # Parameters:
    # - None
    #
    # Return Values:
    # - None.
    #
    # Preconditions:
    # - The application class must be initialized.
    # - A valid application command must be set.
    #
    # Postconditions:
    # - The application command is executed and the application state is updated.
    #
    # To-Do:
    # 1. Add more application commands and their handling.
    # 2. Improve error handling for command execution.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def execute_application_command ( self ):

        # No Command.

        if self.command == self.APPLICATION_COMMAND_NONE:
            pass

        # Exit application.

        if self.command == self.APPLICATION_COMMAND_EXIT:        
            self.state = self.APPLICATION_STATE_STOPPED

        # Clear the application terminal.

        if self.command == self.APPLICATION_COMMAND_CLEAR_TERMINAL:
            if platform.system () == "Windows":
                os.system ( self.TERMINAL_COMMAND_CLEAR_TERMINAL_WINDOWS )
            else:
                os.system ( self.TERMINAL_COMMAND_CLEAR_TERMINAL_LINUX )

        # Reset command to no command. 

        self.command = self.APPLICATION_COMMAND_NONE
        
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Render the language model's response.
    #
    # Function name:
    # - render_language_model_response
    #
    # Description:
    # - This function renders the language model's response, handling both streaming and non-streaming outputs.
    #
    # Parameters:    
    # - model_response : object : The response object from the language model.
    #
    # Return Values:
    # - response_text : str : The text of the language model's response.
    #
    # Preconditions:
    # - The application and model classes must be initialized.
    # - The model_response must be a valid response object.
    #
    # Postconditions:
    # - The language model's response is rendered and the response text is returned.
    #
    # To-Do:
    # 1. Improve handling of different response formats.
    # 2. Add error handling for rendering issues.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def render_language_model_response ( self, model_response ):

        try:

            # Initialise local variables. 

            terminal_prompt_ai = f'[{self.agent_name_ai}]'  # Compile terminal prompt.
            response_text      = ''                         # Initialise to empty string. We'll populate after handing streaming or non-streaming responses.
            
            # Print response. 

            print ( f'\n{terminal_prompt_ai}')

            # Render model response. 

            if self.model.streaming_enabled:

                # Output chunk by chunk as the response is streamed. 

                response_stream = { 'role' : 'assistant', 'content' : '' }
            
                for chunk in model_response:
                    if chunk.choices [ 0 ].delta.content:
                        print ( chunk.choices [ 0 ].delta.content, end = '', flush = True )
                        response_stream [ 'content' ] += chunk.choices [ 0 ].delta.content
                print ()

                # For a streamed response, get the response text from the completed response stream.

                response_text = response_stream [ 'content' ]
                
            else:

                # For a non-streamed response, get the response text from the response object, and write to the terminal. 

                response_text = model_response.choices [ 0 ].message.content
                print ( f"{response_text}" )

            # Return language model response text. 

            return response_text
        
        except Exception as e:

            error_message = f'\n{[self.TERMINAL_ERROR]} {str(e)}\n'

            print ( error_message )

            return error_message
       
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Display application and model information.
    #
    # Function name:
    # - print_application_info
    #
    # Description:
    # - This function prints the application's and model's information to the console.
    #
    # Parameters:
    # - None
    #
    # Return Values:
    # - None.
    #
    # Preconditions:
    # - The application and model classes must be initialized.
    #
    # Postconditions:
    # - The application's and model's information is printed to the console.
    #
    # To-Do:
    # - None.
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------

    def print_application_info ( self ):

        # Print application and model information to the console. 
        
        print ( f'\nApplication:' )
        print ( f'{self.TERMINAL_BULLET}Name:    {self.name}' )
        print ( f'{self.TERMINAL_BULLET}Version: {self.version}' )
        print ( f'\nModel:' )
        print ( f'{self.TERMINAL_BULLET}Name:              {self.model.name}' )
        print ( f'{self.TERMINAL_BULLET}Max Tokens:        {self.model.max_tokens}' )
        print ( f'{self.TERMINAL_BULLET}Temperature:       {self.model.temperature}' )
        print ( f'{self.TERMINAL_BULLET}Streaming Enabled: {self.model.streaming_enabled}' )

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
